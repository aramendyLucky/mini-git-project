import os
import json
import hashlib
import shutil
from datetime import datetime
from pathlib import Path

class Commit:
    """
    Clase que maneja la creación y gestión de commits.
    
    Un commit es como una "fotografía" de tu proyecto en un momento específico.
    Esta clase se encarga de:
    1. Tomar archivos del staging area
    2. Guardar su contenido de forma permanente  
    3. Crear un registro del commit
    4. Mantener el historial
    """
    
    def __init__(self, repository):
        """
        Inicializa el manejador de commits.
        
        Args:
            repository: Instancia de la clase Repository
        """
        # Guardamos referencia al repositorio para acceder a sus métodos y rutas
        self.repo = repository
        
        # Verificamos que sea un repositorio válido antes de continuar
        if not self.repo.is_repository():
            raise Exception("No es un repositorio válido. Ejecuta 'init' primero.")
    
    def create(self, message):
        """
        Crea un nuevo commit con los archivos del staging area.
        
        Este es el método principal - como hacer 'git commit -m "mensaje"'
        
        Args:
            message (str): Mensaje descriptivo del commit
            
        Returns:
            str: ID (hash) del commit creado
        """
        # 1. VALIDAR que tenemos un mensaje
        if not message or not message.strip():
            raise Exception("El mensaje del commit no puede estar vacío")
        
        message = message.strip()  # Limpiar espacios extra
        
        # 2. OBTENER archivos del staging area
        print("📋 Obteniendo archivos del staging area...")
        staging_data = self.repo.get_staging()
        staged_files = staging_data.get("files", [])
        
        # Verificar que hay archivos para commitear
        if not staged_files:
            raise Exception("No hay archivos en staging. Usa 'add' primero.")
        
        print(f"📁 Archivos a commitear: {staged_files}")
        
        # 3. PROCESAR cada archivo del staging
        commit_files = {}  # Diccionario: {"archivo.py": "hash_contenido"}
        
        for file_path in staged_files:
            print(f"🔄 Procesando: {file_path}")
            
            # Verificar que el archivo existe
            full_path = self.repo.path / file_path
            if not full_path.exists():
                raise Exception(f"Archivo no encontrado: {file_path}")
            
            # Calcular hash del contenido del archivo
            content_hash = self.repo.calculate_file_hash(full_path)
            
            # Guardar el contenido del archivo en /objects
            self._save_file_to_objects(full_path, content_hash)
            
            # Agregar al diccionario del commit
            commit_files[file_path] = content_hash
            
            print(f"✅ {file_path} -> {content_hash[:8]}...")
        
        # 4. CREAR el objeto commit
        commit_data = self._create_commit_object(message, commit_files)
        
        # 5. CALCULAR hash único del commit
        commit_hash = self._calculate_commit_hash(commit_data)
        commit_data["id"] = commit_hash
        
        print(f"🆔 ID del commit: {commit_hash}")
        
        # 6. GUARDAR commit en el historial
        self._add_commit_to_history(commit_data)
        
        # 7. ACTUALIZAR configuración del repositorio
        self._update_last_commit(commit_hash)
        
        # 8. LIMPIAR staging area (los archivos ya están commiteados)
        self._clear_staging()
        
        print(f"🎉 Commit '{message}' creado exitosamente!")
        return commit_hash
    
    def _create_commit_object(self, message, files):
        """
        Crea el objeto de datos del commit.
        
        Args:
            message (str): Mensaje del commit
            files (dict): Diccionario {archivo: hash_contenido}
            
        Returns:
            dict: Objeto commit con toda la metadata
        """
        # Obtener el commit padre (el último commit)
        last_commit = self._get_last_commit_id()
        
        # Crear objeto commit con toda la información
        commit_data = {
            "id": None,  # Se calculará después
            "message": message,
            "timestamp": datetime.now().isoformat(),  # Fecha/hora actual
            "parent": last_commit,  # Commit del que viene (puede ser None)
            "files": files,  # Diccionario de archivos y sus hashes
            "author": "user"  # Por ahora hardcodeado (opcional: mejorar después)
        }
        
        return commit_data
    
    def _calculate_commit_hash(self, commit_data):
        """
        Calcula el hash SHA-1 único del commit.
        
        El hash se basa en TODO el contenido del commit:
        - Mensaje
        - Timestamp  
        - Archivos incluidos
        - Commit padre
        
        Args:
            commit_data (dict): Datos del commit
            
        Returns:  
            str: Hash SHA-1 del commit
        """
        # Crear string con toda la información del commit
        # (sin incluir el ID que aún no existe)
        commit_string = f"{commit_data['message']}" \
                       f"{commit_data['timestamp']}" \
                       f"{commit_data['parent']}" \
                       f"{json.dumps(commit_data['files'], sort_keys=True)}"
        
        # Calcular SHA-1 del string completo
        sha1 = hashlib.sha1()
        sha1.update(commit_string.encode('utf-8'))
        return sha1.hexdigest()
    
    def _save_file_to_objects(self, file_path, content_hash):
        """
        Guarda el contenido del archivo en la carpeta objects/.
        
        En Git, los archivos se guardan por su hash. Si dos archivos
        tienen el mismo contenido, solo se guarda una copia.
        
        Args:
            file_path (Path): Ruta al archivo original
            content_hash (str): Hash del contenido
        """
        # Ruta donde guardar el archivo en objects/
        object_file = self.repo.objects_path / content_hash
        
        # Si ya existe un archivo con ese hash, no lo duplicamos
        if object_file.exists():
            print(f"📋 Contenido ya existe: {content_hash[:8]}...")
            return
        
        # Copiar el archivo original a objects/ con nombre = hash
        try:
            shutil.copy2(file_path, object_file)
            print(f"💾 Guardado en objects: {content_hash[:8]}...")
        except Exception as e:
            raise Exception(f"Error al guardar {file_path}: {e}")
    
    def _add_commit_to_history(self, commit_data):
        """
        Agrega el commit al historial (archivo commits.json).
        
        Args:
            commit_data (dict): Datos completos del commit
        """
        # Obtener historial actual
        commits = self.repo.get_commits()
        
        # Agregar nuevo commit al final de la lista
        commits.append(commit_data)
        
        # Guardar historial actualizado
        self.repo._save_json(self.repo.commits_file, commits)
        
        print(f"📚 Commit agregado al historial (total: {len(commits)})")
    
    def _update_last_commit(self, commit_hash):
        """
        Actualiza la configuración con el último commit.
        
        Args:
            commit_hash (str): Hash del commit recién creado
        """
        # Obtener configuración actual
        config = self.repo.get_config()
        
        # Actualizar último commit
        config["last_commit"] = commit_hash
        
        # Guardar configuración actualizada
        self.repo._save_json(self.repo.config_file, config)
    
    def _clear_staging(self):
        """
        Limpia el staging area después de hacer commit.
        
        Una vez que los archivos están commiteados, 
        el staging area vuelve a estar vacío.
        """
        staging_data = {
            "files": [],
            "timestamp": None
        }
        
        self.repo._save_json(self.repo.staging_file, staging_data)
        print("🧹 Staging area limpiada")
    
    def _get_last_commit_id(self):
        """
        Obtiene el ID del último commit (commit padre).
        
        Returns:
            str or None: Hash del último commit, o None si es el primer commit
        """
        config = self.repo.get_config()
        return config.get("last_commit")
    
    def get_commit_by_id(self, commit_id):
        """
        Busca un commit específico por su ID.
        
        Args:
            commit_id (str): Hash del commit a buscar
            
        Returns:
            dict or None: Datos del commit si se encuentra
        """
        commits = self.repo.get_commits()
        
        # Buscar en la lista de commits
        for commit in commits:
            if commit["id"] == commit_id:
                return commit
        
        return None
    
    def get_history(self, limit=None):
        """
        Obtiene el historial de commits (como 'git log').
        
        Args:
            limit (int, optional): Número máximo de commits a retornar
            
        Returns:
            list: Lista de commits ordenados del más reciente al más antiguo
        """
        commits = self.repo.get_commits()
        
        # Ordenar por timestamp (más reciente primero)
        sorted_commits = sorted(commits, 
                               key=lambda x: x["timestamp"], 
                               reverse=True)
        
        # Aplicar límite si se especifica
        if limit:
            sorted_commits = sorted_commits[:limit]
        
        return sorted_commits
    
    def show_log(self, limit=5):
        """
        Muestra el historial de commits de forma legible (como 'git log').
        
        Args:
            limit (int): Número de commits a mostrar
        """
        commits = self.get_history(limit)
        
        if not commits:
            print("📭 No hay commits en el historial")
            return
        
        print(f"📚 Historial de commits (últimos {len(commits)}):")
        print("=" * 60)
        
        for commit in commits:
            print(f"🆔 Commit: {commit['id']}")
            print(f"📝 Mensaje: {commit['message']}")  
            print(f"📅 Fecha: {commit['timestamp']}")
            print(f"👤 Autor: {commit.get('author', 'unknown')}")
            
            if commit['parent']:
                print(f"⬆️  Padre: {commit['parent'][:8]}...")
            else:
                print("⬆️  Padre: (commit inicial)")
            
            print(f"📁 Archivos: {list(commit['files'].keys())}")
            print("-" * 40)


# Ejemplo de uso básico (para testing)
if __name__ == "__main__":
    from repository import Repository
    
    # Crear repositorio de prueba
    repo = Repository()
    
    if not repo.is_repository():
        print("Inicializando repositorio...")
        repo.init()
    
    # Crear manejador de commits
    commit_manager = Commit(repo)
    
    print("Clase Commit lista para usar!")
    print("Para hacer commit, primero agrega archivos al staging area")
    