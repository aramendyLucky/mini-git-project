#!/usr/bin/env python3
"""
Test completo para la clase Repository.
Un gran developer siempre prueba su código antes de continuar.
"""

import os
import shutil
import tempfile
from pathlib import Path
from repository import Repository

def test_basic_functionality():
    """
    Prueba básica: crear repositorio y verificar estructura.
    """
    print("=" * 50)
    print("TEST 1: Funcionalidad básica")
    print("=" * 50)
    
    # Crear directorio temporal para pruebas
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"📁 Directorio de prueba: {temp_dir}")
        
        # Cambiar al directorio temporal
        original_dir = os.getcwd()
        os.chdir(temp_dir)
        
        try:
            # 1. Crear repositorio
            print("\n1️⃣ Inicializando repositorio...")
            repo = Repository()
            success = repo.init()
            
            assert success == True, "❌ Error: init() debería retornar True"
            print("✅ Repositorio inicializado correctamente")
            
            # 2. Verificar estructura de carpetas
            print("\n2️⃣ Verificando estructura...")
            assert repo.mygit_path.exists(), "❌ Error: carpeta .mygit no existe"
            assert repo.objects_path.exists(), "❌ Error: carpeta objects no existe"
            assert repo.config_file.exists(), "❌ Error: config.json no existe"
            assert repo.staging_file.exists(), "❌ Error: staging.json no existe"
            assert repo.commits_file.exists(), "❌ Error: commits.json no existe"
            print("✅ Estructura de carpetas correcta")
            
            # 3. Verificar que es repositorio válido
            print("\n3️⃣ Verificando validez del repositorio...")
            assert repo.is_repository() == True, "❌ Error: no reconoce repo válido"
            print("✅ Repositorio reconocido como válido")
            
            # 4. Verificar configuración inicial
            print("\n4️⃣ Verificando configuración...")
            config = repo.get_config()
            assert "name" in config, "❌ Error: falta 'name' en config"
            assert "created" in config, "❌ Error: falta 'created' en config"  
            assert "last_commit" in config, "❌ Error: falta 'last_commit' en config"
            assert config["last_commit"] is None, "❌ Error: last_commit debería ser None"
            print(f"✅ Configuración válida: {config}")
            
            # 5. Verificar staging inicial
            print("\n5️⃣ Verificando staging inicial...")
            staging = repo.get_staging()
            assert staging["files"] == [], "❌ Error: staging debería estar vacío"
            assert staging["timestamp"] is None, "❌ Error: timestamp debería ser None"
            print("✅ Staging área inicializada correctamente")
            
            # 6. Verificar commits inicial
            print("\n6️⃣ Verificando commits inicial...")
            commits = repo.get_commits()
            assert commits == [], "❌ Error: lista de commits debería estar vacía"
            print("✅ Lista de commits inicializada correctamente")
            
            print("\n🎉 TODAS LAS PRUEBAS BÁSICAS PASARON 🎉")
            
        finally:
            # Volver al directorio original
            os.chdir(original_dir)

def test_duplicate_init():
    """
    Prueba: intentar inicializar repositorio que ya existe.
    """
    print("\n" + "=" * 50)
    print("TEST 2: Inicialización duplicada")
    print("=" * 50)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        original_dir = os.getcwd()
        os.chdir(temp_dir)
        
        try:
            repo = Repository()
            
            # Primera inicialización
            print("1️⃣ Primera inicialización...")
            success1 = repo.init()
            assert success1 == True, "❌ Primera init debería funcionar"
            print("✅ Primera inicialización exitosa")
            
            # Segunda inicialización (debería fallar)
            print("\n2️⃣ Segunda inicialización (debería fallar)...")
            success2 = repo.init()
            assert success2 == False, "❌ Segunda init debería retornar False"
            print("✅ Segunda inicialización correctamente rechazada")
            
        finally:
            os.chdir(original_dir)

def test_file_hashing():
    """
    Prueba: cálculo de hash de archivos.
    """
    print("\n" + "=" * 50)
    print("TEST 3: Cálculo de hash de archivos")
    print("=" * 50)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        original_dir = os.getcwd()
        os.chdir(temp_dir)
        
        try:
            repo = Repository()
            repo.init()
            
            # Crear archivo de prueba
            test_file = "test.txt"
            test_content = "Hola mundo!\nEste es un archivo de prueba."
            
            print(f"1️⃣ Creando archivo: {test_file}")
            with open(test_file, 'w', encoding='utf-8') as f:
                f.write(test_content)
            
            # Calcular hash
            print("2️⃣ Calculando hash...")
            file_hash = repo.calculate_file_hash(test_file)
            
            # Verificar que el hash tiene formato correcto
            assert isinstance(file_hash, str), "❌ Hash debería ser string"
            assert len(file_hash) == 40, f"❌ Hash SHA-1 debería tener 40 caracteres, tiene {len(file_hash)}"
            assert all(c in '0123456789abcdef' for c in file_hash), "❌ Hash debería ser hexadecimal"
            
            print(f"✅ Hash calculado correctamente: {file_hash}")
            
            # Calcular hash del mismo archivo otra vez (debería ser igual)
            print("3️⃣ Verificando consistencia...")
            file_hash2 = repo.calculate_file_hash(test_file)
            assert file_hash == file_hash2, "❌ Hash debería ser consistente"
            print("✅ Hash es consistente")
            
            # Intentar hash de archivo inexistente
            print("4️⃣ Probando archivo inexistente...")
            try:
                repo.calculate_file_hash("archivo_que_no_existe.txt")
                assert False, "❌ Debería lanzar excepción para archivo inexistente"
            except Exception as e:
                print(f"✅ Correctamente lanzó excepción: {e}")
                
        finally:
            os.chdir(original_dir)

def test_invalid_repository():
    """
    Prueba: operaciones en directorio sin repositorio.
    """
    print("\n" + "=" * 50)
    print("TEST 4: Operaciones sin repositorio")
    print("=" * 50)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        original_dir = os.getcwd()
        os.chdir(temp_dir)
        
        try:
            repo = Repository()
            
            # Verificar que NO es repositorio
            print("1️⃣ Verificando que NO es repositorio...")
            assert repo.is_repository() == False, "❌ No debería ser repositorio válido"
            print("✅ Correctamente detecta que no es repositorio")
            
            # Intentar operaciones sin inicializar
            print("2️⃣ Probando get_config() sin repo...")
            try:
                repo.get_config()
                assert False, "❌ Debería lanzar excepción"
            except Exception as e:
                print(f"✅ Correctamente lanzó excepción: {e}")
            
            print("3️⃣ Probando get_staging() sin repo...")
            try:
                repo.get_staging()
                assert False, "❌ Debería lanzar excepción"
            except Exception as e:
                print(f"✅ Correctamente lanzó excepción: {e}")
                
            print("4️⃣ Probando get_commits() sin repo...")
            try:
                repo.get_commits()
                assert False, "❌ Debería lanzar excepción"  
            except Exception as e:
                print(f"✅ Correctamente lanzó excepción: {e}")
                
        finally:
            os.chdir(original_dir)

def run_all_tests():
    """
    Ejecuta todas las pruebas.
    """
    print("🧪 INICIANDO PRUEBAS DE LA CLASE REPOSITORY")
    print("Un gran developer siempre prueba su código\n")
    
    try:
        test_basic_functionality()
        test_duplicate_init()
        test_file_hashing()
        test_invalid_repository()
        
        print("\n" + "🎉" * 20)
        print("🎉 TODAS LAS PRUEBAS PASARON EXITOSAMENTE 🎉")
        print("🎉 La clase Repository funciona perfectamente 🎉")
        print("🎉" * 20)
        print("\n✅ LISTO PARA CONTINUAR CON EL SIGUIENTE PASO")
        
    except AssertionError as e:
        print(f"\n❌ PRUEBA FALLÓ: {e}")
        print("❌ Necesitamos arreglar el código antes de continuar")
        return False
    except Exception as e:
        print(f"\n💥 ERROR INESPERADO: {e}")
        print("💥 Revisar el código")
        return False
    
    return True

if __name__ == "__main__":
    run_all_tests()