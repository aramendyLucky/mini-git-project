# 🕹️ Mini-Git

![Mini-Git Banner](https://em-content.zobj.net/thumbs/120/microsoft/319/floppy-disk_1f4be.png)

Mini-Git es un sistema de control de versiones simplificado, inspirado en Git, ideal para aprender los conceptos básicos de control de versiones y cómo funcionan internamente.

---

## 🎯 Objetivo

El objetivo de Mini-Git es didáctico: mostrar cómo funcionan internamente los conceptos básicos de un sistema de control de versiones (staging, commits, historial, etc.) de forma sencilla y entendible.

---

## 🛠️ Instalación

Solo necesitas Python 3. No requiere dependencias externas.

---

## 🚀 Uso rápido

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

- `minigit.py`           : 🎮 Lógica principal y CLI.
- `repository.py`        : 🗂️ Lógica de manejo del repositorio.
- `commit.py`            : 💾 Clase para representar commits.
- `test_repository.py`   : 🧪 Pruebas unitarias.
- `test_complete_flow.py`: 🧪 Pruebas de flujo completo.
- `cheatsheet.txt`       : 📜 Comandos rápidos.
- `explicacion_minigit.txt`: 📖 Explicación detallada del código y arquitectura.

---

## 📝 Licencia

MIT

---

> 🎲 ¡Diviértete versionando como en los viejos tiempos!