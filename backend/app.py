# ===============================
# Mini-Git Web API principal
# ---------------------------
# Este archivo implementa la API RESTful de Mini-Git usando FastAPI.
# Permite inicializar, consultar estado, agregar/eliminar archivos, hacer commit,
# ver historial, obtener diffs y gestionar el área de staging, integrando el core Python.
# Cada endpoint está documentado para máxima comprensión.
#
# Dependencias: fastapi, uvicorn, pydantic, core/
# Estructura: utiliza modelos Pydantic para validación y clases adaptadoras para el core.
# ===============================

# Requiere: fastapi, uvicorn, pydantic
# Requisitos:
# - Python 3.7+

import sys
import os
import json
from datetime import datetime
import hashlib
from typing import List, Dict, Any, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List

# Añadir el directorio padre al PATH para importar core/
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Importar las clases existentes del proyecto
from core.repository import Repository
from core.commit import Commit
# Importar WebRepository para funcionalidades avanzadas
from backend.minigit_core import WebRepository


# Inicializar la aplicación FastAPI
app = FastAPI(title="Mini-Git Web API", version="1.0.0")

# Middleware CORS para permitir peticiones desde cualquier origen (desarrollo)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir archivos estáticos del frontend (HTML, JS, CSS)
FRONTEND_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend'))
app.mount("/static", StaticFiles(directory=os.path.join(FRONTEND_PATH)), name="static")

# Endpoint raíz: sirve el index.html del frontend
@app.get("/")
async def root():
    """Devuelve la página principal del frontend web."""
    return FileResponse(os.path.join(FRONTEND_PATH, "index.html"))

# ===============================
# Modelos Pydantic para validación de datos
# ===============================
class FileModel(BaseModel):
    """Modelo para archivos enviados/recibidos por la API."""
    name: str
    content: str

class CommitModel(BaseModel):
    """Modelo para datos de commit enviados por el frontend."""
    message: str
    files: Optional[List[str]] = []

class StatusResponse(BaseModel):
    """Modelo de respuesta para el estado del repositorio."""
    initialized: bool
    current_branch: str
    total_commits: int
    staged_files: List[str]
    working_directory: str

# ===============================
# Clase adaptadora para el core Mini-Git
# ===============================
class MiniGitCore:
    """
    Adaptador para operaciones principales del repositorio Mini-Git.
    Integra el core Python y gestiona archivos de control y staging.
    """
    def __init__(self, repo_path: str = "./mini_git_repo"):
        self.repo_path = repo_path
        self.repo_file = os.path.join(repo_path, ".mingit", "repository.json")
        self.commits_dir = os.path.join(repo_path, ".mingit", "commits")
    
    def init_repository(self) -> Dict[str, Any]:
        """
        Inicializa un repositorio Mini-Git en el directorio dado.
        Crea carpetas y archivos de control si no existen.
        Retorna dict con éxito y mensaje.
        """
        try:
            os.makedirs(self.repo_path, exist_ok=True)
            os.makedirs(os.path.dirname(self.repo_file), exist_ok=True)
            os.makedirs(self.commits_dir, exist_ok=True)
            # Inicializa la estructura del core (.mygit)
            repo = Repository(self.repo_path)
            repo.init()
            # Crear repository.json si no existe
            if not os.path.exists(self.repo_file):
                repo_data = {
                    "current_branch": "main",
                    "staged_files": [],
                    "last_commit": None
                }
                with open(self.repo_file, 'w') as f:
                    json.dump(repo_data, f, indent=2)
            return {
                "success": True, 
                "message": "Repositorio inicializado correctamente",
                "path": self.repo_path
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error al inicializar: {str(e)}")

    def get_status(self) -> StatusResponse:
        """
        Devuelve el estado actual del repositorio: si está inicializado, branch, commits, archivos staged, etc.
        """
        try:
            if not os.path.exists(self.repo_file):
                return StatusResponse(
                    initialized=False,
                    current_branch="main",
                    total_commits=0,
                    staged_files=[],
                    working_directory=self.repo_path
                )
            with open(self.repo_file, 'r') as f:
                repo_data = json.load(f)
            commits_count = 0
            if os.path.exists(self.commits_dir):
                commits_count = len([f for f in os.listdir(self.commits_dir) if f.endswith('.json')])
            staged_files = repo_data.get('staged_files', [])
            return StatusResponse(
                initialized=True,
                current_branch=repo_data.get('current_branch', 'main'),
                total_commits=commits_count,
                staged_files=staged_files,
                working_directory=self.repo_path
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error al obtener estado: {str(e)}")
    
    def add_files(self, files: List[FileModel]) -> Dict[str, Any]:
        """
        Añade archivos al área de staging y los guarda físicamente en el repo.
        Actualiza el archivo de control para reflejar el staging.
        """
        try:
            created_files = []
            repo = Repository(self.repo_path)
            for file_data in files:
                file_path = os.path.join(self.repo_path, file_data.name)
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(file_data.content)
                created_files.append(file_data.name)
                # Agregar al staging del core
                repo.add_file(file_data.name)
            # Actualizar repository.json (opcional, para mantener compatibilidad)
            if os.path.exists(self.repo_file):
                with open(self.repo_file, 'r') as f:
                    repo_data = json.load(f)
                staged_files = repo_data.get('staged_files', [])
                for file_name in created_files:
                    if file_name not in staged_files:
                        staged_files.append(file_name)
                repo_data['staged_files'] = staged_files
                with open(self.repo_file, 'w') as f:
                    json.dump(repo_data, f, indent=2)
            return {
                "success": True,
                "message": f"Archivos añadidos: {', '.join(created_files)}",
                "files": created_files
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error al añadir archivos: {str(e)}")
    
    def create_commit(self, message: str, files: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Crea un nuevo commit usando la lógica del core.
        Limpia el área de staging tras el commit.
        """
        try:
            repo = Repository(self.repo_path)
            commit = Commit(repo)
            commit_hash = commit.create(message)
            # Limpiar staged_files en repository.json
            if os.path.exists(self.repo_file):
                with open(self.repo_file, 'r') as f:
                    repo_data = json.load(f)
                repo_data['last_commit'] = commit_hash
                repo_data['staged_files'] = []
                with open(self.repo_file, 'w') as f:
                    json.dump(repo_data, f, indent=2)
            return {
                "success": True,
                "message": "Commit creado exitosamente",
                "commit_hash": commit_hash
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error al crear commit: {str(e)}")
    
    def get_commit_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Devuelve el historial de commits (ordenados por fecha descendente).
        """
        try:
            repo = Repository(self.repo_path)
            commits = repo.get_commits()
            # Ordenar por timestamp descendente
            commits = sorted(commits, key=lambda c: c.get('timestamp', ''), reverse=True)
            return commits[:limit]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error al obtener historial: {str(e)}")

# Instancia global del core y del adaptador avanzado para funcionalidades extra
mini_git = MiniGitCore()
web_repo = WebRepository("./mini_git_repo")

# ===============================
# ENDPOINTS PRINCIPALES DE LA API
# ===============================

@app.post("/api/init")
async def init_repository():
    """Inicializa el repositorio Mini-Git (estructura y archivos de control)."""
    return mini_git.init_repository()

@app.get("/api/status")
async def get_status():
    """Devuelve el estado actual del repositorio (branch, commits, archivos staged, etc)."""
    return mini_git.get_status()

@app.post("/api/add")
async def add_files(files: List[FileModel]):
    """Agrega archivos al repositorio y los añade al área de staging."""
    return mini_git.add_files(files)

@app.post("/api/commit")
async def create_commit(commit_data: CommitModel):
    """Crea un nuevo commit con los archivos staged."""
    return mini_git.create_commit(commit_data.message, commit_data.files)

@app.get("/api/log")
async def get_commit_history(limit: int = 10):
    """Devuelve el historial de commits (limit configurable)."""
    return mini_git.get_commit_history(limit)

@app.get("/api/commit/{commit_hash}")
async def get_commit_details(commit_hash: str):
    """
    Devuelve los detalles de un commit específico (por hash).
    Retorna error 404 si no existe.
    """
    try:
        commit_file = os.path.join(mini_git.commits_dir, f"{commit_hash}.json")
        if not os.path.exists(commit_file):
            raise HTTPException(status_code=404, detail="Commit no encontrado")
        with open(commit_file, 'r') as f:
            return json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener commit: {str(e)}")

@app.get("/api/files")
async def list_files():
    """
    Lista todos los archivos de usuario en el repositorio (excluye carpetas y archivos ocultos/configuración).
    """
    try:
        files = []
        for root, dirs, filenames in os.walk(mini_git.repo_path):
            # Excluir carpetas ocultas
            dirs[:] = [d for d in dirs if not d.startswith('.') and not d.startswith('__')]
            for filename in filenames:
                # Excluir archivos ocultos y de configuración
                if filename.startswith('.') or filename.endswith('.json'):
                    continue
                file_path = os.path.join(root, filename)
                rel_path = os.path.relpath(file_path, mini_git.repo_path)
                files.append(rel_path)
        return {"files": files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al listar archivos: {str(e)}")

@app.get("/api/file/{file_path:path}")
async def get_file_content(file_path: str):
    """
    Devuelve el contenido de un archivo dado su path relativo al repo.
    Retorna error 404 si no existe.
    """
    try:
        full_path = os.path.join(mini_git.repo_path, file_path)
        if not os.path.exists(full_path) or not os.path.isfile(full_path):
            raise HTTPException(status_code=404, detail="Archivo no encontrado")
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return {"name": file_path, "content": content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al leer archivo: {str(e)}")

@app.delete("/api/file/{file_path:path}")
async def delete_file(file_path: str):
    """
    Elimina un archivo del repositorio y lo quita del área de staging si corresponde.
    Retorna error 404 si no existe.
    """
    import os
    from core.repository import Repository
    repo_path = mini_git.repo_path
    abs_path = os.path.join(repo_path, file_path)
    if not os.path.exists(abs_path):
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    try:
        os.remove(abs_path)
        # Quitar del staging si está
        repo = Repository(repo_path)
        try:
            repo.remove_file_from_staging(file_path)
        except Exception:
            pass
        return {"success": True, "message": f"Archivo eliminado: {file_path}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al eliminar archivo: {str(e)}")

@app.get("/api/diff/{file_path:path}")
async def get_file_diff(file_path: str):
    """
    Devuelve el diff entre el archivo actual y la última versión commiteada.
    Retorna error 404 si no se puede obtener el diff.
    """
    result = web_repo.get_file_diff(file_path)
    if not result.get('success', False):
        raise HTTPException(status_code=404, detail=result.get('error', 'No se pudo obtener el diff'))
    return result

@app.post("/api/stage/{file_path:path}")
async def stage_file(file_path: str):
    """
    Agrega un archivo al área de staging (granular).
    Retorna error 400 si falla.
    """
    result = web_repo.stage_file(file_path)
    if not result.get('success', False):
        raise HTTPException(status_code=400, detail=result.get('error', 'No se pudo agregar al staging'))
    return result

@app.post("/api/unstage/{file_path:path}")
async def unstage_file(file_path: str):
    """
    Quita un archivo del área de staging (granular).
    Retorna error 400 si falla.
    """
    result = web_repo.unstage_file(file_path)
    if not result.get('success', False):
        raise HTTPException(status_code=400, detail=result.get('error', 'No se pudo quitar del staging'))
    return result

# ===============================
# Ejecución directa para desarrollo
# ===============================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
# ===============================
# FIN DEL ARCHIVO PRINCIPAL DE BACKEND
# ===============================