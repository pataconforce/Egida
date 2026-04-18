# EGIDA

EGIDA es un sistema de visión por computadora diseñado para transformar un gesto humano universal en un mecanismo automático de protección. Detecta la elevación de manos como señal de auxilio y activa respuestas disuasivas en tiempo real, reemplazando la supervisión humana continua con un sistema autónomo, preciso y siempre atento.

---

## Descripción

EGIDA redefine la seguridad basada en video al introducir un enfoque activo. En lugar de depender de operadores humanos que monitorean cámaras de forma continua, el sistema mantiene una vigilancia constante con niveles de concentración superiores a los humanos, identificando señales de vulnerabilidad y actuando de inmediato.

Ante la detección de una situación potencial de riesgo, EGIDA ejecuta una secuencia controlada de acciones: captura evidencia visual, emite advertencias auditivas y, si es necesario, activa alarmas. Todo el proceso está diseñado para ser reversible y controlable directamente por el usuario en sitio.

---

## Principios de diseño

- Ultraligero
- Escalable
- Diseñado para operación en edge
- Capaz de ejecutarse con recursos limitados
- Baja latencia
- Alta confiabilidad en entornos reales
- Requiere de internet para notificar a terceros.
- Identifica, registra y disuade sin internet, IA local.

---

## Diferenciación

Los sistemas tradicionales de detección de amenazas, como los detectores de armas, presentan en la práctica una alta tasa de falsos positivos. En escenarios reales, hasta 9 de cada 10 detecciones pueden ser incorrectas debido a limitaciones de ángulo, visibilidad u oclusión.

EGIDA elimina este problema al no depender de la visibilidad de un objeto específico. En su lugar, se basa en una señal humana intencional y universal: la elevación de las manos. Esto permite detectar situaciones de riesgo incluso cuando la amenaza no es visible para la cámara.

---

## Funcionamiento

EGIDA utiliza una secuencia temporal estructurada para activar respuestas de forma progresiva:

1. Detección del gesto de manos elevadas durante 3 segundos  
2. Reproducción de un primer mensaje de audio:  
   "Este es el centro de monitoreo, ¿está todo bien?"  
3. Nueva ventana de observación de 3 segundos  
4. Activación de una alarma sonora si la señal persiste  
5. Captura automática de evidencia (imágenes) y envío a personal de seguridad  

El sistema permite intervención inmediata por parte del usuario en sitio:  
la secuencia puede detenerse en cualquier momento simplemente bajando las manos.

---
## Interfaz de usuario

EGIDA utiliza nuestro BOT de Telegram ADIA_BOT como interfaz principal de interacción.

A través de un bot, el sistema permite:

- Recepción inmediata de alertas 
- Envío automático de imágenes capturadas durante eventos  
- Notificaciones en tiempo real al personal de seguridad  
- Control remoto básico del sistema a través de botones y comandos:
  1: Abrir local
  2: Cerrar local
  3: Capturar foto
  4: Ver estado

Este enfoque elimina la necesidad de interfaces complejas y permite una integración directa con herramientas de comunicación ya adoptadas por los usuarios.

## Modos de operación

### Modo "Local Cerrado"

Diseñado para escenarios fuera de horario o sin presencia autorizada.

- No se permite el ingreso de personas  
- Si se detecta presencia:
  - Se emite un mensaje de advertencia  
  - Se activa una alarma progresiva  
  - Se envía evidencia al personal de seguridad  
- La alarma se mantiene activa mientras exista presencia en la escena  

Este modo reemplaza sistemas de alarma tradicionales.

---

### Modo "Local Abierto"

Diseñado para operación en horario normal, con presencia de personas.

- Se permite el ingreso y tránsito habitual  
- El sistema permanece en estado de vigilancia constante  
- Ante la elevación de manos:
  - Se inicia la secuencia de validación y alerta  
  - Se ejecutan acciones disuasivas progresivas  
  - El usuario mantiene control total para cancelar la alerta  

Este modo introduce un mecanismo de protección activa durante la operación normal del negocio.

---

## Arquitectura

EGIDA está diseñado para funcionar en entornos edge, procesando video directamente en el punto de captura sin depender de infraestructura centralizada.
Cámaras → Nodo de procesamiento edge → Motor de visión → Eventos / Respuesta
- Procesamiento local en tiempo real  
- Independencia de la nube  
- Despliegue modular y escalable  

---

## Capacidades

- Detección de gestos humanos en tiempo real  
- Reemplazo de monitoreo humano 24/7  
- Activación automática de acciones disuasivas  
- Captura y envío de evidencia visual  
- Control directo por parte del usuario en sitio  
- Operación continua con alta precisión  

---

## Licencia

Este proyecto está licenciado bajo MIT License

---

## Atribución

Si utilizas este proyecto, se solicita mantener referencia a su origen:

EGIDA — Sistema de protección activa basado en visión por computadora

