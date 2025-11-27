# Executar Dashboard Streamlit
# Execute este script para iniciar o dashboard web

Write-Host "🚀 Iniciando Dashboard Streamlit..." -ForegroundColor Green

# Verificar se o ambiente virtual existe
if (Test-Path ".\venv\Scripts\Activate.ps1") {
    Write-Host "✅ Ativando ambiente virtual..." -ForegroundColor Yellow
    .\venv\Scripts\Activate.ps1
} else {
    Write-Host "⚠️ Ambiente virtual não encontrado!" -ForegroundColor Red
    Write-Host "Execute: python -m venv venv" -ForegroundColor Yellow
    exit
}

# Executar Streamlit
Write-Host "🌐 Iniciando servidor Streamlit..." -ForegroundColor Cyan
Write-Host "📍 Acesse: http://localhost:8501" -ForegroundColor Yellow

streamlit run app.py

Write-Host "✅ Servidor encerrado." -ForegroundColor Green
