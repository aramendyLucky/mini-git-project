#!/usr/bin/env python3
"""
Mini-Git: Un sistema de control de versiones simplificado
Uso: python minigit.py <comando> [argumentos]
"""
import base64
import sys
import argparse
import hashlib
import json
import time
from pathlib import Path
from typing import Dict, List, Optional
# Importar clases del core
from core.repository import Repository
from core.commit import Commit



class MiniGit:
    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path).resolve()
        self.git_dir = self.repo_path / ".minigit"
        self.objects_dir = self.git_dir / "objects"
        self.refs_dir = self.git_dir / "refs"
        self.heads_dir = self.refs_dir / "heads"
        self.index_file = self.git_dir / "index"
        self.head_file = self.git_dir / "HEAD"
        
    def init(self) -> bool:
        """Inicializa un nuevo repositorio"""
        try:
            if self.git_dir.exists():
                print(f"❌ El repositorio ya existe en {self.git_dir}")
                return False
                
            # Crear estructura de directorios
            self.git_dir.mkdir()
            self.objects_dir.mkdir()
            self.refs_dir.mkdir()
            self.heads_dir.mkdir()
            
            # Crear archivos iniciales
            self.index_file.write_text("[]")
            self.head_file.write_text("ref: refs/heads/main")
            
            print(f"✅ Repositorio inicializado en {self.git_dir}")
            return True
            
        except Exception as e:
            print(f"❌ Error al inicializar: {e}")
            return False
    
    def _check_repo(self) -> bool:
        """Verifica si estamos en un repositorio válido"""
        if not self.git_dir.exists():
            print("❌ No estás en un repositorio Mini-Git. Ejecuta 'minigit init' primero.")
            return False
        return True
    
    def _hash_content(self, content: str) -> str:
        """Genera hash SHA-1 del contenido"""
        return hashlib.sha1(content.encode()).hexdigest()
    
    def _save_object(self, content: str) -> str:
        """Guarda un objeto y retorna su hash"""
        hash_obj = self._hash_content(content)
        obj_path = self.objects_dir / hash_obj
        obj_path.write_text(content)
        return hash_obj
    
    def _load_object(self, hash_obj: str) -> Optional[str]:
        """Carga un objeto por su hash"""
        obj_path = self.objects_dir / hash_obj
        if obj_path.exists():
            return obj_path.read_text()
        return None
    
    def _load_index(self) -> List[Dict]:
        """Carga el índice (staging area)"""
        if self.index_file.exists():
            return json.loads(self.index_file.read_text())
        return []
    
    def _save_index(self, index: List[Dict]):
        """Guarda el índice"""
        self.index_file.write_text(json.dumps(index, indent=2))
    
    def add(self, files: List[str]) -> bool:
        """Añade archivos al staging area (soporta binarios y texto)"""
        if not self._check_repo():
            return False
        
        index = self._load_index()
        added_files = []
        
        for file_path in files:
            path = Path(file_path).resolve()
            print(f"DEBUG: path={path}, repo_path={self.repo_path}")
            
            if not path.exists():
                print(f"❌ Archivo no encontrado: {file_path}")
                continue
                
            if not path.is_file():
                print(f"❌ No es un archivo: {file_path}")
                continue
            
            # Leer contenido del archivo en binario y codificar en base64
            try:
                content_bytes = path.read_bytes()
                content_b64 = base64.b64encode(content_bytes).decode('ascii')
            except Exception:
                print(f"❌ No se puede leer {file_path}")
                continue
            
            # Guardar como objeto
            hash_obj = self._save_object(content_b64)
            
            # Actualizar índice
            try:
                rel_path = str(path.relative_to(self.repo_path)).replace("\\", "/")
            except ValueError:
                print(f"❌ El archivo {file_path} debe estar dentro del repositorio ({self.repo_path})")
                continue
            
            # Remover entrada existente si existe
            index = [item for item in index if item['path'] != rel_path]
            
            # Añadir nueva entrada
            index.append({
                'path': rel_path,
                'hash': hash_obj,
                'timestamp': time.time()
            })
            
            added_files.append(rel_path)
        
        if added_files:
            self._save_index(index)
            print(f"✅ Archivos añadidos: {', '.join(added_files)}")
            return True
        else:
            print("❌ No se añadieron archivos")
            return False

    def status(self):
        """Muestra el estado del repositorio"""
        if not self._check_repo():
            return
            
        print("📊 Estado del repositorio:")
        print("-" * 30)
        
        # Mostrar branch actual
        if self.head_file.exists():
            head_ref = self.head_file.read_text().strip()
            if head_ref.startswith("ref: "):
                branch = head_ref.split("/")[-1]
                print(f"🌿 Branch actual: {branch}")
            else:
                print(f"🔍 HEAD detached: {head_ref[:8]}")
        
        # Mostrar archivos en staging
        index = self._load_index()
        if index:
            print(f"\n📦 Archivos en staging ({len(index)}):")
            for item in index:
                print(f"   ✅ {item['path']}")
        else:
            print("\n📦 No hay archivos en staging")
        
        # Mostrar archivos modificados (simplificado)
        print(f"\n📁 Directorio de trabajo: {self.repo_path}")

    def commit(self, message: str) -> bool:
        """Crea un commit con los archivos en staging"""
        if not self._check_repo():
            return False
            
        index = self._load_index()
        if not index:
            print("❌ No hay cambios para commitear. Usa 'minigit add' primero.")
            return False
        
        # Crear objeto commit
        commit_data = {
            'message': message,
            'timestamp': time.time(),
            'files': index,
            'parent': self._get_current_commit()
        }
        
        commit_json = json.dumps(commit_data, indent=2)
        commit_hash = self._save_object(commit_json)
        
        # Actualizar referencia del branch
        head_ref = self.head_file.read_text().strip()
        if head_ref.startswith("ref: "):
            branch_path = self.git_dir / head_ref[5:]  # Remove "ref: "
            branch_path.parent.mkdir(parents=True, exist_ok=True)
            branch_path.write_text(commit_hash)
        
        # Limpiar staging area
        self._save_index([])
        
        print(f"✅ Commit creado: {commit_hash[:8]}")
        print(f"📝 Mensaje: {message}")
        print(f"📊 Archivos: {len(index)}")
        
        return True
    
    def _get_current_commit(self) -> Optional[str]:
        """Obtiene el hash del commit actual"""
        if not self.head_file.exists():
            return None
            
        head_ref = self.head_file.read_text().strip()
        if head_ref.startswith("ref: "):
            branch_path = self.git_dir / head_ref[5:]
            if branch_path.exists():
                return branch_path.read_text().strip()
        else:
            return head_ref
        
        return None
    
    def log(self, limit: int = 10):
        """Muestra el historial de commits"""
        if not self._check_repo():
            return
            
        current_hash = self._get_current_commit()
        if not current_hash:
            print("📝 No hay commits aún")
            return
        
        print("📚 Historial de commits:")
        print("=" * 50)
        
        count = 0
        while current_hash and count < limit:
            commit_data = self._load_object(current_hash)
            if not commit_data:
                break
                
            try:
                commit = json.loads(commit_data)
                timestamp = time.strftime('%Y-%m-%d %H:%M:%S', 
                                        time.localtime(commit['timestamp']))
                
                print(f"🔸 Commit: {current_hash[:8]}")
                print(f"📅 Fecha: {timestamp}")
                print(f"💬 Mensaje: {commit['message']}")
                print(f"📊 Archivos: {len(commit['files'])}")
                
                for file_info in commit['files']:
                    print(f"   📄 {file_info['path']}")
                
                print("-" * 30)
                
                current_hash = commit.get('parent')
                count += 1
                
            except json.JSONDecodeError:
                break
    
    def show(self, commit_hash: Optional[str] = None):
        """Muestra detalles de un commit específico"""
        if not self._check_repo():
            return
            
        if not commit_hash:
            commit_hash = self._get_current_commit()
            
        if not commit_hash:
            print("❌ No hay commits para mostrar")
            return
        
        # Buscar hash completo si se dio hash parcial
        if len(commit_hash) < 40:
            for obj_file in self.objects_dir.iterdir():
                if obj_file.name.startswith(commit_hash):
                    commit_hash = obj_file.name
                    break
        
        commit_data = self._load_object(commit_hash)
        if not commit_data:
            print(f"❌ Commit no encontrado: {commit_hash}")
            return
        
        try:
            commit = json.loads(commit_data)
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S', 
                                    time.localtime(commit['timestamp']))
            
            if commit_hash:
                print(f"🔍 Detalles del commit: {commit_hash[:8]}")
            else:
                print("🔍 Detalles del commit: (hash desconocido)")
            print("=" * 40)
            print(f"📅 Fecha: {timestamp}")
            print(f"💬 Mensaje: {commit['message']}")
            print(f"📊 Archivos modificados: {len(commit['files'])}")
            
            if commit.get('parent'):
                print(f"👆 Commit padre: {commit['parent'][:8]}")
            
            print("\n📁 Archivos en este commit:")
            for file_info in commit['files']:
                print(f"   📄 {file_info['path']} ({file_info['hash'][:8]})")
                
        except json.JSONDecodeError:
            print("❌ Error al leer el commit")

class MiniGitCLI:
    def __init__(self):
        self.git = MiniGit()
    
    def run(self):
        """Punto de entrada principal del CLI"""
        parser = argparse.ArgumentParser(
            description="Mini-Git: Sistema de control de versiones simplificado",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Comandos disponibles:
  init                 Inicializa un nuevo repositorio
  add <archivos...>    Añade archivos al staging area
  commit -m "mensaje"  Crea un commit con un mensaje
  status              Muestra el estado del repositorio
  log                 Muestra el historial de commits
  show [hash]         Muestra detalles de un commit

Ejemplos:
  python minigit.py init
  python minigit.py add archivo.txt otro.py
  python minigit.py commit -m "Mi primer commit"
  python minigit.py status
  python minigit.py log
  python minigit.py show abc123
            """
        )
        
        subparsers = parser.add_subparsers(dest='command', help='Comandos disponibles')
        
        # Comando init
        subparsers.add_parser('init', help='Inicializa un nuevo repositorio')
        
        # Comando add
        add_parser = subparsers.add_parser('add', help='Añade archivos al staging area')
        add_parser.add_argument('files', nargs='+', help='Archivos a añadir')
        
        # Comando commit
        commit_parser = subparsers.add_parser('commit', help='Crea un commit')
        commit_parser.add_argument('-m', '--message', required=True, 
                                 help='Mensaje del commit')
        
        # Comando status
        subparsers.add_parser('status', help='Muestra el estado del repositorio')
        
        # Comando log
        log_parser = subparsers.add_parser('log', help='Muestra el historial')
        log_parser.add_argument('-n', '--limit', type=int, default=10,
                              help='Número máximo de commits a mostrar')
        
        # Comando show
        show_parser = subparsers.add_parser('show', help='Muestra detalles de un commit')
        show_parser.add_argument('hash', nargs='?', help='Hash del commit (opcional)')
        
        # Parsear argumentos
        if len(sys.argv) == 1:
            parser.print_help()
            return

        args = parser.parse_args()
        
        # Ejecutar comando
        try:
            if args.command == 'init':
                self.git.init()
            elif args.command == 'add':
                self.git.add(args.files)
            elif args.command == 'commit':
                self.git.commit(args.message)
            elif args.command == 'status':
                self.git.status()
            elif args.command == 'log':
                self.git.log(args.limit)
            elif args.command == 'show':
                self.git.show(args.hash)
            else:
                parser.print_help()
        except KeyboardInterrupt:
            print("\n\n👋 ¡Hasta luego!")
        except Exception as e:
            print(f"❌ Error inesperado: {e}")

def main():
    """Función principal"""
    print("🚀 Mini-Git v1.0")
    print("================")
    
    cli = MiniGitCLI()
    cli.run()

if __name__ == "__main__":
    main()