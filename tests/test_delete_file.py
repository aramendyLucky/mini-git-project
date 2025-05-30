import requests

BACKEND = "http://127.0.0.1:8000"

# 1. Crear archivo de prueba
r = requests.post(f"{BACKEND}/api/add", json=[{"name": "test_delete.txt", "content": "archivo para test de borrado"}])
assert r.ok, f"Error al crear archivo: {r.text}"

# 2. Eliminar archivo
r = requests.delete(f"{BACKEND}/api/file/test_delete.txt")
assert r.ok, f"Error al eliminar archivo: {r.text}"

# 3. Verificar que no existe
import os
assert not os.path.exists("backend/mini_git_repo/test_delete.txt"), "El archivo NO fue eliminado"

print("TEST DELETE FILE: OK")
