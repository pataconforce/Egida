# SETUP

A continuacion encontraras las instrucciones para levantar el proyecto en tu computadora.

Este proyecto funciona con Python 3.11.15, para instalar Python usaremos el package manager uv, que permite instalar multiples versiones de Python en la misma computadora e intercambiar entre ellas facilmente por comandos.

1. Instalar uv usando este comando:

macOS/Linux:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Windows:
```bash
irm https://astral.sh/uv/install.ps1 | iex
```

2. Verifica la version de uv:

```bash
uv --version
```

3. Instala Python 3.11.15:

```bash
uv python install 3.11.15
```

4. Crea el entorno virtual:

```bash
uv venv --python 3.11.15
```

5. Activa el entorno virtual:

macOS/Linux:
```bash
source .venv/bin/activate
```

Windows:
```bash
.venv\Scripts\activate
```

5. Instala las dependencias:

```bash
uv pip install -r requirements.txt
```