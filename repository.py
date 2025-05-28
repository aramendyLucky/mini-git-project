import os
import json
import hashlib
from datetime import datetime
from pathlib import Path

class Repository:
    """
    Clase principal que maneja el repositorio de nuestro mini-Git.
    Se encarga de crear, configurar y gestionar el repositorio.
    """
    
    def __init__(self, path="."):
        """
        Inicializa el repositorio en la ruta especificada.
        
        Args:
            path (str): Ruta donde está el repositorio (por defecto carpeta actual)
        """
        self.path = Path(path).resolve()  # Ruta absoluta del proyecto
        self.mygit_path = self.path / ".mygit"  # Carpeta .mygit
        self.objects_path = self.mygit_path / "objects"  # Carpeta objects
        
        # Archivos de configuración
        self.config_file = self.mygit_path / "config.json"
        self.staging_file = self.mygit_path / "staging.json" 
        self.commits_file = self.mygit_path / "commits.json"
    
    def init(self):
        """
        Inicializa un nuevo repositorio (como 'git init').
        Crea la estructura de carpetas y archivos necesarios.
        """
        # Verificar si ya existe un repositorio
        if self.mygit_path.exists():
            print(f"Ya existe un repositorio en {self.path}")
            return False
        
        # Crear carpeta .mygit y subcarpetas
        self.mygit_path.mkdir(exist_ok=True)
        self.objects_path.mkdir(exist_ok=True)
        
        # Crear archivo de configuración inicial
        config_data = {
            "name": self.path.name,
            "created": datetime.now().isoformat(),
            "last_commit": None
        }
        self._save_json(self.config_file, config_data)
        
        # Crear archivo de staging vacío
        staging_data = {
            "files": [],
            "timestamp": None
        }
        self._save_json(self.staging_file, staging_data)
        
        # Crear archivo de commits vacío
        self._save_json(self.commits_file, [])
        
        print(f"Repositorio inicializado en {self.path}")
        return True
    
    def is_repository(self):
        """
        Verifica si la carpeta actual es un repositorio válido.
        
        Returns:
            bool: True si es un repositorio, False si no
        """
        return (self.mygit_path.exists() and 
                self.config_file.exists() and
                self.staging_file.exists() and
                self.commits_file.exists())
    
    def get_config(self):
        """
        Obtiene la configuración del repositorio.
        
        Returns:
            dict: Configuración del repositorio
        """
        if not self.is_repository():
            raise Exception("No es un repositorio válido. Ejecuta 'init' primero.")
        
        return self._load_json(self.config_file)
    
    def get_staging(self):
        """
        Obtiene los archivos en el área de staging.
        
        Returns:
            dict: Archivos en staging
        """
        if not self.is_repository():
            raise Exception("No es un repositorio válido. Ejecuta 'init' primero.")
        
        return self._load_json(self.staging_file)
    
    def get_commits(self):
        """
        Obtiene la lista de todos los commits.
        
        Returns:
            list: Lista de commits
        """
        if not self.is_repository():
            raise Exception("No es un repositorio válido. Ejecuta 'init' primero.")
        
        return self._load_json(self.commits_file)
    
    def _save_json(self, file_path, data):
        """
        Guarda datos en formato JSON.
        
        Args:
            file_path (Path): Ruta del archivo
            data: Datos a guardar
        """
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _load_json(self, file_path):
        """
        Carga datos desde un archivo JSON.
        
        Args:
            file_path (Path): Ruta del archivo
            
        Returns:
            dict/list: Datos cargados
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def add_file(self, file_path):
        """
        Agrega un archivo al staging area (como 'git add archivo.py').
        
        El staging area es donde preparamos archivos antes del commit.
        
        Args:
            file_path (str): Ruta del archivo a agregar
            
        Returns:
            bool: True si se agregó correctamente
        """
        if not self.is_repository():
            raise Exception("No es un repositorio válido. Ejecuta 'init' primero.")
        
        # Convertir a Path para manejo más fácil
        file_path = str(file_path).replace("\\", "/")  # Normalizar barras
        full_path = self.path / file_path
        
        # Verificar que el archivo existe
        if not full_path.exists():
            raise Exception(f"Archivo no encontrado: {file_path}")
        
        # Verificar que el archivo está dentro del repositorio
        try:
            full_path.resolve().relative_to(self.path.resolve())
        except ValueError:
            raise Exception(f"El archivo debe estar dentro del repositorio: {file_path}")
        
        # Obtener staging actual
        staging_data = self.get_staging()
        
        # Agregar archivo si no está ya en staging
        if file_path not in staging_data["files"]:
            staging_data["files"].append(file_path)
            staging_data["timestamp"] = datetime.now().isoformat()
            
            # Guardar staging actualizado
            self._save_json(self.staging_file, staging_data)
            
            print(f"✅ Archivo agregado al staging: {file_path}")
            return True
        else:
            print(f"📋 Archivo ya está en staging: {file_path}")
            return True
    
    def remove_file_from_staging(self, file_path):
        """
        Remueve un archivo del staging area (como 'git reset archivo.py').
        
        Args:
            file_path (str): Ruta del archivo a remover
            
        Returns:
            bool: True si se removió correctamente
        """
        if not self.is_repository():
            raise Exception("No es un repositorio válido. Ejecuta 'init' primero.")
        
        # Normalizar ruta
        file_path = str(file_path).replace("\\", "/")
        
        # Obtener staging actual
        staging_data = self.get_staging()
        
        # Remover archivo si está en staging
        if file_path in staging_data["files"]:
            staging_data["files"].remove(file_path)
            staging_data["timestamp"] = datetime.now().isoformat() if staging_data["files"] else None
            
            # Guardar staging actualizado
            self._save_json(self.staging_file, staging_data)
            
            print(f"🗑️ Archivo removido del staging: {file_path}")
            return True
        else:
            print(f"❌ Archivo no está en staging: {file_path}")
            return False
    
    def status(self):
        """
        Muestra el estado del repositorio (como 'git status').
        
        Muestra:
        - Archivos en staging area
        - Archivos modificados no agregados
        - Último commit
        """
        if not self.is_repository():
            raise Exception("No es un repositorio válido. Ejecuta 'init' primero.")
        
        print("📊 Estado del repositorio:")
        print("=" * 40)
        
        # Información del último commit
        config = self.get_config()
        if config["last_commit"]:
            print(f"📌 Último commit: {config['last_commit'][:8]}...")
        else:
            print("📌 Último commit: (ninguno)")
        
        # Archivos en staging
        staging_data = self.get_staging()
        staged_files = staging_data["files"]
        
        if staged_files:
            print(f"\n✅ Archivos en staging ({len(staged_files)}):")
            for file_path in staged_files:
                print(f"  📁 {file_path}")
        else:
            print("\n📭 No hay archivos en staging")
        
        # Información adicional
        if staging_data["timestamp"]:
            print(f"\n🕐 Última modificación del staging: {staging_data['timestamp']}")
        
        print("\n💡 Comandos disponibles:")
        print("  - add_file('archivo.py') : agregar archivo al staging")
        print("  - remove_file_from_staging('archivo.py') : remover del staging")
        print("  - commit.create('mensaje') : crear commit")
    
    def calculate_file_hash(self, file_path):
        """
        Calcula el hash SHA-1 de un archivo.
        
        Args:
            file_path (str): Ruta del archivo
            
        Returns:
            str: Hash SHA-1 del archivo
        """
        sha1 = hashlib.sha1()
        
        try:
            with open(file_path, 'rb') as f:
                # Leer el archivo en chunks para archivos grandes
                for chunk in iter(lambda: f.read(4096), b""):
                    sha1.update(chunk)
            return sha1.hexdigest()
        except FileNotFoundError:
            raise Exception(f"Archivo no encontrado: {file_path}")
        except Exception as e:
            raise Exception(f"Error al leer archivo {file_path}: {e}")


# Ejemplo de uso básico (para testing)
if __name__ == "__main__":
    # Crear instancia del repositorio
    repo = Repository()
    
    # Inicializar repositorio
    repo.init()
    
    # Verificar que es un repositorio válido
    print(f"¿Es repositorio válido? {repo.is_repository()}")
    
    # Mostrar configuración
    config = repo.get_config()
    print(f"Configuración: {config}")