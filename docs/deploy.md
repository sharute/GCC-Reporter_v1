# 🚀 Guia de Deploy para Produção

Este guia descreve como preparar e implantar o Sistema de Comunicados em um servidor de produção.

## 📋 Pré-requisitos

- Servidor Linux (Ubuntu/Debian recomendado)
- Python 3.8+
- Nginx (recomendado como proxy reverso)
- Certificado SSL (Let's Encrypt recomendado)

## 🔧 Configuração Inicial

### 1. Instalar Dependências do Sistema

```bash
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv nginx
```

### 2. Configurar Variáveis de Ambiente

```bash
cd /home/gccreporter
cp env.example .env
nano .env
```

Configure as seguintes variáveis:

```env
# Gere uma chave secreta forte
SECRET_KEY=SUA_CHAVE_SECRETA_AQUI

# Para produção, use PostgreSQL ou MySQL
DATABASE_URI=postgresql://user:password@localhost/comunicados

# Ou mantenha SQLite para pequenos volumes
DATABASE_URI=sqlite:///comunicados.db

# Configurações de produção
FLASK_DEBUG=false
FLASK_HOST=127.0.0.1
FLASK_PORT=5000
```

**Gerar SECRET_KEY:**
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 3. Criar Ambiente Virtual

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 4. Inicializar Banco de Dados

```bash
python3 app.py
# Pressione Ctrl+C após ver "Running on"
```

## 🌐 Configuração do Nginx

### 1. Criar Configuração do Nginx

```bash
sudo nano /etc/nginx/sites-available/gccreporter
```

Adicione:

```nginx
server {
    listen 80;
    server_name seu-dominio.com.br;

    # Redirecionar para HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name seu-dominio.com.br;

    ssl_certificate /etc/letsencrypt/live/seu-dominio.com.br/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/seu-dominio.com.br/privkey.pem;

    # Configurações SSL
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Tamanho máximo de upload
    client_max_body_size 10M;

    # Logs
    access_log /var/log/nginx/gccreporter_access.log;
    error_log /var/log/nginx/gccreporter_error.log;

    # Servir arquivos estáticos diretamente
    location /static {
        alias /home/gccreporter/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Proxy para aplicação Flask
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }
}
```

### 2. Habilitar Site

```bash
sudo ln -s /etc/nginx/sites-available/gccreporter /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## 🔒 Configurar SSL (Let's Encrypt)

```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d seu-dominio.com.br
```

## 🔄 Configurar Systemd (Serviço)

### 1. Criar Arquivo de Serviço

```bash
sudo nano /etc/systemd/system/gccreporter.service
```

Adicione:

```ini
[Unit]
Description=Sistema de Comunicados - Globo Tecnologia
After=network.target

[Service]
Type=simple
User=seu-usuario
WorkingDirectory=/home/gccreporter
Environment="PATH=/home/gccreporter/venv/bin"
ExecStart=/home/gccreporter/venv/bin/python app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 2. Habilitar e Iniciar Serviço

```bash
sudo systemctl daemon-reload
sudo systemctl enable gccreporter
sudo systemctl start gccreporter
sudo systemctl status gccreporter
```

## 🔐 Segurança

### 1. Permissões de Arquivos

```bash
chmod 600 /home/gccreporter/.env
chmod 600 /home/gccreporter/comunicados.db
chmod -R 755 /home/gccreporter/static
```

### 2. Firewall

```bash
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### 3. Backup Automático

Crie um script de backup:

```bash
nano /home/gccreporter/backup.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/backup/gccreporter"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

# Backup do banco de dados
cp /home/gccreporter/comunicados.db $BACKUP_DIR/comunicados_$DATE.db

# Backup dos uploads
tar -czf $BACKUP_DIR/uploads_$DATE.tar.gz /home/gccreporter/static/uploads

# Manter apenas últimos 7 dias
find $BACKUP_DIR -name "*.db" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
```

Adicione ao crontab:

```bash
crontab -e
# Backup diário às 2h da manhã
0 2 * * * /home/gccreporter/backup.sh
```

## 📊 Monitoramento

### Logs

- Aplicação: `/home/gccreporter/logs/audit.log`
- Nginx: `/var/log/nginx/gccreporter_*.log`
- Systemd: `sudo journalctl -u gccreporter -f`

### Verificar Status

```bash
# Status do serviço
sudo systemctl status gccreporter

# Verificar porta
sudo netstat -tuln | grep 5000

# Testar aplicação
curl http://localhost:5000
```

## 🔄 Atualizações

```bash
cd /home/gccreporter
source venv/bin/activate
git pull  # Se usar Git
pip install -r requirements.txt
sudo systemctl restart gccreporter
```

## ⚠️ Troubleshooting

### Serviço não inicia

```bash
sudo journalctl -u gccreporter -n 50
```

### Erro de permissão

```bash
sudo chown -R seu-usuario:seu-usuario /home/gccreporter
```

### Porta já em uso

```bash
sudo lsof -i :5000
# Matar processo se necessário
sudo kill -9 PID
```

## 📝 Checklist de Deploy

- [ ] Variáveis de ambiente configuradas (.env)
- [ ] SECRET_KEY gerada e configurada
- [ ] FLASK_DEBUG=false
- [ ] Banco de dados inicializado
- [ ] Nginx configurado e testado
- [ ] SSL/HTTPS configurado
- [ ] Serviço systemd criado e ativo
- [ ] Firewall configurado
- [ ] Backup automático configurado
- [ ] Logs sendo monitorados
- [ ] Testes de funcionalidade realizados

