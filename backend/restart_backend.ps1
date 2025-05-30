#!/usr/bin/env powershell
# restart_backend.ps1 - Script para reiniciar el backend de Mini-Git en Windows
# Ubicación recomendada: backend/

# 1. Detener cualquier proceso uvicorn existente en el puerto 8000
Write-Host "Buscando procesos uvicorn en ejecución..."
$uvicorn = Get-Process | Where-Object { $_.ProcessName -like 'python*' -or $_.ProcessName -like 'uvicorn*' }
foreach ($proc in $uvicorn) {
    if ($proc.MainWindowTitle -like '*uvicorn*' -or $proc.Path -like '*uvicorn*') {
        Write-Host "Deteniendo proceso: $($proc.Id) $($proc.ProcessName)"
        Stop-Process -Id $proc.Id -Force
    }
}

# 2. Navegar a la carpeta backend
Write-Host "Cambiando a la carpeta backend..."
Set-Location -Path "$PSScriptRoot"

# 3. Iniciar el servidor FastAPI con recarga automática
Write-Host "Iniciando backend con: python -m uvicorn app:app --reload"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "python -m uvicorn app:app --reload"

# 4. Mensaje final
Write-Host "Backend reiniciado. Puedes cerrar esta ventana si no la necesitas."
