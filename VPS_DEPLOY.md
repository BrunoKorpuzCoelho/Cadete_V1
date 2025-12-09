# Configuração VPS - HTTP Permanente

## ✅ Aplicação Configurada para HTTP

A aplicação está **permanentemente configurada para HTTP** - não requer SSL/HTTPS.

## Deploy na VPS

### 1. Pull das alterações:

```bash
cd /caminho/do/projeto
git pull
```

### 2. Certifique-se que tem o `.env` básico:

```bash
nano .env
```

**Configuração mínima necessária:**

```env
# Flask Configuration
FLASK_ENV=production
FLASK_DEBUG=False

# Database
DATABASE_URI=sqlite:///instance/test.db

# Secret Key (gere uma nova)
SECRET_KEY=seu-secret-key-aqui

# Session (opcional - já tem defaults para HTTP)
PERMANENT_SESSION_LIFETIME=3600
```

### 3. Reinicie o serviço:

```bash
sudo systemctl restart cadete
# ou
pkill gunicorn && gunicorn --config gunicorn_config.py wsgi:app
```

---

## ✨ Não precisa configurar:

- ❌ SESSION_COOKIE_SECURE - sempre False (hardcoded)
- ❌ PREFERRED_URL_SCHEME - sempre http (hardcoded)
- ❌ Certificados SSL
- ❌ Nginx com HTTPS

**A aplicação funciona diretamente com HTTP em qualquer ambiente!**
