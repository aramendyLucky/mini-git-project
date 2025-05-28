import os
import shutil

#Idea de orden de carpetas y archivos para un proyecto de software
# que implemente un sistema de control de versiones similar a Git.
# Este script reorganiza un proyecto existente en una estructura más limpia y modular.  
# Reorganiza un proyecto de software en una estructura modular
# y limpia, separando el backend, frontend, core y tests.
# Asegúrate de ejecutar este script en la raíz del proyecto.
# Importante: Este script asume que se ejecuta en la raíz del proyecto.

"""

mini-git-project/
├── backend/
│   ├── app.py              # 🆕 Servidor FastAPI (entrypoint backend)
│   ├── minigit_core.py     # 🆕 Lógica central adaptada para backend
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py       # 🆕 Endpoints de la API
│   └── requirements.txt    # 🆕 Dependencias del backend
├── frontend/
│   ├── index.html          # 🆕 Interfaz principal
│   ├── css/
│   │   └── style.css       # 🆕 Estilos
│   └── js/
│       └── app.js          # 🆕 Lógica JavaScript
├── core/
│   ├── repository.py       # Existente (lógica de repositorio)
│   ├── commit.py           # Existente (lógica de commit)
│   └── minigit.py          # CLI existente (puede quedarse aquí o en raíz)
├── tests/
│   ├── test_repository.py      # 🧪 Pruebas unitarias para repository
│   ├── test_commit.py          # 🧪 Pruebas unitarias para commit
│   ├── test_minigit_cli.py     # 🧪 Pruebas para la CLI
│   └── test_complete_flow.py   # 🧪 Pruebas de flujo completo
├── README.md               # 🆕 Documentación principal
└── .gitignore              # 🆕 Ignorar archivos temporales y dependencias

"""

# reorganize_project.py


# Estructura de carpetas y archivos a crear
structure = {
    "backend": [
        "app.py",
        "minigit_core.py",
        "requirements.txt",
        os.path.join("api", "__init__.py"),
        os.path.join("api", "routes.py"),
    ],
    "frontend": [
        "index.html",
        os.path.join("css", "style.css"),
        os.path.join("js", "app.js"),
    ],
    "core": [
        "repository.py",
        "commit.py",
        "minigit.py",
    ],
    "tests": [
        "test_repository.py",
        "test_commit.py",
        "test_minigit_cli.py",
        "test_complete_flow.py",
    ]
}

# Archivos que se moverán si existen en la raíz
move_files = {
    "repository.py": "core",
    "commit.py": "core",
    "minigit.py": "core",
    "test_repository.py": "tests",
    "test_commit.py": "tests",
    "test_minigit_cli.py": "tests",
    "test_complete_flow.py": "tests",
}

def ensure_structure():
    for folder, files in structure.items():
        os.makedirs(folder, exist_ok=True)
        for file in files:
            file_path = os.path.join(folder, file)
            dir_path = os.path.dirname(file_path)
            if dir_path and not os.path.exists(dir_path):
                os.makedirs(dir_path, exist_ok=True)
            if not os.path.exists(file_path):
                with open(file_path, "w", encoding="utf-8") as f:
                    pass  # Crea archivos vacíos si no existen

def move_existing_files():
    for filename, target_folder in move_files.items():
        if os.path.exists(filename):
            shutil.move(filename, os.path.join(target_folder, filename))

def main():
    ensure_structure()
    move_existing_files()
    print("✅ Proyecto reorganizado según la nueva estructura.")

if __name__ == "__main__":
    main()