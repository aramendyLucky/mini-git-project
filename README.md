# 🕹️ Mini-Git

![Mini-Git Banner](https://em-content.zobj.net/thumbs/120/microsoft/319/floppy-disk_1f4be.png)

Mini-Git es un sistema de control de versiones simplificado, inspirado en Git, ideal para aprender los conceptos básicos de control de versiones y cómo funcionan internamente.

---

## 🎯 Objetivo

El objetivo de Mini-Git es didáctico: mostrar cómo funcionan internamente los conceptos básicos de un sistema de control de versiones (staging, commits, historial, etc.) de forma sencilla y entendible.

---

## 🛠️ Instalación

Solo necesitas Python 3. No requiere dependencias externas para la CLI.

---

## 🚀 Uso rápido (CLI)

```sh
🕹️ python minigit.py init
🕹️ python minigit.py add archivo.txt
🕹️ python minigit.py commit -m "Primer commit"
🕹️ python minigit.py log
```

---

## 🎮 Comandos disponibles

- 🏁 **init**   : Inicializa un nuevo repositorio.
- ➕ **add**    : Añade archivos al área de staging.
- 💾 **commit** : Crea un nuevo commit.
- 📋 **status** : Muestra el estado del repositorio.
- 🕰️ **log**    : Muestra el historial de commits.
- 🔍 **show**   : Muestra detalles de un commit.

---

## 🧩 Ejemplo de flujo completo

```sh
🕹️ python minigit.py init
🕹️ echo "Hola Mini-Git" > ejemplo.txt
🕹️ python minigit.py add ejemplo.txt
🕹️ python minigit.py commit -m "Primer commit"
🕹️ python minigit.py status
🕹️ python minigit.py log
🕹️ python minigit.py show
```

---

## 📁 Estructura del proyecto

```
mini-git-project/
├── backend/
│   ├── app.py              # Servidor FastAPI principal
│   ├── minigit_core.py     # Lógica central adaptada
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py       # Endpoints de la API
│   └── requirements.txt    # Dependencias backend
├── frontend/
│   ├── index.html          # Interfaz principal
│   ├── css/
│   │   └── style.css       # Estilos
│   └── js/
│       └── app.js          # Lógica JS
├── repository.py           # Lógica de repositorio (legacy/core)
├── commit.py               # Lógica de commits (legacy/core)
├── minigit.py              # CLI original
└── README.md               # Este archivo
```

---

## ⚙️ Instalación y ejecución (Web)

### 1. Clona el repositorio

```sh
git clone https://github.com/aramendyLucky/mini-git-project.git
cd mini-git-project
```

### 2. Instala dependencias del backend

```sh
cd backend
pip install -r requirements.txt
```

### 3. Ejecuta el servidor FastAPI

```sh
python -m uvicorn app:app --reload
```

### 4. Abre la interfaz web

Visita [http://127.0.0.1:8000/](http://127.0.0.1:8000/) en tu navegador.

---

## 🖥️ Uso básico (Web)

1. **Inicializa el repositorio** con el botón correspondiente.
2. **Agrega archivos** usando el formulario.
3. **Haz commits** con un mensaje.
4. **Consulta historial y archivos** desde la interfaz.

---

## 🧪 Ejemplo paso a paso para probar Mini-Git

### Opción 1: Usar Mini-Git desde la línea de comandos (CLI)

1. **Inicializa el repositorio**  
   Ejecuta en la terminal:
   ```sh
   python minigit.py init
   ```
   Esto crea la estructura interna de Mini-Git en tu carpeta actual.

2. **Crea un archivo de prueba**  
   Por ejemplo:
   ```sh
   echo "Hola Mini-Git" > ejemplo.txt
   ```

3. **Agrega el archivo al área de staging**  
   ```sh
   python minigit.py add ejemplo.txt
   ```

4. **Haz un commit**  
   ```sh
   python minigit.py commit -m "Primer commit"
   ```

5. **Consulta el estado del repositorio**  
   ```sh
   python minigit.py status
   ```

6. **Mira el historial de commits**  
   ```sh
   python minigit.py log
   ```

7. **Muestra detalles de un commit**  
   ```sh
   python minigit.py show
   ```

---

### Opción 2: Usar Mini-Git desde la interfaz web

1. **Arranca el backend**  
   Desde la carpeta `backend/`:
   ```sh
   pip install -r requirements.txt
   python -m uvicorn app:app --reload
   ```

2. **Abre la interfaz web**  
   Ve a [http://127.0.0.1:8000/](http://127.0.0.1:8000/) en tu navegador.

3. **Inicializa el repositorio**  
   Haz clic en el botón "🏁 Inicializar Repositorio".

4. **Agrega archivos**  
   Usa el formulario "➕ Añadir archivo" para crear archivos y su contenido.

5. **Haz commits**  
   Escribe un mensaje y haz clic en "Hacer commit".

6. **Consulta historial y archivos**  
   Visualiza los commits recientes, el estado y los archivos desde la interfaz.

---

## 🚦 Reinicio rápido del backend (Windows)

Para facilitar el desarrollo, puedes reiniciar el backend automáticamente usando el script PowerShell incluido:

1. Abre una terminal PowerShell.
2. Ve a la carpeta `backend/`:
   ```powershell
   cd backend
   ```
3. Ejecuta el script:
   ```powershell
   ./restart_backend.ps1
   ```

Este script:
- Detiene cualquier proceso de FastAPI/uvicorn activo.
- Cambia a la carpeta correcta.
- Inicia el backend con recarga automática (`python -m uvicorn app:app --reload`).
- Muestra mensajes informativos en cada paso.

> Útil para aplicar cambios de código sin cerrar manualmente procesos.

---

## 🧪 Pruebas automáticas por terminal

El proyecto incluye tests unitarios y de flujo completo en la carpeta `tests/`. Puedes ejecutarlos así:

1. Ve a la raíz del proyecto:
   ```powershell
   cd <ruta-del-proyecto>
   ```
2. Ejecuta los tests con:
   ```powershell
   python -m unittest discover tests
   ```
   o usando pytest (si lo tienes instalado):
   ```powershell
   pytest tests
   ```

**¿Por qué hacer tests?**
- Garantizan que la lógica de Mini-Git funciona correctamente tras cada cambio.
- Permiten detectar errores antes de usarlos en la web o CLI.
- Son una referencia de uso y ejemplos de flujo real.

---

## ℹ️ ¿Por qué esta estructura y scripts?

- **Separación de backend/frontend/core/tests**: Facilita el mantenimiento y la extensión del proyecto.
- **Script de reinicio**: Acelera el ciclo de desarrollo y evita errores por procesos colgados.
- **Tests**: Aseguran calidad y sirven de documentación viva.

---

## 🛠️ Stack tecnológico

- **Backend:** FastAPI, Python 3.8+
- **Frontend:** HTML5, CSS3, JavaScript (fetch API)
- **Estilo:** CSS moderno y responsivo

---

## 📦 Dependencias principales

- [FastAPI](https://fastapi.tiangolo.com/)
- [Uvicorn](https://www.uvicorn.org/)

---

## 📄 Licencia

MIT

---

## ✨ Créditos

Desarrollado por [aramendyLucky](https://github.com/aramendyLucky).

---

> 🎲 ¡Diviértete versionando como en los viejos tiempos!