# 📢 Sistema de Comunicados - Globo Tecnologia

Sistema web completo para criação padronizada de comunicados de tecnologia com geração automática de imagens PNG/JPG.

![Status](https://img.shields.io/badge/status-ready-green)
![Python](https://img.shields.io/badge/python-3.8+-blue)
![Flask](https://img.shields.io/badge/flask-3.0-lightgrey)

## ✨ Funcionalidades

- ✅ **Interface Intuitiva** para analistas criarem comunicados
- ✅ **Editor de Texto** com formatação (negrito, itálico, sublinhado, listas)
- ✅ **Prévia em Tempo Real** do comunicado enquanto você digita
- ✅ **Painel Administrativo** completo para gerenciar templates e configurações
- ✅ **Personalização Total**: fontes, tamanhos, cores de cada elemento
- ✅ **Download PNG de Alta Qualidade** (1200x630px)
- ✅ **Histórico Completo** de todos os comunicados criados
- ✅ **Templates Customizáveis** com imagens de fundo próprias
- ✅ **Configuração via Variáveis de Ambiente** para produção

## 🎯 Visão Geral

Este sistema foi desenvolvido para facilitar a criação de comunicados visuais padronizados, similar à arte fornecida (Ambiente Normalizado). A aplicação permite que analistas criem comunicados rapidamente enquanto administradores mantêm o controle total sobre o design e estilo.

## 📋 Pré-requisitos

Antes de começar, você precisa ter instalado:

- **Sistema Operacional**: Linux (Ubuntu/Debian recomendado)
- **Python**: versão 3.8 ou superior
- **pip**: gerenciador de pacotes Python
- **nginx** (opcional, para produção)
- **Fontes do sistema**: DejaVu Sans (geralmente já instalada)

### Verificar se Python está instalado:

```bash
python3 --version
```

Se não estiver instalado:

```bash
sudo apt-get update
sudo apt-get install python3 python3-pip
```

## 🚀 Instalação Rápida

### Opção 1: Usando o Script Automático (Recomendado)

```bash
cd /home/gccreporter
./iniciar.sh
```

O script irá:
1. Verificar se Python está instalado
2. Instalar todas as dependências necessárias
3. Criar os diretórios necessários
4. Iniciar o servidor Flask

### Opção 2: Instalação Manual

#### 1. Instalar Dependências Python

```bash
cd /home/gccreporter
pip3 install -r requirements.txt
```

ou com usuário local:

```bash
python3 -m pip install --user -r requirements.txt
```

#### 2. Criar Diretórios Necessários

```bash
mkdir -p static/uploads
```

#### 3. Inicializar o Banco de Dados

```bash
python3 app.py
```

Na primeira execução, você verá:

```
✅ Banco de dados inicializado
 * Running on http://0.0.0.0:5000
```

## ⚙️ Configuração

### Variáveis de Ambiente

O sistema utiliza variáveis de ambiente para configuração. Copie o arquivo de exemplo:

```bash
cp env.example .env
```

Edite o arquivo `.env` conforme necessário:

```env
# Chave secreta (gerada automaticamente se não fornecida)
SECRET_KEY=

# URI do banco de dados
DATABASE_URI=sqlite:///comunicados.db

# Pasta de uploads
UPLOAD_FOLDER=static/uploads

# Configurações do servidor (produção)
FLASK_DEBUG=false
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
```

⚠️ **IMPORTANTE**: Para produção, defina `FLASK_DEBUG=false` e configure uma `SECRET_KEY` segura.

## 🌐 Acessando o Sistema

Abra seu navegador e acesse:

```
http://localhost:5000
```

ou se estiver acessando de outra máquina na rede:

```
http://SEU_IP:5000
```

## 📖 Como Usar

### 🔵 Criar um Novo Comunicado

1. Clique em **"📢 Criar Comunicado"**
2. Selecione um template da lista
3. Preencha os campos:
   - **Título**: Ex: "AMBIENTE NORMALIZADO" (obrigatório)
   - **Subtítulo**: Ex: "Telefonia fixa - São Paulo"
   - **Corpo/Descrição**: Texto principal do comunicado (obrigatório)
   - **Rodapé**: Ex: "Em caso de dúvidas consulte o Service Desk no telefone 3003-7000"
   - **Público Alvo**: Ex: "São Paulo"

4. Use a barra de formatação:
   - **B**: Negrito
   - **I**: Itálico
   - **U**: Sublinhado
   - **• Lista**: Criar lista com marcadores

5. Veja a **prévia em tempo real** no painel direito
6. Clique em **"💾 Salvar e Gerar Imagem"**
7. O download do PNG iniciará automaticamente!

#### 3. Ver Histórico
- Clique em **"📋 Histórico"** no menu superior
- Veja todos os comunicados criados
- Baixe novamente qualquer comunicado antigo

### 🔴 Configurações e Templates

#### 1. Configurar Estilos

1. Clique em **"⚙️ Admin"** no menu superior
2. Na aba **"🎨 Configurações"**:
   
   **Para cada elemento (Título, Subtítulo, Corpo, Rodapé):**
   - Ajuste a **fonte** (ex: "Montserrat, sans-serif")
   - Defina o **tamanho** em pixels
   - Escolha a **cor** usando o seletor

3. Clique em **"💾 Salvar Configurações"**
4. As mudanças aplicam-se a todos os comunicados novos

#### 3. Gerenciar Templates

1. Na aba **"🖼️ Templates"**:
2. Digite o **nome do template**
3. Faça upload de uma **imagem de fundo**
   - Tamanho recomendado: **1200x630 pixels**
   - Formato: PNG, JPG ou JPEG
   - Pode ser um gradiente, foto ou qualquer imagem

4. Clique em **"➕ Adicionar Template"**
5. O template estará disponível imediatamente para os analistas

## 🎨 Personalização Avançada

### Alterar Dimensões da Imagem

Edite o arquivo `gerar_imagem.py` (linhas 20-21):

```python
width = 1200  # Largura em pixels
height = 630  # Altura em pixels (padrão: formato widescreen)
```

### Usar Fontes Customizadas

1. Instale a fonte no sistema:
```bash
sudo cp MinhaFonte.ttf /usr/share/fonts/truetype/
sudo fc-cache -f -v
```

2. Edite `gerar_imagem.py` e atualize o caminho:
```python
fonte_titulo = ImageFont.truetype('/usr/share/fonts/truetype/MinhaFonte.ttf', tamanho)
```

### Alterar Cores do Gradiente Padrão

No arquivo `gerar_imagem.py`, função `criar_gradiente_padrao()`:

```python
# Gradiente atual: vermelho → roxo
r = int(255 - (255 * ratio))  # Componente vermelha
g = int(0)                     # Componente verde
b = int(150 * ratio)           # Componente azul
```

## 🏗️ Estrutura do Projeto

```
/home/gccreporter/
├── app.py                      # Aplicação principal Flask
├── gerar_imagem.py            # Módulo de geração de PNG
├── requirements.txt           # Dependências Python
├── iniciar.sh                 # Script de inicialização
├── README.md                  # Este arquivo
├── comunicados.db            # Banco de dados SQLite (criado automaticamente)
│
├── templates/                # Templates HTML (Jinja2)
│   ├── criar_comunicado.html # Interface de criação
│   ├── historico.html       # Lista de comunicados
│   └── preview_comunicado.html # Template de prévia
│
└── static/                  # Arquivos estáticos
    └── uploads/            # Templates de imagem enviados
```

## 🔧 Configuração para Produção

### 1. Configurar nginx (Recomendado)

Crie `/etc/nginx/sites-available/comunicados`:

```nginx
server {
    listen 80;
    server_name seu-dominio.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /static {
        alias /home/gccreporter/static;
    }
}
```

Ative:

```bash
sudo ln -s /etc/nginx/sites-available/comunicados /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 2. Usar Gunicorn para Produção

```bash
pip3 install gunicorn
gunicorn -w 4 -b 127.0.0.1:5000 app:app
```

### 3. Criar Serviço Systemd

Crie `/etc/systemd/system/comunicados.service`:

```ini
[Unit]
Description=Sistema de Comunicados
After=network.target

[Service]
User=operador
WorkingDirectory=/home/gccreporter
ExecStart=/usr/local/bin/gunicorn -w 4 -b 127.0.0.1:5000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

Ative:

```bash
sudo systemctl enable comunicados
sudo systemctl start comunicados
```

## 🔒 Segurança

### ⚠️ ANTES DE USAR EM PRODUÇÃO:

1. **Altere a SECRET_KEY** em `app.py` (linha 11):
   ```python
   app.config['SECRET_KEY'] = 'gere-uma-chave-forte-aleatoria-aqui'
   ```
   
   Gere uma chave forte:
   ```python
   python3 -c "import secrets; print(secrets.token_hex(32))"
   ```

2. **Configure HTTPS** no nginx

4. **Restrinja permissões**:
   ```bash
   chmod 600 /home/gccreporter/comunicados.db
   ```

5. **Configure firewall**:
   ```bash
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   sudo ufw enable
   ```

## 🐛 Solução de Problemas

### Erro: "Python not found"
```bash
sudo apt-get install python3 python3-pip
```

### Erro ao gerar imagem: "cannot open font"
```bash
sudo apt-get install fonts-dejavu-core fonts-dejavu-extra
```

### Porta 5000 já em uso
Altere em `app.py` (última linha):
```python
app.run(debug=True, host='0.0.0.0', port=5001)
```

### Erro de permissão no diretório uploads
```bash
chmod 755 /home/gccreporter/static/uploads
```

### Banco de dados corrompido
```bash
rm comunicados.db
python3 app.py  # Recria o banco
```

## 💡 Dicas e Truques

- **Prévia em Tempo Real**: A prévia atualiza automaticamente conforme você digita
- **Atalhos de Teclado**: Ctrl+B (negrito), Ctrl+I (itálico), Ctrl+U (sublinhado)
- **Reutilizar Comunicados**: Use o histórico para ver comunicados anteriores e criar similares
- **Templates Múltiplos**: Crie templates para diferentes tipos de comunicados (incidentes, manutenções, avisos)
- **Backup Regular**: Faça backup do arquivo `comunicados.db` periodicamente

## 📝 Licença

Uso interno - Globo Tecnologia

## 🆘 Suporte

### Logs da Aplicação
Os logs aparecem no terminal onde o Flask está rodando.

### Logs do nginx
```bash
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log
```

### Verificar Status
```bash
sudo systemctl status comunicados
sudo systemctl status nginx
```

---

## 📞 Contato

Para dúvidas, sugestões ou reportar problemas, entre em contato com a equipe de Tecnologia.

**Desenvolvido com ❤️ para a Globo Tecnologia**
