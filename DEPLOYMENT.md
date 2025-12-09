# Deployment Guide - Cadete Application

## Guia Completo de Deploy em Produção

### Pré-requisitos

- Python 3.8+
- pip
- virtualenv
- Nginx (recomendado)
- Supervisor ou Systemd
- Certificado SSL/TLS (Let's Encrypt recomendado)

## Instalação Passo a Passo

### 1. Preparar o Servidor

```bash
# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependências
sudo apt install python3-pip python3-venv nginx git -y

# Criar usuário para a aplicação (opcional mas recomendado)
sudo useradd -m -s /bin/bash cadete
sudo usermod -aG www-data cadete
```

### 2. Clonar e Configurar Aplicação

```bash
# Clonar repositório
cd /var/www
sudo git clone https://github.com/seu-usuario/Cadete_V1.git
sudo chown -R cadete:www-data Cadete_V1
cd Cadete_V1

# Criar ambiente virtual
sudo -u cadete python3 -m venv venv
sudo -u cadete venv/bin/pip install --upgrade pip

# Instalar dependências
sudo -u cadete venv/bin/pip install -r requirements.txt
```

### 3. Configurar Variáveis de Ambiente

```bash
# Copiar template
sudo -u cadete cp .env.example .env

# Gerar SECRET_KEY
sudo -u cadete bash -c "python3 -c \"import secrets; print('SECRET_KEY=' + secrets.token_hex(32))\" >> .env"

# Editar configurações
sudo -u cadete nano .env
```

Configure o `.env`:
```bash
SECRET_KEY=sua-chave-super-secreta-aqui-64-caracteres
FLASK_ENV=production
FLASK_DEBUG=False
FLASK_HOST=127.0.0.1
FLASK_PORT=8000

DATABASE_URI=sqlite:///instance/test.db

RATELIMIT_STORAGE_URL=memory://

SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Lax
PERMANENT_SESSION_LIFETIME=3600
```

### 4. Inicializar Banco de Dados

```bash
# Criar diretório instance se não existir
sudo -u cadete mkdir -p instance

# Inicializar banco de dados
sudo -u cadete venv/bin/python app.py
# Pressione Ctrl+C após ver "Running on..."

# Migrar passwords existentes (se necessário)
sudo -u cadete venv/bin/python migrate_passwords.py
```

### 5. Configurar Gunicorn

O arquivo `gunicorn_config.py` já está configurado. Teste:

```bash
# Testar Gunicorn
sudo -u cadete venv/bin/gunicorn -c gunicorn_config.py wsgi:app

# Se funcionar, pressione Ctrl+C
```

### 6. Configurar Systemd Service

```bash
# Copiar arquivo de serviço
sudo cp systemd.service.example /etc/systemd/system/cadete.service

# Editar com os caminhos corretos
sudo nano /etc/systemd/system/cadete.service
```

Atualizar os caminhos:
```ini
WorkingDirectory=/var/www/Cadete_V1
EnvironmentFile=/var/www/Cadete_V1/.env
ExecStart=/var/www/Cadete_V1/venv/bin/gunicorn -c gunicorn_config.py wsgi:app
```

Habilitar e iniciar serviço:
```bash
sudo systemctl daemon-reload
sudo systemctl enable cadete
sudo systemctl start cadete
sudo systemctl status cadete
```

### 7. Configurar Nginx

#### 7.1 Instalar Certbot (Let's Encrypt)

```bash
sudo apt install certbot python3-certbot-nginx -y

# Obter certificado SSL
sudo certbot --nginx -d seu-dominio.com -d www.seu-dominio.com
```

#### 7.2 Configurar Nginx

```bash
# Copiar configuração
sudo cp nginx.conf.example /etc/nginx/sites-available/cadete

# Editar com seu domínio
sudo nano /etc/nginx/sites-available/cadete
```

Atualizar:
- `server_name` para seu domínio
- Caminhos dos certificados SSL (se não usar certbot automático)
- Caminho para arquivos estáticos

```bash
# Criar symlink
sudo ln -s /etc/nginx/sites-available/cadete /etc/nginx/sites-enabled/

# Remover configuração padrão
sudo rm /etc/nginx/sites-enabled/default

# Testar configuração
sudo nginx -t

# Recarregar Nginx
sudo systemctl reload nginx
```

### 8. Configurar Firewall

```bash
# UFW
sudo ufw allow 22/tcp      # SSH
sudo ufw allow 80/tcp      # HTTP
sudo ufw allow 443/tcp     # HTTPS
sudo ufw enable
sudo ufw status
```

### 9. Verificar Funcionamento

```bash
# Verificar serviço
sudo systemctl status cadete

# Verificar logs
sudo journalctl -u cadete -f

# Verificar Nginx
sudo systemctl status nginx
tail -f /var/log/nginx/cadete_access.log

# Testar aplicação
curl http://localhost:8000
curl https://seu-dominio.com
```

## Manutenção

### Atualizar Aplicação

```bash
cd /var/www/Cadete_V1

# Backup do banco de dados
sudo -u cadete cp instance/test.db instance/test.db.backup.$(date +%Y%m%d)

# Atualizar código
sudo -u cadete git pull

# Instalar novas dependências
sudo -u cadete venv/bin/pip install -r requirements.txt

# Reiniciar serviço
sudo systemctl restart cadete
```

### Backup

```bash
# Criar script de backup
sudo nano /usr/local/bin/backup-cadete.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/var/backups/cadete"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup banco de dados
cp /var/www/Cadete_V1/instance/test.db $BACKUP_DIR/test.db.$DATE

# Backup .env
cp /var/www/Cadete_V1/.env $BACKUP_DIR/.env.$DATE

# Manter apenas últimos 7 backups
find $BACKUP_DIR -name "test.db.*" -mtime +7 -delete
find $BACKUP_DIR -name ".env.*" -mtime +7 -delete

echo "Backup completed: $DATE"
```

```bash
# Tornar executável
sudo chmod +x /usr/local/bin/backup-cadete.sh

# Adicionar ao cron (diário às 2h)
sudo crontab -e
# Adicionar: 0 2 * * * /usr/local/bin/backup-cadete.sh
```

### Monitoramento

```bash
# Ver logs em tempo real
sudo journalctl -u cadete -f

# Ver erros específicos
sudo journalctl -u cadete --since "1 hour ago" | grep ERROR

# Verificar uso de recursos
htop
# ou
ps aux | grep gunicorn
```

### Troubleshooting

#### Serviço não inicia

```bash
# Ver logs detalhados
sudo journalctl -u cadete -n 100

# Verificar permissões
ls -la /var/www/Cadete_V1

# Testar manualmente
cd /var/www/Cadete_V1
sudo -u cadete venv/bin/python wsgi.py
```

#### Erro 502 Bad Gateway

```bash
# Verificar se Gunicorn está rodando
sudo systemctl status cadete

# Verificar porta
sudo netstat -tulpn | grep 8000

# Verificar logs Nginx
tail -f /var/log/nginx/cadete_error.log
```

#### Erro de CSRF Token

- Verificar se `SESSION_COOKIE_SECURE=True` e site está em HTTPS
- Limpar cookies do navegador
- Verificar configuração do Nginx (headers X-Forwarded-Proto)

#### Performance Issues

```bash
# Aumentar workers no gunicorn_config.py
workers = (cpu_count * 2) + 1

# Otimizar Nginx
# Adicionar cache, compressão, etc.
```

## Segurança Adicional

### 1. Fail2Ban

```bash
# Instalar
sudo apt install fail2ban

# Configurar para Nginx
sudo nano /etc/fail2ban/jail.local
```

```ini
[nginx-limit-req]
enabled = true
filter = nginx-limit-req
logpath = /var/log/nginx/cadete_error.log
maxretry = 5
findtime = 600
bantime = 3600
```

### 2. ModSecurity (WAF)

```bash
# Instalar ModSecurity para Nginx
sudo apt install libnginx-mod-security
```

### 3. Monitoramento Automático

Considere usar:
- Prometheus + Grafana
- New Relic
- DataDog
- Sentry para erros

## Performance

### 1. Redis para Rate Limiting

```bash
# Instalar Redis
sudo apt install redis-server

# Atualizar .env
RATELIMIT_STORAGE_URL=redis://localhost:6379
```

### 2. PostgreSQL (Opcional)

Para melhor performance em produção:

```bash
# Instalar PostgreSQL
sudo apt install postgresql postgresql-contrib

# Criar banco de dados
sudo -u postgres createdb cadete
sudo -u postgres createuser cadete

# Atualizar .env
DATABASE_URI=postgresql://cadete:senha@localhost/cadete
```

## Rollback

Se algo der errado:

```bash
# Parar serviço
sudo systemctl stop cadete

# Restaurar backup
sudo -u cadete cp /var/backups/cadete/test.db.YYYYMMDD /var/www/Cadete_V1/instance/test.db

# Reverter código
cd /var/www/Cadete_V1
sudo -u cadete git reset --hard HEAD~1

# Reiniciar
sudo systemctl start cadete
```

## Contato

Suporte: +351 965 567 916
