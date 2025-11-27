# Setup do Projeto
# Execute este script para configurar o ambiente

Write-Host "🚀 Configurando Projeto Big Data..." -ForegroundColor Green
Write-Host ""

# 1. Criar ambiente virtual
Write-Host "1️⃣ Criando ambiente virtual..." -ForegroundColor Cyan
if (-not (Test-Path ".\venv")) {
    python -m venv venv
    Write-Host "✅ Ambiente virtual criado!" -ForegroundColor Green
} else {
    Write-Host "⚠️ Ambiente virtual já existe!" -ForegroundColor Yellow
}

# 2. Ativar ambiente virtual
Write-Host ""
Write-Host "2️⃣ Ativando ambiente virtual..." -ForegroundColor Cyan
.\venv\Scripts\Activate.ps1

# 3. Atualizar pip
Write-Host ""
Write-Host "3️⃣ Atualizando pip..." -ForegroundColor Cyan
python -m pip install --upgrade pip

# 4. Instalar dependências
Write-Host ""
Write-Host "4️⃣ Instalando dependências..." -ForegroundColor Cyan
pip install -r requirements.txt

# 5. Criar diretórios necessários
Write-Host ""
Write-Host "5️⃣ Criando diretórios..." -ForegroundColor Cyan
$directories = @(
    "data\raw",
    "data\processed",
    "models",
    "visualizations",
    "logs"
)

foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "  📁 Criado: $dir" -ForegroundColor Gray
    }
}

# 6. Verificar instalação
Write-Host ""
Write-Host "6️⃣ Verificando instalação..." -ForegroundColor Cyan

$packages = @("pandas", "numpy", "pyspark", "streamlit", "PyQt5", "plotly")
$allInstalled = $true

foreach ($package in $packages) {
    $result = pip show $package 2>$null
    if ($result) {
        Write-Host "  ✅ $package" -ForegroundColor Green
    } else {
        Write-Host "  ❌ $package" -ForegroundColor Red
        $allInstalled = $false
    }
}

# 7. Finalizar
Write-Host ""
if ($allInstalled) {
    Write-Host "🎉 Setup concluído com sucesso!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 Próximos passos:" -ForegroundColor Yellow
    Write-Host "  1. Execute: .\run_streamlit.ps1 (Dashboard Web)" -ForegroundColor Cyan
    Write-Host "  2. Execute: .\run_gui.ps1 (Aplicação Desktop)" -ForegroundColor Cyan
    Write-Host "  3. Execute: jupyter notebook (Notebooks)" -ForegroundColor Cyan
} else {
    Write-Host "⚠️ Alguns pacotes não foram instalados!" -ForegroundColor Red
    Write-Host "Execute novamente: pip install -r requirements.txt" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "📚 Leia o README.md para mais informações!" -ForegroundColor Magenta
