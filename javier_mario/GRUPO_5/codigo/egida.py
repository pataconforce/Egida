#Proyecto integrador
#Maestría en Inteligencia Artificial
#Mario Sánchez y Javier Vega
#Égida versión 3

import cv2
import time
import pygame
import os
import threading
from datetime import datetime
from ultralytics import YOLO
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler

# BOTAPIKEYS
APIKEY1 = "CONFIDENCIAL"
APIKEY2 = "CONFIDENCIAL"

# USAMOS PYGAME PARA CONTROLAR LA REPRODUCCION DE AUDIOS WAV
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

class SistemaSeguridad:
    def __init__(self):
        # Rutas de audio
        self.audio1 = r"C:\Users\Admin\Desktop\handsup1.wav"
        self.audio2 = r"C:\Users\Admin\Desktop\handsup2.wav"
        self.audio3 = r"C:\Users\Admin\Desktop\handsup3.wav"
        
        # Verificar audios
        self.verificar_audios()
        
        # Estado del sistema (thread-safe)
        self.modo = "abierto"
        self.estado = "idle"
        self.tiempo_inicio = 0
        self.audio_sonando = False
        self.lock = threading.Lock()
        
        # Estabilización
        self.frame_count_arriba = 0
        self.frame_count_abajo = 0
        self.frame_count_persona = 0
        self.umbral_estable = 3
        
        # Control de video
        self.video_ejecutando = True
        
        # Cargar modelo
        print("Cargando modelo...")
        self.model = YOLO("yolo11n-pose.pt")
        self.model.conf = 0.5
        print("Modelo cargado en CPU")
        
        # Cámara
        print("Iniciando cámara...")
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        if not self.cap.isOpened():
            print("ERROR: No se pudo abrir la cámara")
            exit()
        
        # Bot de Telegram
        self.bot = Bot(API=KEY)
        self.updater = None
    
    def verificar_audios(self):
        audios = [self.audio1, self.audio2, self.audio3]
        for i, audio in enumerate(audios, 1):
            if not os.path.exists(audio):
                print(f"ERROR: No existe {audio}")
                setattr(self, f"audio{i}", None)
            else:
                print(f"OK: audio{i} encontrado")
    
    def enviar_notificacion(self, mensaje, foto=None):
        """Envía notificación (puede ser llamada desde cualquier hilo)"""
        try:
            if foto is not None:
                _, buffer = cv2.imencode('.jpg', foto, [cv2.IMWRITE_JPEG_QUALITY, 70])
                self.bot.send_photo(API_id=API_ID, photo=buffer.tobytes(), caption=mensaje)
            else:
                self.bot.send_message(chat_id=CHAT_ID, text=mensaje, parse_mode='Markdown')
            print(f"[NOTIFICACION] {mensaje[:50]}...")
        except Exception as e:
            print(f"Error notificación: {e}")
    
    def enviar_menu_con_botones(self):
        """Envía menú con botones inline"""
        with self.lock:
            modo_actual = "🟢 ABIERTO" if self.modo == "abierto" else "🔴 CERRADO"
        
        keyboard = [
            [InlineKeyboardButton("🏪 ABRIR LOCAL", callback_data='abrir')],
            [InlineKeyboardButton("🔒 CERRAR LOCAL", callback_data='cerrar')],
            [InlineKeyboardButton("📸 CAPTURAR FOTO", callback_data='foto')],
            [InlineKeyboardButton("📊 VER ESTADO", callback_data='estado')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        mensaje = f"🤖 *SISTEMA DE SEGURIDAD*\n\nModo actual: {modo_actual}\n\nSelecciona una opción:"
        self.bot.send_message(chat_id=CHAT_ID, text=mensaje, parse_mode='Markdown', reply_markup=reply_markup)
    
    def enviar_foto_actual(self):
        """Captura y envía la foto actual"""
        ret, frame = self.cap.read()
        if ret:
            with self.lock:
                modo = self.modo.upper()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cv2.putText(frame, f"Modo: {modo}", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(frame, timestamp, (10, 60), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            mensaje = f"📸 Foto del establecimiento\nModo: {modo}\nHora: {timestamp}"
            self.enviar_notificacion(mensaje, frame)
            return True
        return False
    
    def reproducir_audio(self, ruta):
        if ruta is None:
            return False
        try:
            pygame.mixer.music.load(ruta)
            pygame.mixer.music.play()
            self.audio_sonando = True
            return True
        except Exception as e:
            print(f"Error audio: {e}")
            return False
    
    def detener_audio(self):
        pygame.mixer.music.stop()
        self.audio_sonando = False
    
    def audio_terminado(self):
        return not pygame.mixer.music.get_busy()
    
    def detectar_personas(self, frame):
        results = self.model(frame, verbose=False)
        r = results[0]
        hay_persona = len(r.boxes) > 0 if r.boxes is not None else False
        
        if hay_persona:
            self.frame_count_persona += 1
        else:
            self.frame_count_persona = 0
        
        return self.frame_count_persona >= self.umbral_estable, r.plot() if hay_persona else frame
    
    def detectar_manos_arriba(self, frame):
        results = self.model(frame, verbose=False)
        r = results[0]
        manos_arriba = False
        
        if r.keypoints is not None and len(r.keypoints.xy) > 0:
            kpts = r.keypoints.xy[0]
            if len(kpts) > 10:
                nariz_y = float(kpts[0][1])
                muneca_izq_y = float(kpts[9][1])
                muneca_der_y = float(kpts[10][1])
                if muneca_izq_y < nariz_y and muneca_der_y < nariz_y:
                    manos_arriba = True
        
        if manos_arriba:
            self.frame_count_arriba += 1
            self.frame_count_abajo = 0
        else:
            self.frame_count_abajo += 1
            self.frame_count_arriba = 0
        
        manos_estable_arriba = self.frame_count_arriba >= self.umbral_estable
        manos_estable_abajo = self.frame_count_abajo >= self.umbral_estable
        
        return manos_estable_arriba, manos_estable_abajo, r.plot()
    
    def ejecutar_modo_abierto(self, frame):
        manos_arriba, manos_abajo, frame_anotado = self.detectar_manos_arriba(frame)
        tiempo_actual = time.time()
        
        if manos_abajo:
            if self.estado != "idle":
                print("[RESET] Cancelado")
                self.detener_audio()
                self.estado = "idle"
                self.tiempo_inicio = 0
            cv2.putText(frame_anotado, "MANOS ABAJO", (50, 100), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        elif manos_arriba:
            cv2.putText(frame_anotado, "MANOS ARRIBA", (50, 100), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
            
            if self.estado == "idle":
                self.estado = "contando1"
                self.tiempo_inicio = tiempo_actual
                print("[INFO] Iniciando conteo")
            elif self.estado == "contando1":
                tiempo_transcurrido = tiempo_actual - self.tiempo_inicio
                tiempo_restante = max(0, 3 - tiempo_transcurrido)
                cv2.putText(frame_anotado, f"Audio en: {tiempo_restante:.1f}s", (50, 150), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
                if tiempo_transcurrido >= 3:
                    print("[AUDIO] Mensaje 1")
                    self.reproducir_audio(self.audio1)
                    self.estado = "esperando_fin_audio1"
                    self.tiempo_inicio = tiempo_actual
                    self.enviar_notificacion("🚨 EMERGENCIA\nGesto de manos arriba detectado")
            elif self.estado == "esperando_fin_audio1":
                cv2.putText(frame_anotado, "MENSAJE ACTIVO", (50, 150), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                if self.audio_terminado():
                    self.estado = "contando2"
                    self.tiempo_inicio = tiempo_actual
                    print("[INFO] Esperando alarma")
            elif self.estado == "contando2":
                tiempo_transcurrido = tiempo_actual - self.tiempo_inicio
                tiempo_restante = max(0, 3 - tiempo_transcurrido)
                cv2.putText(frame_anotado, f"ALARMA en: {tiempo_restante:.1f}s", (50, 150), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 3)
                if tiempo_transcurrido >= 3:
                    print("[ALARMA] Activando")
                    self.reproducir_audio(self.audio2)
                    self.estado = "alarma"
                    self.enviar_notificacion("🔴 ALARMA ACTIVADA\nEmergencia confirmada", frame)
            elif self.estado == "alarma":
                cv2.putText(frame_anotado, "!!! ALARMA !!!", (50, 150), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 3)
                if self.audio_terminado():
                    self.estado = "idle"
                    print("[INFO] Sistema reiniciado")
        
        return frame_anotado
    
    def ejecutar_modo_cerrado(self, frame):
        hay_persona, frame_anotado = self.detectar_personas(frame)
        tiempo_actual = time.time()
        
        if hay_persona:
            cv2.putText(frame_anotado, "¡INTRUSO!", (50, 100), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 3)
            
            if self.estado == "idle":
                self.estado = "contando_persona"
                self.tiempo_inicio = tiempo_actual
                print("[INFO] Intruso detectado")
            elif self.estado == "contando_persona":
                tiempo_transcurrido = tiempo_actual - self.tiempo_inicio
                tiempo_restante = max(0, 3 - tiempo_transcurrido)
                cv2.putText(frame_anotado, f"Alerta en: {tiempo_restante:.1f}s", (50, 150), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
                if tiempo_transcurrido >= 3:
                    self.reproducir_audio(self.audio3)
                    self.estado = "esperando_fin_audio1"
                    self.tiempo_inicio = tiempo_actual
                    self.enviar_notificacion("🚨 INTRUSO\nLocal cerrado - Persona detectada", frame)
            elif self.estado == "esperando_fin_audio1":
                cv2.putText(frame_anotado, "MENSAJE ACTIVO", (50, 150), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                if self.audio_terminado():
                    self.estado = "contando2"
                    self.tiempo_inicio = tiempo_actual
            elif self.estado == "contando2":
                tiempo_transcurrido = tiempo_actual - self.tiempo_inicio
                tiempo_restante = max(0, 3 - tiempo_transcurrido)
                cv2.putText(frame_anotado, f"ALARMA en: {tiempo_restante:.1f}s", (50, 150), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 3)
                if tiempo_transcurrido >= 3:
                    self.reproducir_audio(self.audio2)
                    self.estado = "alarma"
                    self.enviar_notificacion("🔴 ALARMA\nIntruso persistente", frame)
            elif self.estado == "alarma":
                cv2.putText(frame_anotado, "!!! ALARMA !!!", (50, 150), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 3)
                if self.audio_terminado():
                    self.estado = "idle"
        else:
            if self.estado != "idle":
                self.estado = "idle"
                self.detener_audio()
            cv2.putText(frame_anotado, "SEGURO", (50, 100), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        return frame_anotado
    
    def loop_video(self):
        """Loop de video en hilo separado"""
        print("[VIDEO] Iniciando procesamiento de video...")
        
        while self.video_ejecutando:
            ret, frame = self.cap.read()
            if not ret:
                continue
            
            with self.lock:
                modo_actual = self.modo
            
            if modo_actual == "abierto":
                frame_anotado = self.ejecutar_modo_abierto(frame)
            else:
                frame_anotado = self.ejecutar_modo_cerrado(frame)
            
            with self.lock:
                modo_texto = self.modo.upper()
            
            cv2.putText(frame_anotado, f"MODO: {modo_texto}", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0) if modo_texto == "ABIERTO" else (0, 0, 255), 2)
            
            cv2.imshow("Sistema Seguridad", frame_anotado)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.video_ejecutando = False
                break
        
        self.cap.release()
        cv2.destroyAllWindows()
        print("[VIDEO] Procesamiento de video terminado")
    
    # ============ COMANDOS PARA CHATBOT ============
    
    def cmd_start(self, update, context):
        """Comando /start - muestra menú con botones"""
        if str(update.effective_chat.id) != CHAT_ID:
            update.message.reply_text("❌ No autorizado")
            return
        
        print("[COMANDO] /start recibido")
        self.enviar_menu_con_botones()
    
    def cmd_abrir(self, update, context):
        """Comando /abrir - cambia a modo abierto"""
        if str(update.effective_chat.id) != CHAT_ID:
            return
        
        print("[COMANDO] /abrir recibido")
        
        with self.lock:
            self.modo = "abierto"
            self.estado = "idle"
        self.detener_audio()
        
        update.message.reply_text("🏪 LOCAL ABIERTO\nModo: Emergencia (manos arriba)")
        
        ret, frame = self.cap.read()
        if ret:
            self.enviar_notificacion("📢 Modo cambiado: ABIERTO", frame)
    
    def cmd_cerrar(self, update, context):
        """Comando /cerrar - cambia a modo cerrado"""
        if str(update.effective_chat.id) != CHAT_ID:
            return
        
        print("[COMANDO] /cerrar recibido")
        
        with self.lock:
            self.modo = "cerrado"
            self.estado = "idle"
        self.detener_audio()
        
        update.message.reply_text("🔒 LOCAL CERRADO\nModo: Seguridad (detección de intrusos)")
        
        ret, frame = self.cap.read()
        if ret:
            self.enviar_notificacion("📢 Modo cambiado: CERRADO", frame)
    
    def cmd_foto(self, update, context):
        """Comando /foto - captura y envía foto"""
        if str(update.effective_chat.id) != CHAT_ID:
            return
        
        print("[COMANDO] /foto recibido")
        update.message.reply_text("📸 Capturando foto...")
        self.enviar_foto_actual()
    
    def cmd_estado(self, update, context):
        """Comando /estado - muestra estado del sistema"""
        if str(update.effective_chat.id) != CHAT_ID:
            return
        
        print("[COMANDO] /estado recibido")
        
        with self.lock:
            modo_texto = "🟢 ABIERTO" if self.modo == "abierto" else "🔴 CERRADO"
            estado_actual = self.estado
            audio_estado = "🔊 SONANDO" if self.audio_sonando else "🔇 SILENCIO"
        
        estado_msg = f"""
📊 *ESTADO DEL SISTEMA*

Modo: {modo_texto}
Estado: `{estado_actual}`
Audio: {audio_estado}

*Comandos:*
/start - Mostrar menú
/abrir - Modo abierto
/cerrar - Modo cerrado
/foto - Capturar foto
/estado - Este mensaje
        """
        update.message.reply_text(estado_msg, parse_mode='Markdown')
    
    # ============ CALLBACKS PARA BOTONES ============
    
    def button_callback(self, update, context):
        """Maneja los botones inline"""
        query = update.callback_query
        query.answer()
        
        chat_id = str(query.message.chat_id)
        if chat_id != CHAT_ID:
            return
        
        data = query.data
        print(f"[BOTON] {data} presionado")
        
        if data == 'abrir':
            with self.lock:
                self.modo = "abierto"
                self.estado = "idle"
            self.detener_audio()
            query.edit_message_text("🏪 LOCAL ABIERTO\nModo: Emergencia (manos arriba)")
            ret, frame = self.cap.read()
            if ret:
                self.enviar_notificacion("📢 Modo cambiado: ABIERTO", frame)
        
        elif data == 'cerrar':
            with self.lock:
                self.modo = "cerrado"
                self.estado = "idle"
            self.detener_audio()
            query.edit_message_text("🔒 LOCAL CERRADO\nModo: Seguridad (detección de intrusos)")
            ret, frame = self.cap.read()
            if ret:
                self.enviar_notificacion("📢 Modo cambiado: CERRADO", frame)
        
        elif data == 'foto':
            query.edit_message_text("📸 Capturando foto...")
            self.enviar_foto_actual()
        
        elif data == 'estado':
            with self.lock:
                modo_texto = "🟢 ABIERTO" if self.modo == "abierto" else "🔴 CERRADO"
                estado_actual = self.estado
                audio_estado = "🔊 SONANDO" if self.audio_sonando else "🔇 SILENCIO"
            
            estado_msg = f"""
📊 *ESTADO DEL SISTEMA*

Modo: {modo_texto}
Estado: `{estado_actual}`
Audio: {audio_estado}
            """
            query.edit_message_text(estado_msg, parse_mode='Markdown')
        
        # Volver a mostrar el menú después de 2 segundos (excepto para estado)
        if data != 'estado':
            import threading
            threading.Timer(2.0, self.enviar_menu_con_botones).start()
    
    def ejecutar(self):
        """Main - el bot es el hilo principal, video en segundo plano"""
        print("\n" + "="*50)
        print("SISTEMA DE SEGURIDAD")
        print("="*50)
        print("Modo: ABIERTO")
        print("\nComandos Telegram:")
        print("/start - Mostrar menú con botones")
        print("/abrir - Modo abierto")
        print("/cerrar - Modo cerrado")
        print("/foto - Capturar foto")
        print("/estado - Ver estado")
        print("\nPresiona 'q' en la ventana de video para salir")
        print("="*50 + "\n")
        
        # Iniciar el loop de video en un hilo separado
        video_thread = threading.Thread(target=self.loop_video, daemon=True)
        video_thread.start()
        
        # Enviar mensaje de inicio
        self.enviar_menu_con_botones()
        
        # Iniciar el bot (esto es bloqueante y será el hilo principal)
        print("[BOT] Iniciando bot de Telegram...")
        
        self.updater = Updater(API=KEY, use_context=True)
        dp = self.updater.dispatcher
        
        # Comandos de texto
        dp.add_handler(CommandHandler("start", self.cmd_start))
        dp.add_handler(CommandHandler("abrir", self.cmd_abrir))
        dp.add_handler(CommandHandler("cerrar", self.cmd_cerrar))
        dp.add_handler(CommandHandler("foto", self.cmd_foto))
        dp.add_handler(CommandHandler("estado", self.cmd_estado))
        
        # Callback para botones
        dp.add_handler(CallbackQueryHandler(self.button_callback))
        
        # Iniciar polling (bloqueante)
        self.updater.start_polling()
        self.updater.idle()  # Mantiene el bot corriendo
        
        # Cuando se sale, limpiar
        self.video_ejecutando = False
        pygame.mixer.quit()
        print("Programa terminado")

if __name__ == "__main__":
    sistema = SistemaSeguridad()
    sistema.ejecutar()
