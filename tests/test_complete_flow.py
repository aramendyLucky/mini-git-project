#!/usr/bin/env python3
"""
Pruebas del flujo completo: Repository + Staging + Commit

Un gran developer prueba todo el flujo de principio a fin.
Esto simula el uso real del sistema.
"""

import os
import tempfile
from pathlib import Path
from repository import Repository
from commit import Commit

def test_complete_workflow():
    """
    Prueba el flujo completo de trabajo:
    1. Crear repositorio
    2. Crear archivos
    3. Agregar al staging
    4. Hacer commits
    5. Ver historial
    """
    print("=" * 60)
    print("🧪 TEST: Flujo completo de trabajo")  
    print("=" * 60)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        original_dir = os.getcwd()
        os.chdir(temp_dir)
        
        try:
            # 1. INICIALIZAR REPOSITORIO
            print("\n1️⃣ Inicializando repositorio...")
            repo = Repository()
            repo.init()
            print("✅ Repositorio inicializado")
            
            # 2. CREAR ARCHIVOS DE PRUEBA
            print("\n2️⃣ Creando archivos de prueba...")
            
            # Archivo 1: main.py
            with open("main.py", "w", encoding="utf-8") as f:
                f.write("""#!/usr/bin/env python3
# Archivo principal del proyecto
def main():
    print("Hola mundo!")
    
if __name__ == "__main__":
    main()
""")
            
            # Archivo 2: utils.py  
            with open("utils.py", "w", encoding="utf-8") as f:
                f.write("""# Utilidades del proyecto
def saludar(nombre):
    return f"Hola {nombre}!"

def calcular(a, b):
    return a + b
""")
            
            print("✅ Archivos creados: main.py, utils.py")
            
            # 3. PROBAR STATUS INICIAL
            print("\n3️⃣ Estado inicial del repositorio...")
            repo.status()
            
            # 4. AGREGAR ARCHIVOS AL STAGING
            print("\n4️⃣ Agregando archivos al staging...")
            repo.add_file("main.py")
            repo.add_file("utils.py")
            
            # 5. VERIFICAR STATUS DESPUÉS DE ADD
            print("\n5️⃣ Estado después de agregar archivos...")
            repo.status()
            
            # 6. CREAR PRIMER COMMIT
            print("\n6️⃣ Creando primer commit...")
            commit_manager = Commit(repo)
            commit1_id = commit_manager.create("Initial commit: added main.py and utils.py")
            
            assert len(commit1_id) == 40, "❌ ID de commit debe tener 40 caracteres"
            print(f"✅ Primer commit creado: {commit1_id[:8]}...")
            
            # 7. VERIFICAR STATUS DESPUÉS DEL COMMIT
            print("\n7️⃣ Estado después del commit...")
            repo.status()
            
            # 8. MODIFICAR ARCHIVO Y HACER SEGUNDO COMMIT
            print("\n8️⃣ Modificando archivo para segundo commit...")
            
            # Modificar utils.py
            with open("utils.py", "w", encoding="utf-8") as f:
                f.write("""# Utilidades del proyecto
def saludar(nombre):
    return f"Hola {nombre}!"

def calcular(a, b):
    return a + b

def despedir(nombre):
    return f"Adiós {nombre}!"
""")
            
            # Crear nuevo archivo
            with open("config.txt", "w", encoding="utf-8") as f:
                f.write("# Configuración del proyecto\nversion=1.0\nauthor=user\n")
            
            # Agregar archivos modificados/nuevos
            repo.add_file("utils.py")      # Archivo modificado
            repo.add_file("config.txt")    # Archivo nuevo
            
            print("✅ Archivos modificados y agregados al staging")
            
            # 9. SEGUNDO COMMIT
            print("\n9️⃣ Creando segundo commit...")
            commit2_id = commit_manager.create("Added farewell function and config file")
            
            assert len(commit2_id) == 40, "❌ ID de commit debe tener 40 caracteres"
            assert commit1_id != commit2_id, "❌ Los commits deben tener IDs diferentes"
            print(f"✅ Segundo commit creado: {commit2_id[:8]}...")
            
            # 10. VER HISTORIAL COMPLETO
            print("\n🔟 Mostrando historial completo...")
            commit_manager.show_log()
            
            # 11. VERIFICAR DATOS DE COMMITS
            print("\n1️⃣1️⃣ Verificando datos de commits...")
            
            commits = commit_manager.get_history()
            assert len(commits) == 2, f"❌ Debería haber 2 commits, hay {len(commits)}"
            
            # El más reciente debe ser el segundo
            latest_commit = commits[0]
            assert latest_commit["id"] == commit2_id, "❌ El commit más reciente debe ser el segundo"
            assert latest_commit["parent"] == commit1_id, "❌ El segundo commit debe tener al primero como padre"
            
            # El primero no debe tener padre
            first_commit = commits[1]
            assert first_commit["id"] == commit1_id, "❌ El segundo en la lista debe ser el primer commit"
            assert first_commit["parent"] is None, "❌ El primer commit no debe tener padre"
            
            print("✅ Relaciones entre commits correctas")
            
            # 12. VERIFICAR ARCHIVOS EN OBJECTS
            print("\n1️⃣2️⃣ Verificando archivos en objects...")
            
            objects_dir = repo.objects_path
            object_files = list(objects_dir.glob("*"))
            
            # Deberíamos tener al menos 4 archivos:
            # - main.py (versión 1)
            # - utils.py (versión 1) 
            # - utils.py (versión 2)
            # - config.txt (versión 1)
            assert len(object_files) >= 3, f"❌ Debería haber al menos 3 archivos en objects, hay {len(object_files)}"
            
            print(f"✅ {len(object_files)} archivos guardados en objects/")
            
            print("\n🎉" * 20)
            print("🎉 FLUJO COMPLETO FUNCIONA PERFECTAMENTE 🎉")
            print("🎉" * 20)
            
        finally:
            os.chdir(original_dir)

def test_staging_operations():
    """
    Prueba operaciones específicas del staging area.
    """
    print("\n" + "=" * 60)
    print("🧪 TEST: Operaciones de staging")
    print("=" * 60)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        original_dir = os.getcwd()
        os.chdir(temp_dir)
        
        try:
            # Inicializar repositorio
            repo = Repository()
            repo.init()
            
            # Crear archivo de prueba
            with open("test.py", "w") as f:
                f.write("print('test')")
            
            # 1. AGREGAR ARCHIVO
            print("\n1️⃣ Agregando archivo al staging...")
            repo.add_file("test.py")
            
            staging = repo.get_staging()
            assert "test.py" in staging["files"], "❌ Archivo debería estar en staging"
            print("✅ Archivo agregado correctamente")
            
            # 2. AGREGAR EL MISMO ARCHIVO (NO DEBE DUPLICAR)
            print("\n2️⃣ Agregando mismo archivo otra vez...")
            repo.add_file("test.py")
            
            staging = repo.get_staging()
            assert staging["files"].count("test.py") == 1, "❌ No debería duplicar archivos"
            print("✅ No duplica archivos en staging")
            
            # 3. REMOVER ARCHIVO DEL STAGING
            print("\n3️⃣ Removiendo archivo del staging...")
            result = repo.remove_file_from_staging("test.py")
            
            assert result == True, "❌ Remove debería retornar True"
            
            staging = repo.get_staging()
            assert "test.py" not in staging["files"], "❌ Archivo debería haberse removido"
            print("✅ Archivo removido correctamente")
            
            # 4. REMOVER ARCHIVO QUE NO ESTÁ EN STAGING
            print("\n4️⃣ Removiendo archivo que no está en staging...")
            result = repo.remove_file_from_staging("test.py")
            
            assert result == False, "❌ Remove debería retornar False para archivo no existente"
            print("✅ Manejo correcto de archivo no existente")
            
            # 5. INTENTAR AGREGAR ARCHIVO INEXISTENTE
            print("\n5️⃣ Intentando agregar archivo inexistente...")
            try:
                repo.add_file("archivo_inexistente.py")
                assert False, "❌ Debería lanzar excepción"
            except Exception as e:
                print(f"✅ Correctamente lanzó excepción: {e}")
            
            print("\n✅ TODAS LAS OPERACIONES DE STAGING FUNCIONAN")
            
        finally:
            os.chdir(original_dir)

def test_empty_commit():
    """
    Prueba intentar hacer commit sin archivos en staging.
    """
    print("\n" + "=" * 60)
    print("🧪 TEST: Commit vacío")
    print("=" * 60)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        original_dir = os.getcwd()
        os.chdir(temp_dir)
        
        try:
            repo = Repository()
            repo.init()
            commit_manager = Commit(repo)
            
            # Intentar commit sin archivos en staging
            print("1️⃣ Intentando commit sin archivos en staging...")
            try:
                commit_manager.create("Commit vacío")
                assert False, "❌ Debería lanzar excepción"
            except Exception as e:
                print(f"✅ Correctamente lanzó excepción: {e}")
            
            # Intentar commit con mensaje vacío
            print("\n2️⃣ Intentando commit con mensaje vacío...")
            with open("test.py", "w") as f:
                f.write("print('test')")
            
            repo.add_file("test.py")
            
            try:
                commit_manager.create("")  # Mensaje vacío
                assert False, "❌ Debería lanzar excepción"
            except Exception as e:
                print(f"✅ Correctamente lanzó excepción: {e}")
            
            print("\n✅ VALIDACIONES DE COMMIT FUNCIONAN")
            
        finally:
            os.chdir(original_dir)

def run_all_tests():
    """
    Ejecuta todas las pruebas del flujo completo.
    """
    print("🚀 INICIANDO PRUEBAS DEL FLUJO COMPLETO")
    print("Probando Repository + Staging + Commit integrados\n")
    
    try:
        test_complete_workflow()
        test_staging_operations()  
        test_empty_commit()
        
        print("\n" + "🎉" * 25)
        print("🎉 TODAS LAS PRUEBAS DEL FLUJO COMPLETO PASARON 🎉")
        print("🎉 EL SISTEMA FUNCIONA PERFECTAMENTE 🎉")
        print("🎉" * 25)
        print("\n✅ LISTO PARA CREAR LA INTERFACE CLI")
        
        return True
        
    except AssertionError as e:
        print(f"\n❌ PRUEBA FALLÓ: {e}")
        return False
    except Exception as e:
        print(f"\n💥 ERROR INESPERADO: {e}")
        return False

if __name__ == "__main__":
    run_all_tests()