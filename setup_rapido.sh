#!/bin/bash
# Script rápido de configuração no servidor

echo "🚀 Configuração Rápida - Sistema de Comunicados"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado!"
    echo "Instale com: sudo apt-get install python3 python3-pip"
    exit 1
fi

echo "✅ Python: $(python3 --version)"

# Criar venv (opcional mas recomendado)
read -p "Criar ambiente virtual? (s/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Ss]$ ]]; then
    echo "📦 Criando ambiente virtual..."
    python3 -m venv venv
    source venv/bin/activate
    echo "✅ Ambiente virtual criado"
fi

# Instalar dependências
echo ""
echo "📦 Instalando dependências..."
if [ -d "venv" ]; then
    venv/bin/pip install -r requirements.txt
else
    python3 -m pip install --user -r requirements.txt
fi

# Criar .env se não existir
if [ ! -f .env ]; then
    echo ""
    echo "📝 Criando arquivo .env..."
    if [ -f env.example ]; then
        cp env.example .env
    else
        cat > .env << 'ENVEOF'
SECRET_KEY=
DATABASE_URI=sqlite:///comunicados.db
UPLOAD_FOLDER=static/uploads
FLASK_DEBUG=false
FLASK_HOST=127.0.0.1
FLASK_PORT=5000
ENVEOF
    fi
    echo "✅ Arquivo .env criado"
    echo "⚠️  IMPORTANTE: Edite .env e configure SECRET_KEY!"
    echo "   Gere uma chave com: python3 -c \"import secrets; print(secrets.token_urlsafe(32))\""
fi

# Criar diretórios
echo ""
echo "📁 Criando diretórios..."
mkdir -p static/uploads
mkdir -p logs
chmod 755 static/uploads
echo "✅ Diretórios criados"

# Inicializar banco
echo ""
echo "🗄️  Inicializando banco de dados..."
if [ -d "venv" ]; then
    venv/bin/python app.py &
    sleep 3
    pkill -f "python.*app.py"
else
    python3 app.py &
    sleep 3
    pkill -f "python.*app.py"
fi
echo "✅ Banco de dados inicializado"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Configuração básica concluída!"
echo ""
echo "📝 PRÓXIMOS PASSOS:"
echo "1. Edite .env e configure SECRET_KEY"
echo "2. Teste: python3 app.py (ou venv/bin/python app.py)"
echo "3. Configure Nginx (veja DEPLOY.md)"
echo "4. Configure serviço systemd (veja DEPLOY.md)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
