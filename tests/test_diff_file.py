import requests
import os
import time

def test_diff_file():
    base_url = "http://localhost:8000/api"
    test_file = "diff_test.txt"
    file_path = os.path.join("backend", "mini_git_repo", test_file)

    # 1. Crear archivo y hacer commit inicial
    r = requests.post(f"{base_url}/add", json=[{"name": test_file, "content": "linea1\nlinea2\n"}])
    assert r.status_code == 200
    r = requests.post(f"{base_url}/commit", json={"message": "commit inicial"})
    assert r.status_code == 200

    # 2. Modificar archivo
    with open(file_path, "w", encoding="utf-8") as f:
        f.write("linea1\nlinea2\nlinea3\n")
    time.sleep(0.5)  # Esperar a que el backend detecte el cambio

    # 3. Pedir diff
    r = requests.get(f"{base_url}/diff/{test_file}")
    assert r.status_code == 200
    data = r.json()
    assert data["success"]
    diff = data["diff"]
    print("Diff devuelto por el endpoint:\n", diff)
    assert "+linea3" in diff
    print("Diff generado correctamente:\n", diff)

    # 4. Limpiar
    os.remove(file_path)

if __name__ == "__main__":
    test_diff_file()
    print("Test de diff_file PASÓ correctamente.")
