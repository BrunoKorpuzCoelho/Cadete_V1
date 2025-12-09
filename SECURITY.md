# Security Guide

## Vulnerabilidades Corrigidas

Este documento descreve as vulnerabilidades críticas que foram corrigidas e as medidas de segurança implementadas.

### 1. Password Hashing Implementado ✅

**Problema:** Passwords eram armazenadas em texto plano no banco de dados.

**Solução:**
- Implementado hash de passwords usando Werkzeug (PBKDF2-SHA256)
- Método `set_password()` e `check_password()` adicionados à classe User
- Salt de 16 bytes para cada password

**Arquivos alterados:**
- `instance/base.py`: Adicionados métodos de hash
- `instance/seeds/users.py`: Criação de users com passwords hasheadas
- `app.py`: Login usando `check_password()` em vez de comparação direta

### 2. SECRET_KEY Fixa e Segura ✅

**Problema:** SECRET_KEY era gerada aleatoriamente a cada restart com `os.urandom(24)`, invalidando todas as sessões.

**Solução:**
- SECRET_KEY armazenada no arquivo `.env`
- Chave de 64 caracteres hexadecimais (256 bits)
- `.env` adicionado ao `.gitignore`

**Como gerar nova SECRET_KEY:**
```python
python -c "import secrets; print(secrets.token_hex(32))"
```

### 3. Debug Mode Desativado em Produção ✅

**Problema:** `debug=True` expõe informações sensíveis e permite execução de código.

**Solução:**
- Debug mode controlado por variável de ambiente `FLASK_DEBUG`
- Default: `False` (produção)
- Aviso exibido se debug estiver ativo

### 4. CSRF Protection Implementada ✅

**Problema:** Sem proteção contra Cross-Site Request Forgery.

**Solução:**
- Flask-WTF CSRF protection habilitada globalmente
- Tokens CSRF automáticos em todos os formulários
- Configuração em `config.py`

**Uso nos templates:**
```html
<form method="POST">
    {{ csrf_token() }}
    <!-- form fields -->
</form>
```

### 5. Rate Limiting no Login ✅

**Problema:** Sem limite de tentativas de login, permitindo ataques de força bruta.

**Solução:**
- Flask-Limiter implementado
- Login limitado a 5 tentativas por minuto por IP
- Limite global: 200 req/dia, 50 req/hora
- Conta bloqueada após 5 tentativas falhas (aumentado de 3)

### 6. Mensagens de Erro Genéricas ✅

**Problema:** Mensagens revelavam se usuário existia no sistema.

**Solução:**
- Todas as falhas de login usam mensagem genérica: "Credenciais inválidas"
- Não revela contador de tentativas falhas
- Apenas mostra bloqueio quando conta é bloqueada

## Configuração de Produção

### 1. Variáveis de Ambiente (.env)

```bash
# Copie o arquivo .env.example para .env
cp .env.example .env

# Gere uma nova SECRET_KEY
python -c "import secrets; print(secrets.token_hex(32))"

# Edite o .env com sua SECRET_KEY
nano .env
```

**Configurações importantes:**
- `SECRET_KEY`: Chave secreta única (NUNCA compartilhe)
- `FLASK_ENV=production`
- `FLASK_DEBUG=False`
- `SESSION_COOKIE_SECURE=True` (requer HTTPS)

### 2. Migração de Passwords Existentes

Se você já tem usuários com passwords em texto plano:

```bash
# IMPORTANTE: Faça backup do banco de dados primeiro!
cp instance/test.db instance/test.db.backup

# Execute o script de migração
python migrate_passwords.py
```

O script irá:
1. Identificar passwords em texto plano
2. Converter para hash seguro
3. Manter as passwords originais funcionando

### 3. Instalação de Dependências

```bash
# Instale as novas dependências de segurança
pip install -r requirements.txt
```

Novas dependências:
- `Flask-WTF`: CSRF protection
- `Flask-Limiter`: Rate limiting
- `python-dotenv`: Variáveis de ambiente
- `gunicorn`: WSGI server para produção

### 4. Deployment em Produção

#### Opção 1: Gunicorn Standalone

```bash
# Ative o ambiente virtual
source venv/bin/activate

# Execute com Gunicorn
gunicorn -c gunicorn_config.py wsgi:app
```

#### Opção 2: Gunicorn + Nginx (Recomendado)

1. Configure o Nginx:
```bash
sudo cp nginx.conf.example /etc/nginx/sites-available/cadete
sudo ln -s /etc/nginx/sites-available/cadete /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

2. Configure o Systemd:
```bash
sudo cp systemd.service.example /etc/systemd/system/cadete.service
# Edite o arquivo com os caminhos corretos
sudo systemctl daemon-reload
sudo systemctl enable cadete
sudo systemctl start cadete
```

## Checklist de Segurança

Antes de fazer deploy em produção:

- [ ] `.env` criado com SECRET_KEY única
- [ ] `FLASK_DEBUG=False` no `.env`
- [ ] Passwords migradas para hash (se necessário)
- [ ] `.env` adicionado ao `.gitignore`
- [ ] HTTPS configurado (SSL/TLS)
- [ ] Firewall configurado (apenas portas 80/443)
- [ ] Backup do banco de dados configurado
- [ ] Logs monitorados
- [ ] Nginx como reverse proxy (se aplicável)
- [ ] Systemd service configurado
- [ ] Testes realizados em staging

## Monitoramento de Segurança

### Logs Importantes

```bash
# Logs do Nginx
tail -f /var/log/nginx/cadete_access.log
tail -f /var/log/nginx/cadete_error.log

# Logs do Gunicorn (via systemd)
sudo journalctl -u cadete -f

# Verificar tentativas de login falhas
grep "Credenciais inválidas" /var/log/nginx/cadete_access.log
```

### Alertas Recomendados

- Múltiplas tentativas de login falhas do mesmo IP
- Contas sendo bloqueadas
- Erros 500 repetidos
- Rate limit sendo atingido frequentemente

## Atualizações de Segurança

Mantenha as dependências atualizadas:

```bash
# Verificar vulnerabilidades conhecidas
pip install safety
safety check

# Atualizar dependências (cuidado em produção)
pip list --outdated
```

## Recuperação de Conta Bloqueada

Para desbloquear uma conta manualmente:

```python
from app import app
from instance.base import User, db

with app.app_context():
    user = User.query.filter_by(username="username").first()
    user.is_locked = False
    user.failed_login_attempts = 0
    db.session.commit()
    print(f"User {user.username} unlocked")
```

## Suporte

Para questões de segurança, entre em contato:
- Telefone: +351 965 567 916
- Email: [seu-email-aqui]

## Histórico de Mudanças

- **2025-12-09**: Implementação inicial de segurança
  - Password hashing
  - CSRF protection
  - Rate limiting
  - Mensagens de erro genéricas
  - Configuração para produção
