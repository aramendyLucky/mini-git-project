import requests
import os
import time

def test_staging_api():
    base_url = "http://localhost:8000/api"
    test_file = "staging_test.txt"
    file_path = os.path.join("backend", "mini_git_repo", test_file)

    # 1. Crear archivo
    r = requests.post(f"{base_url}/add", json=[{"name": test_file, "content": "linea1\n"}])
    assert r.status_code == 200
    # 2. Quitar del staging
    r = requests.post(f"{base_url}/unstage/{test_file}")
    assert r.status_code == 200
    data = r.json()
    assert data["success"]
    # 3. Agregar al staging
    r = requests.post(f"{base_url}/stage/{test_file}")
    assert r.status_code == 200
    data = r.json()
    assert data["success"]
    # 4. Verificar que el archivo está en staging consultando status
    r = requests.get(f"{base_url}/status")
    assert r.status_code == 200
    status = r.json()
    assert test_file in status["staged_files"]
    # 5. Limpiar
    os.remove(file_path)
    print("Test de staging API PASÓ correctamente.")

if __name__ == "__main__":
    test_staging_api()
