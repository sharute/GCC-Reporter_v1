# 📢 Sistema de Comunicados - Globo Tecnologia

Sistema web para criação padronizada de comunicados com geração automática de imagens PNG.

![Python](https://img.shields.io/badge/python-3.8+-blue)
![Flask](https://img.shields.io/badge/flask-3.0-lightgrey)

## ✨ Funcionalidades

- **Interface Intuitiva** para criar comunicados
- **Editor de Texto** com formatação (negrito, itálico, sublinhado)
- **Prévia em Tempo Real** enquanto digita
- **Download PNG** de alta qualidade (1200x630px)
- **Histórico Completo** de todos os comunicados
- **Templates Customizáveis** com imagens de fundo
- **Painel Admin** para configurar estilos e templates

## 🚀 Início Rápido

```bash
# Instalar dependências
pip3 install -r requirements.txt

# Iniciar
./iniciar.sh

# Acessar
# http://localhost:5000
```

## 📚 Documentação

| Documento | Descrição |
|-----------|-----------|
| [Guia do Usuário](docs/guia-usuario.md) | Como usar o sistema |
| [Deploy](docs/deploy.md) | Configurar para produção |
| [Regras de Formatação](docs/regras-formatacao.md) | Especificações de estilo |
| [Changelog](docs/changelog.md) | Histórico de mudanças |

## ⚙️ Configuração

Copie o arquivo de exemplo e configure:

```bash
cp env.example .env
```

Variáveis principais:
- `SECRET_KEY` - Chave secreta (gerada automaticamente se vazia)
- `DATABASE_URI` - Banco de dados (padrão: SQLite)
- `FLASK_DEBUG` - Debug mode (false para produção)

## 🏗️ Estrutura

```
├── app.py              # Aplicação Flask
├── gerar_imagem.py     # Gerador de PNG
├── requirements.txt    # Dependências
├── iniciar.sh          # Script de início
├── docs/               # Documentação adicional
├── templates/          # Templates HTML
└── static/             # CSS, JS, uploads
```

## 🐛 Problemas Comuns

**Python não encontrado:**
```bash
sudo apt-get install python3 python3-pip
```

**Erro ao gerar imagem:**
```bash
sudo apt-get install fonts-dejavu-core
```

**Porta ocupada:** Edite a porta em `.env` ou `app.py`

## 📝 Licença

Uso interno - Globo Tecnologia
