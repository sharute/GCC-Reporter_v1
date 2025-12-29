# 🚀 Guia Rápido - Configuração no Servidor

## Passo a Passo para Configurar no Servidor

### 1️⃣ Conectar ao Servidor

```bash
ssh usuario@seu-servidor.com
cd /caminho/para/gccreporter
```

### 2️⃣ Verificar Python

```bash
python3 --version
# Deve ser 3.8 ou superior
```

Se não tiver Python:
```bash
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv
```

### 3️⃣ Criar Ambiente Virtual (Recomendado)

```bash
python3 -m venv venv
source venv/bin/activate
```

### 4️⃣ Instalar Dependências

```bash
pip install -r requirements.txt
```

### 5️⃣ Configurar Variáveis de Ambiente

```bash
# Copiar arquivo de exemplo
cp env.example .env

# Editar configurações
nano .env
```

**Configurações mínimas necessárias:**

```env
# Gerar uma chave secreta forte
SECRET_KEY=SUA_CHAVE_SECRETA_AQUI

# Banco de dados (SQLite para começar, ou PostgreSQL/MySQL para produção)
DATABASE_URI=sqlite:///comunicados.db

# Pasta de uploads
UPLOAD_FOLDER=static/uploads

# PRODUÇÃO - IMPORTANTE!
FLASK_DEBUG=false
FLASK_HOST=127.0.0.1
FLASK_PORT=5000
```

**Gerar SECRET_KEY:**
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 6️⃣ Criar Diretórios Necessários

```bash
mkdir -p static/uploads
mkdir -p logs
chmod 755 static/uploads
```

### 7️⃣ Inicializar Banco de Dados

```bash
# Ativar venv se estiver usando
source venv/bin/activate

# Executar uma vez para criar o banco
python3 app.py
# Pressione Ctrl+C após ver "Running on"
```

### 8️⃣ Testar Localmente

```bash
python3 app.py
```

Acesse: `http://localhost:5000` (ou IP do servidor)

### 9️⃣ Configurar como Serviço (Systemd)

Criar arquivo de serviço:

```bash
sudo nano /etc/systemd/system/gccreporter.service
```

**Conteúdo (ajuste caminhos e usuário):**

```ini
[Unit]
Description=Sistema de Comunicados - Globo Tecnologia
After=network.target

[Service]
Type=simple
User=seu-usuario
WorkingDirectory=/caminho/para/gccreporter
Environment="PATH=/caminho/para/gccreporter/venv/bin"
ExecStart=/caminho/para/gccreporter/venv/bin/python app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Habilitar e iniciar:**

```bash
sudo systemctl daemon-reload
sudo systemctl enable gccreporter
sudo systemctl start gccreporter
sudo systemctl status gccreporter
```

### 🔟 Configurar Nginx (Proxy Reverso)

**Instalar Nginx:**
```bash
sudo apt-get install -y nginx
```

**Criar configuração:**
```bash
sudo nano /etc/nginx/sites-available/gccreporter
```

**Conteúdo:**
```nginx
server {
    listen 80;
    server_name seu-dominio.com.br;

    client_max_body_size 10M;

    # Arquivos estáticos
    location /static {
        alias /caminho/para/gccreporter/static;
        expires 30d;
    }

    # Proxy para Flask
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**Habilitar site:**
```bash
sudo ln -s /etc/nginx/sites-available/gccreporter /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 1️⃣1️⃣ Configurar SSL (Opcional mas Recomendado)

```bash
sudo apt-get install -y certbot python3-certbot-nginx
sudo certbot --nginx -d seu-dominio.com.br
```

### 1️⃣2️⃣ Configurar Firewall

```bash
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

## ✅ Checklist de Verificação

- [ ] Python 3.8+ instalado
- [ ] Dependências instaladas (`pip install -r requirements.txt`)
- [ ] Arquivo `.env` criado e configurado
- [ ] `SECRET_KEY` gerada e configurada
- [ ] `FLASK_DEBUG=false` no `.env`
- [ ] Diretórios criados (`static/uploads`, `logs`)
- [ ] Banco de dados inicializado
- [ ] Teste local funcionando
- [ ] Serviço systemd configurado e ativo
- [ ] Nginx configurado e funcionando
- [ ] SSL configurado (se aplicável)
- [ ] Firewall configurado

## 🔍 Comandos Úteis

**Ver logs do serviço:**
```bash
sudo journalctl -u gccreporter -f
```

**Reiniciar serviço:**
```bash
sudo systemctl restart gccreporter
```

**Ver status:**
```bash
sudo systemctl status gccreporter
```

**Ver logs da aplicação:**
```bash
tail -f /caminho/para/gccreporter/logs/audit.log
```

**Testar conexão:**
```bash
curl http://localhost:5000
```

## ⚠️ Problemas Comuns

### Porta 5000 já em uso
```bash
sudo lsof -i :5000
sudo kill -9 PID
```

### Erro de permissão
```bash
sudo chown -R seu-usuario:seu-usuario /caminho/para/gccreporter
chmod 600 .env
```

### Serviço não inicia
```bash
sudo journalctl -u gccreporter -n 50
# Verificar erros e ajustar configuração
```

## 📝 Próximos Passos

1. Testar todas as funcionalidades
2. Configurar backup automático
3. Monitorar logs regularmente
4. Configurar alertas (opcional)











