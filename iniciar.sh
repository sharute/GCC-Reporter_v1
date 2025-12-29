#!/bin/bash
# Script de inicialização do Sistema de Comunicados

echo "🚀 Sistema de Comunicados - Globo Tecnologia"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não está instalado!"
    echo ""
    echo "Para instalar, execute:"
    echo "  sudo apt-get update"
    echo "  sudo apt-get install python3 python3-pip"
    exit 1
fi

echo "✅ Python: $(python3 --version)"

# Criar diretórios
mkdir -p static/uploads

# Instalar dependências
echo ""
echo "📦 Instalando dependências..."
python3 -m pip install --user -r requirements.txt

# Verificar arquivo .env
if [ ! -f .env ]; then
    echo ""
    echo "⚠️  Arquivo .env não encontrado!"
    echo "   Criando .env a partir de env.example..."
    if [ -f env.example ]; then
        cp env.example .env
        echo "   ✅ Arquivo .env criado. Ajuste as configurações se necessário."
    else
        echo "   ⚠️  env.example não encontrado. Criando .env padrão..."
        cat > .env << 'EOF'
SECRET_KEY=
DATABASE_URI=sqlite:///comunicados.db
UPLOAD_FOLDER=static/uploads
FLASK_DEBUG=false
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
EOF
    fi
fi

# Iniciar aplicação
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🌐 Acesse: http://localhost:5000"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

python3 app.py
