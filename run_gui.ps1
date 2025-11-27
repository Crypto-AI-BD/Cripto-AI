# Executar Desktop App
# Execute este script para iniciar a aplicação desktop

Write-Host "🚀 Iniciando Aplicação Desktop..." -ForegroundColor Green

# Verificar se o ambiente virtual existe
if (Test-Path ".\venv\Scripts\Activate.ps1") {
    Write-Host "✅ Ativando ambiente virtual..." -ForegroundColor Yellow
    .\venv\Scripts\Activate.ps1
} else {
    Write-Host "⚠️ Ambiente virtual não encontrado!" -ForegroundColor Red
    Write-Host "Execute: python -m venv venv" -ForegroundColor Yellow
    exit
}

# Executar aplicação
Write-Host "🖥️ Iniciando interface gráfica..." -ForegroundColor Cyan
python desktop_app/main.py

Write-Host "✅ Aplicação encerrada." -ForegroundColor Green
