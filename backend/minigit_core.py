# ===============================
# minigit_core.py - Lógica avanzada Mini-Git para Web
# ---------------------------------------------------
# Este archivo implementa la lógica extendida de Mini-Git para la interfaz web.
# Provee clases y métodos para snapshots, commits, staging granular, diff, historial,
# y operaciones tipo Git, integrando con el backend FastAPI.
# Cada clase y método está documentado para máxima comprensión.
#
# Usado por: backend/app.py (API REST)
# Dependencias: Python 3.7+, dataclasses, difflib, os, json
# ===============================

# minigit_core.py - Core logic adaptado para la web interface
import os
import json
import hashlib
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
import difflib

@dataclass
class FileSnapshot:
    """
    Representa un snapshot (captura) de un archivo en un momento dado.
    Incluye nombre relativo, contenido, hash, tamaño y fecha de modificación.
    """
    name: str
    content: str
    hash: str
    size: int
    modified: str
    
    @classmethod
    def from_file(cls, file_path: str, base_path: str = ""):
        """
        Crea un snapshot a partir de un archivo físico.
        Calcula hash, tamaño y fecha de modificación.
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()[:8]
        stat = os.stat(file_path)
        relative_name = os.path.relpath(file_path, base_path) if base_path else os.path.basename(file_path)
        return cls(
            name=relative_name,
            content=content,
            hash=content_hash,
            size=stat.st_size,
            modified=datetime.fromtimestamp(stat.st_mtime).isoformat()
        )

@dataclass 
class WebCommit:
    """
    Representa un commit adaptado para la interfaz web.
    Incluye hash, mensaje, autor, timestamp, archivos y commit padre.
    """
    hash: str
    message: str
    author: str
    timestamp: str
    files: List[FileSnapshot]
    parent: Optional[str] = None
    
    def __post_init__(self):
        if not self.hash:
            # Generar hash basado en el contenido del commit
            content = f"{self.message}{self.author}{self.timestamp}"
            for file_snap in self.files:
                content += file_snap.hash
            self.hash = hashlib.sha256(content.encode('utf-8')).hexdigest()[:12]
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convierte el commit a diccionario serializable para JSON.
        """
        return {
            'hash': self.hash,
            'message': self.message,
            'author': self.author,
            'timestamp': self.timestamp,
            'files': [asdict(f) for f in self.files],
            'parent': self.parent
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WebCommit':
        """
        Crea un WebCommit desde un diccionario (por ejemplo, leído de JSON).
        """
        files = [FileSnapshot(**f) for f in data.get('files', [])]
        return cls(
            hash=data['hash'],
            message=data['message'],
            author=data['author'],
            timestamp=data['timestamp'],
            files=files,
            parent=data.get('parent')
        )

class WebRepository:
    """
    Repositorio adaptado para la web con funcionalidades extendidas tipo Git.
    Permite inicializar, hacer staging granular, commits, diffs, historial, etc.
    """
    def __init__(self, path: str = "./mini_git_repo"):
        self.path = path
        self.minigit_dir = os.path.join(path, '.minigit')
        self.config_file = os.path.join(self.minigit_dir, 'config.json')
        self.commits_dir = os.path.join(self.minigit_dir, 'commits')
        self.staging_file = os.path.join(self.minigit_dir, 'staging.json')
        self.refs_dir = os.path.join(self.minigit_dir, 'refs')
    
    def init(self) -> Dict[str, Any]:
        """
        Inicializa la estructura completa del repositorio web (carpetas, config, refs, staging).
        """
        try:
            # Crear directorios necesarios
            os.makedirs(self.path, exist_ok=True)
            os.makedirs(self.minigit_dir, exist_ok=True)
            os.makedirs(self.commits_dir, exist_ok=True)
            os.makedirs(self.refs_dir, exist_ok=True)
            # Configuración inicial
            config = {
                'initialized': True,
                'current_branch': 'main',
                'created_at': datetime.now().isoformat(),
                'version': '1.0.0'
            }
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            # Staging inicial vacío
            staging = {
                'files': {},
                'added': [],
                'modified': [],
                'deleted': []
            }
            with open(self.staging_file, 'w') as f:
                json.dump(staging, f, indent=2)
            # Referencia inicial a main
            main_ref = os.path.join(self.refs_dir, 'main')
            with open(main_ref, 'w') as f:
                f.write('')  # Vacío hasta el primer commit
            return {
                'success': True,
                'message': 'Repositorio inicializado correctamente',
                'path': self.path
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error al inicializar: {str(e)}'
            }
    
    def is_initialized(self) -> bool:
        """
        Verifica si el repositorio ya está inicializado (existe config).
        """
        return os.path.exists(self.config_file)
    
    def get_status(self) -> Dict[str, Any]:
        """
        Devuelve el estado detallado del repositorio: branch, commits, archivos staged, etc.
        """
        if not self.is_initialized():
            return {
                'initialized': False,
                'current_branch': None,
                'total_commits': 0,
                'staged_files': [],
                'working_directory': self.path,
                'clean': True
            }
        try:
            # Leer configuración
            with open(self.config_file, 'r') as f:
                config = json.load(f)
            # Leer staging
            staging_data = {}
            if os.path.exists(self.staging_file):
                with open(self.staging_file, 'r') as f:
                    staging_data = json.load(f)
            # Contar commits
            total_commits = 0
            if os.path.exists(self.commits_dir):
                total_commits = len([f for f in os.listdir(self.commits_dir) if f.endswith('.json')])
            # Detectar archivos modificados en el directorio de trabajo
            working_files = self._scan_working_directory()
            staged_files = staging_data.get('added', [])
            return {
                'initialized': True,
                'current_branch': config.get('current_branch', 'main'),
                'total_commits': total_commits,
                'staged_files': staged_files,
                'working_files': working_files,
                'working_directory': self.path,
                'clean': len(staged_files) == 0 and len(working_files) == 0
            }
        except Exception as e:
            return {
                'initialized': True,
                'error': str(e)
            }
    
    def _scan_working_directory(self) -> List[str]:
        """
        Escanea el directorio de trabajo para encontrar archivos (excluye .minigit).
        """
        files = []
        try:
            for root, dirs, filenames in os.walk(self.path):
                # Ignorar directorio .minigit
                if '.minigit' in root:
                    continue
                for filename in filenames:
                    file_path = os.path.join(root, filename)
                    rel_path = os.path.relpath(file_path, self.path)
                    files.append(rel_path)
        except Exception:
            pass
        return files
    
    def add_files(self, files: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Añade archivos al área de staging y los guarda físicamente en el repo.
        """
        try:
            # Leer staging actual
            staging_data = {'files': {}, 'added': [], 'modified': [], 'deleted': []}
            if os.path.exists(self.staging_file):
                with open(self.staging_file, 'r') as f:
                    staging_data = json.load(f)
            added_files = []
            for file_data in files:
                file_name = file_data['name']
                file_content = file_data['content']
                # Crear archivo en el directorio de trabajo
                file_path = os.path.join(self.path, file_name)
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(file_content)
                # Crear snapshot del archivo
                file_snapshot = FileSnapshot.from_file(file_path, self.path)
                # Añadir al staging
                staging_data['files'][file_name] = asdict(file_snapshot)
                if file_name not in staging_data['added']:
                    staging_data['added'].append(file_name)
                added_files.append(file_name)
            # Guardar staging actualizado
            with open(self.staging_file, 'w') as f:
                json.dump(staging_data, f, indent=2)
            return {
                'success': True,
                'message': f'Archivos añadidos al staging: {", ".join(added_files)}',
                'files': added_files
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error al añadir archivos: {str(e)}'
            }
    
    def commit(self, message: str, author: str = "Usuario Web") -> Dict[str, Any]:
        """
        Crea un nuevo commit con los archivos staged. Limpia el staging tras el commit.
        """
        try:
            if not self.is_initialized():
                return {'success': False, 'message': 'Repositorio no inicializado'}
            # Leer staging
            if not os.path.exists(self.staging_file):
                return {'success': False, 'message': 'No hay archivos en staging'}
            with open(self.staging_file, 'r') as f:
                staging_data = json.load(f)
            staged_files = staging_data.get('added', [])
            if not staged_files:
                return {'success': False, 'message': 'No hay archivos para hacer commit'}
            # Crear snapshots de archivos
            file_snapshots = []
            for file_name in staged_files:
                if file_name in staging_data['files']:
                    file_snapshots.append(FileSnapshot(**staging_data['files'][file_name]))
            # Obtener commit padre
            parent_hash = self._get_last_commit_hash()
            # Crear commit
            commit = WebCommit(
                hash="",  # Se generará automáticamente
                message=message,
                author=author,
                timestamp=datetime.now().isoformat(),
                files=file_snapshots,
                parent=parent_hash
            )
            # Guardar commit
            commit_file = os.path.join(self.commits_dir, f'{commit.hash}.json')
            with open(commit_file, 'w') as f:
                json.dump(commit.to_dict(), f, indent=2)
            # Actualizar referencia de branch
            branch_ref = os.path.join(self.refs_dir, 'main')
            with open(branch_ref, 'w') as f:
                f.write(commit.hash)
            # Limpiar staging
            staging_data = {'files': {}, 'added': [], 'modified': [], 'deleted': []}
            with open(self.staging_file, 'w') as f:
                json.dump(staging_data, f, indent=2)
            return {
                'success': True,
                'message': 'Commit creado exitosamente',
                'commit_hash': commit.hash,
                'files_committed': len(file_snapshots)
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error al crear commit: {str(e)}'
            }
    
    def _get_last_commit_hash(self) -> Optional[str]:
        """
        Devuelve el hash del último commit de la rama principal.
        """
        try:
            main_ref = os.path.join(self.refs_dir, 'main')
            if os.path.exists(main_ref):
                with open(main_ref, 'r') as f:
                    hash_value = f.read().strip()
                    return hash_value if hash_value else None
            return None
        except Exception:
            return None
    
    def get_commit_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Devuelve el historial de commits ordenado por fecha (más reciente primero).
        """
        try:
            if not os.path.exists(self.commits_dir):
                return []
            commits = []
            commit_files = [f for f in os.listdir(self.commits_dir) if f.endswith('.json')]
            # Leer todos los commits
            commit_data = []
            for commit_file in commit_files:
                commit_path = os.path.join(self.commits_dir, commit_file)
                with open(commit_path, 'r') as f:
                    data = json.load(f)
                    commit_data.append(data)
            # Ordenar por timestamp (más reciente primero)
            commit_data.sort(key=lambda x: x['timestamp'], reverse=True)
            # Formatear para la web
            for data in commit_data[:limit]:
                commits.append({
                    'hash': data['hash'],
                    'message': data['message'],
                    'author': data['author'],
                    'timestamp': data['timestamp'],
                    'files_count': len(data.get('files', [])),
                    'parent': data.get('parent')
                })
            return commits
        except Exception as e:
            return []
    
    def get_commit_details(self, commit_hash: str) -> Optional[Dict[str, Any]]:
        """
        Devuelve los detalles completos de un commit dado su hash.
        """
        try:
            commit_file = os.path.join(self.commits_dir, f'{commit_hash}.json')
            if not os.path.exists(commit_file):
                return None
            with open(commit_file, 'r') as f:
                return json.load(f)
        except Exception:
            return None
    
    def get_file_content(self, file_path: str) -> Optional[Dict[str, str]]:
        """
        Devuelve el contenido de un archivo del working directory.
        """
        try:
            full_path = os.path.join(self.path, file_path)
            if not os.path.exists(full_path):
                return None
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return {
                'name': file_path,
                'content': content
            }
        except Exception:
            return None
    
    def get_file_diff(self, file_path: str) -> Dict[str, Any]:
        """
        Devuelve el diff unificado entre el archivo actual y la última versión commiteada.
        """
        try:
            # Leer contenido actual
            full_path = os.path.join(self.path, file_path)
            if not os.path.exists(full_path):
                return { 'success': False, 'error': 'Archivo no existe en el directorio de trabajo' }
            with open(full_path, 'r', encoding='utf-8') as f:
                current_content = f.readlines()
            # Buscar último commit que contenga este archivo
            last_commit_hash = self._get_last_commit_hash()
            prev_content = []
            if last_commit_hash:
                commit_file = os.path.join(self.commits_dir, f'{last_commit_hash}.json')
                if os.path.exists(commit_file):
                    with open(commit_file, 'r', encoding='utf-8') as f:
                        commit_data = json.load(f)
                    for file_snap in commit_data.get('files', []):
                        if file_snap['name'] == file_path:
                            prev_content = file_snap['content'].splitlines(keepends=True)
                            break
            # Calcular diff unificado siempre
            diff = difflib.unified_diff(
                prev_content,
                current_content,
                fromfile=f'{file_path} (commit)',
                tofile=f'{file_path} (actual)',
                lineterm=''
            )
            diff_text = '\n'.join(diff)
            return { 'success': True, 'diff': diff_text }
        except Exception as e:
            return { 'success': False, 'error': str(e) }
    
    def stage_file(self, file_path: str) -> Dict[str, Any]:
        """
        Agrega un archivo al área de staging (como git add archivo).
        """
        try:
            # Leer staging actual
            staging_data = {'files': {}, 'added': [], 'modified': [], 'deleted': []}
            if os.path.exists(self.staging_file):
                with open(self.staging_file, 'r') as f:
                    staging_data = json.load(f)
            # Verificar que el archivo existe
            abs_path = os.path.join(self.path, file_path)
            if not os.path.exists(abs_path):
                return {'success': False, 'error': 'Archivo no encontrado'}
            # Crear snapshot
            from dataclasses import asdict
            file_snapshot = FileSnapshot.from_file(abs_path, self.path)
            staging_data['files'][file_path] = asdict(file_snapshot)
            if file_path not in staging_data['added']:
                staging_data['added'].append(file_path)
            # Guardar staging actualizado
            with open(self.staging_file, 'w') as f:
                json.dump(staging_data, f, indent=2)
            return {'success': True, 'message': f"Archivo '{file_path}' añadido al staging"}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def unstage_file(self, file_path: str) -> Dict[str, Any]:
        """
        Quita un archivo del área de staging (como git reset archivo).
        """
        try:
            # Leer staging actual
            staging_data = {'files': {}, 'added': [], 'modified': [], 'deleted': []}
            if os.path.exists(self.staging_file):
                with open(self.staging_file, 'r') as f:
                    staging_data = json.load(f)
            # Quitar del staging
            if file_path in staging_data['files']:
                del staging_data['files'][file_path]
            if file_path in staging_data['added']:
                staging_data['added'].remove(file_path)
            # Guardar staging actualizado
            with open(self.staging_file, 'w') as f:
                json.dump(staging_data, f, indent=2)
            return {'success': True, 'message': f"Archivo '{file_path}' removido del staging"}
        except Exception as e:
            return {'success': False, 'error': str(e)}
# ===============================
# FIN DEL ARCHIVO PRINCIPAL DE LÓGICA WEB MINIGIT
# ===============================