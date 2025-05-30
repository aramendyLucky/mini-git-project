# Informe de Desarrollo y Documentación del Proyecto Mini-Git

## Esquema general del sistema

```
┌────────────────────┐        HTTP/REST         ┌────────────────────┐        Llamadas Python         ┌────────────────────┐
│   Frontend Web     │ <--------------------->  │      Backend       │ <--------------------------->  │       Core         │
│ (HTML, JS, CSS)    │    (FastAPI, API REST)   │ (minigit_core.py)  │   (repository.py, commit.py)  │
└────────────────────┘                          └────────────────────┘                               └────────────────────┘
        │                        │                        │
        │ 1. Solicitud HTTP      │                        │
        ├───────────────────────▶│                        │
        │                        │ 2. Procesa endpoint    │
        │                        ├───────────────────────▶│
        │                        │                        │ 3. Lógica de archivos, commits, etc.
        │                        │◀───────────────────────┤
        │ 4. Respuesta JSON      │                        │
        ◀───────────────────────┤│                        │
        │                        │                        │

Leyenda:
- El Frontend realiza peticiones HTTP (fetch/ajax) a la API REST del Backend.
- El Backend expone endpoints, valida, procesa y delega la lógica avanzada a minigit_core.py.
- minigit_core.py interactúa con el core puro (repository.py, commit.py) para operaciones de bajo nivel.
- El flujo de datos es siempre: Frontend ⇄ Backend ⇄ Core.
```

Este esquema muestra cómo interactúan los tres componentes principales:
- **Frontend:** Interfaz de usuario moderna, realiza peticiones HTTP a la API.
- **Backend:** Expone la API REST, valida, procesa y delega en el core.
- **Core:** Lógica de bajo nivel, maneja archivos, commits y estructura interna.

## Diagrama de flujo: ciclo básico de trabajo

```
+-------------------+
|   Usuario Web     |
+-------------------+
          |
          v
+-------------------+
|  Agregar archivo  |
+-------------------+
          |
          v
+-------------------+
|   Staging (+/-)   |
+-------------------+
          |
          v
+-------------------+
|    Commit         |
+-------------------+
          |
          v
+-------------------+
|   Historial       |
+-------------------+
          |
          v
+-------------------+
|   Visualizar diff |
+-------------------+
```

**Descripción:**
- El usuario agrega archivos desde la web.
- Puede añadir o quitar archivos del área de staging (como `git add`/`git reset`).
- Realiza un commit con los archivos staged.
- Consulta el historial de commits y puede ver el diff de cualquier archivo respecto al último commit.

## Índice

- [1. Primeros pasos y motivación](#1-primeros-pasos-y-motivación)
- [2. Estructura inicial y organización](#2-estructura-inicial-y-organización)
- [3. Proceso de limpieza y modernización](#3-proceso-de-limpieza-y-modernización)
- [4. Problemas técnicos y soluciones](#4-problemas-técnicos-y-soluciones)
- [5. Documentación de archivos principales y su función](#5-documentación-de-archivos-principales-y-su-función)
- [6. Funcionalidades implementadas y pendientes](#6-funcionalidades-implementadas-y-pendientes)
- [7. Recomendaciones para continuar](#7-recomendaciones-para-continuar)
- [8. Contribución, actualización y buenas prácticas](#8-contribución-actualización-y-buenas-prácticas)

## 1. Primeros pasos y motivación

El proyecto Mini-Git surge como un sistema de control de versiones educativo, inspirado en Git, pero simplificado y adaptado para la web. El objetivo es aprender y experimentar con conceptos de versionado, staging, commits, ramas y diferencias de archivos, integrando un backend en Python (FastAPI) y un frontend moderno en JavaScript.

## 2. Estructura inicial y organización

La estructura del proyecto se diseñó para separar claramente responsabilidades:

```
mini-git-project/
│
├── backend/           # Lógica de API, integración web y core
│   ├── app.py         # API REST principal (FastAPI)
│   ├── minigit_core.py# Lógica avanzada tipo Git para la web
│   ├── requirements.txt
│   └── ...            # Otros scripts y carpetas auxiliares
│
├── core/              # Lógica base de Mini-Git (sin web)
│   ├── repository.py  # Clase principal de repositorio
│   ├── commit.py      # Lógica de commits
│   └── ...            # Otros módulos core
│
├── frontend/          # Interfaz web moderna
│   ├── index.html
│   ├── js/app.js      # Lógica JS, integración API, UI
│   └── css/style.css
│
├── tests/             # Pruebas automáticas de backend y lógica core
│   ├── test_*.py
│
├── reorganize_project.py # Script para ordenar y limpiar archivos (aprendizaje)
├── README.md
└── ...
```

### Script de orden y limpieza

Se creó el script `reorganize_project.py` para experimentar con la automatización de la organización de archivos y carpetas, facilitando el aprendizaje de manipulación de archivos en Python y manteniendo el proyecto ordenado.

## 3. Proceso de limpieza y modernización

- **Frontend:**  
  - Se modernizó completamente el frontend, usando clases JS, async/await, manejo de errores y una UI responsiva.
  - Se documentó exhaustivamente cada clase, método y función en `frontend/js/app.js`.
  - Se integraron funcionalidades avanzadas: diff visual, staging granular, eliminación de archivos, modales, alertas, etc.

- **Backend:**  
  - Se refactorizó y documentó exhaustivamente `backend/app.py` y `backend/minigit_core.py`.
  - Se separó la lógica core (`core/`) de la lógica web (`backend/minigit_core.py`).
  - Se implementaron endpoints REST claros y robustos, con validación y manejo de errores.
  - Se corrigieron problemas de rutas, codificación, staging y sincronización con el frontend.

- **Core:**  
  - Se mantuvo la lógica base en `core/`, permitiendo su uso tanto por CLI como por la web.
  - Se documentaron las clases principales (`Repository`, `Commit`).

- **Pruebas:**  
  - Se crearon tests automáticos para cada funcionalidad avanzada (diff, staging, eliminación, etc.).
  - Se validó el correcto funcionamiento de la API y la lógica core.

## 4. Problemas técnicos y soluciones

- **Sincronización backend/frontend:**  
  - Se corrigieron rutas relativas y absolutas para asegurar que los archivos se lean y escriban correctamente desde ambos lados.
  - Se ajustó la serialización/deserialización de datos (JSON, codificación UTF-8).
  - Se mejoró el manejo de errores para que el frontend reciba mensajes claros y útiles.

- **Staging granular:**  
  - Se implementó una lógica de staging por archivo, permitiendo agregar y quitar archivos individualmente, similar a Git.
  - Se adaptó la UI para reflejar el estado real del área de staging.

- **Diff de archivos:**  
  - Se integró `difflib` para mostrar diferencias entre la versión actual y la última commiteada.
  - Se creó un endpoint y un modal visual para mostrar el diff en la web.

- **Eliminación y manejo de archivos:**  
  - Se implementó la eliminación segura de archivos, quitándolos también del área de staging si era necesario.
  - Se validó la existencia y permisos antes de cada operación.

## 5. Documentación de archivos principales y su función

### backend/app.py

- **Propósito:**  
  API REST principal. Expone endpoints para inicializar el repo, consultar estado, agregar/eliminar archivos, hacer commit, ver historial, obtener diffs y gestionar el área de staging.
- **Funciones clave:**  
  - `init_repository`, `get_status`, `add_files`, `create_commit`, `get_commit_history`, `get_commit_details`, `list_files`, `get_file_content`, `delete_file`, `get_file_diff`, `stage_file`, `unstage_file`.
- **Por qué es importante:**  
  Es el punto de entrada de la web, conecta el frontend con la lógica core y gestiona la validación y el flujo de datos.

### backend/minigit_core.py

- **Propósito:**  
  Lógica avanzada tipo Git para la web: snapshots, commits, staging granular, diff, historial, etc.
- **Funciones clave:**  
  - `init`, `get_status`, `add_files`, `commit`, `get_commit_history`, `get_commit_details`, `get_file_content`, `get_file_diff`, `stage_file`, `unstage_file`.
- **Por qué es importante:**  
  Permite funcionalidades avanzadas y flexibles, separando la lógica web de la lógica core.

### core/repository.py y core/commit.py

- **Propósito:**  
  Lógica base de Mini-Git (sin web). Manejan el repositorio, los archivos y los commits.
- **Funciones clave:**  
  - `Repository.init`, `Repository.add_file`, `Repository.remove_file_from_staging`, `Repository.get_commits`, etc.
  - `Commit.create`, etc.
- **Por qué es importante:**  
  Permite reutilizar la lógica tanto en CLI como en la web, y facilita el testing.

### frontend/js/app.js

- **Propósito:**  
  Lógica del frontend: interacción con la API, manejo de estado, renderizado de UI, eventos y UX.
- **Funciones clave:**  
  - Clases: `MiniGitAPI`, `AppState`, `UIHelper`, `PageHandler`.
  - Métodos: cargar dashboard, archivos, commits, staging, diff, eliminar, etc.
- **Por qué es importante:**  
  Es la cara visible del sistema, y está exhaustivamente comentado para facilitar la extensión y el mantenimiento.

## 6. Funcionalidades implementadas y pendientes

- **Implementadas:**  
  - Inicialización de repositorio
  - Agregado y eliminación de archivos
  - Staging granular (+/-)
  - Commit de archivos staged
  - Visualización de historial y detalles de commits
  - Visualización de diff entre archivos
  - Pruebas automáticas para cada función avanzada
  - Documentación exhaustiva en frontend y backend

- **Pendientes o sugeridas:**  
  - Soporte para ramas y merge
  - Renombrar archivos
  - Descargar archivos y versiones
  - Ver archivos de cualquier commit
  - Búsqueda de archivos/contenido
  - Soporte para archivos binarios
  - Mejoras de seguridad y autenticación
  - Modularización avanzada y más tests de integración

---

## 7. Recomendaciones para continuar

- Revisa este informe y la documentación en el código antes de retomar el desarrollo.
- Si agregas nuevas funciones, sigue el estándar de comentarios y pruebas automáticas.
- Considera modularizar aún más si el proyecto crece (por ejemplo, separando rutas, modelos y servicios en el backend).
- Mantén el script de organización actualizado si agregas o mueves archivos.

---

## 8. Contribución, actualización y buenas prácticas

### ¿Cómo contribuir o continuar el desarrollo?

- **Lee primero este informe y la documentación en el código.**
- Antes de agregar nuevas funcionalidades, revisa si ya existe algo similar y sigue el estándar de comentarios y pruebas automáticas.
- Si agregas endpoints, documenta su propósito, parámetros y respuestas en el código y aquí.
- Si modificas la estructura de carpetas o archivos, actualiza este informe y el script de organización si es necesario.
- Si encuentras un bug o problema técnico, documenta la causa y la solución aplicada en una sección nueva de este informe.
- Si implementas una funcionalidad avanzada (ramas, merge, binarios, etc.), explica brevemente la lógica y los archivos afectados.

### Buenas prácticas recomendadas

- **Documenta exhaustivamente:** Cada clase, función y endpoint debe tener docstrings claros y comentarios relevantes.
- **Haz commits pequeños y descriptivos:** Explica el "por qué" del cambio, no solo el "qué".
- **Mantén la compatibilidad:** Si cambias la API, revisa que el frontend y los tests sigan funcionando.
- **Agrega pruebas automáticas:** Cada nueva función debe tener su test en `tests/`.
- **No mezcles lógica de negocio y de presentación:** Mantén la separación entre core, backend y frontend.
- **Actualiza este informe:** Cada vez que realices cambios estructurales, agregues endpoints o soluciones problemas importantes.

### ¿Cómo actualizar el proyecto?

1. Haz pull de la última versión del repositorio.
2. Lee este informe para entender el estado actual y los cambios recientes.
3. Instala dependencias si es necesario (`pip install -r backend/requirements.txt`).
4. Corre los tests automáticos antes y después de tus cambios.
5. Si agregas archivos, actualiza el script de organización y este informe.
6. Documenta todo cambio relevante en el código y aquí.

---

*Este proyecto está pensado para ser didáctico, modular y fácil de mantener. Si sigues estas recomendaciones, cualquier desarrollador podrá retomarlo y continuar el desarrollo sin perder contexto.*

---

*Actualiza este informe cada vez que realices cambios estructurales, agregues funcionalidades importantes o soluciones problemas técnicos relevantes.*
