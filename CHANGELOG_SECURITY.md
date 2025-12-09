# Security Update Changelog

## Versão 1.0.0 - Security Hardening (2025-12-09)

### 🔒 Vulnerabilidades Críticas Corrigidas

#### 1. Password Storage - CRÍTICO ✅
**Antes:**
- Passwords armazenadas em texto plano
- Comparação direta de strings
- Arquivo: `app.py` linha 66, `instance/base.py`

**Depois:**
- Hash PBKDF2-SHA256 com salt de 16 bytes
- Método `set_password()` e `check_password()` na classe User
- Migração automática com script `migrate_passwords.py`

**Arquivos modificados:**
- ✅ `instance/base.py`: Adicionados métodos de hash
- ✅ `instance/seeds/users.py`: Seeds com hash automático
- ✅ `app.py`: Login usando `check_password()`

#### 2. SECRET_KEY Aleatória - CRÍTICO ✅
**Antes:**
```python
app.config["SECRET_KEY"] = os.urandom(24)  # Nova a cada restart!
```

**Depois:**
```python
# config.py
SECRET_KEY = os.environ.get('SECRET_KEY')  # De .env
```

**Arquivos criados/modificados:**
- ✅ `.env`: SECRET_KEY fixa e segura
- ✅ `.env.example`: Template para novos ambientes
- ✅ `config.py`: Gerenciamento centralizado de configs
- ✅ `.gitignore`: Protege .env de commits

#### 3. Debug Mode em Produção - CRÍTICO ✅
**Antes:**
```python
app.run(debug=True, host='0.0.0.0', port=5000)  # SEMPRE True!
```

**Depois:**
```python
debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
app.run(debug=debug_mode, host=host, port=port)
```

**Configuração:**
- Default: `False` (produção segura)
- Warning exibido se `True`
- Controlado via `.env`

#### 4. CSRF Protection - CRÍTICO ✅
**Antes:**
- Nenhuma proteção CSRF
- Vulnerável a ataques cross-site

**Depois:**
```python
from flask_wtf.csrf import CSRFProtect
csrf = CSRFProtect(app)
```

**Implementação:**
- Flask-WTF CSRF habilitado globalmente
- Tokens automáticos em todos os formulários
- Configurado em `config.py`

**Uso nos templates:**
```html
<form method="POST">
    {{ csrf_token() }}
    <!-- form fields -->
</form>
```

#### 5. Rate Limiting - CRÍTICO ✅
**Antes:**
- Sem limite de tentativas
- Vulnerável a brute force

**Depois:**
```python
from flask_limiter import Limiter
limiter = Limiter(app, key_func=get_remote_address)

@app.route('/login')
@limiter.limit("5 per minute")
def login():
    # ...
```

**Proteções:**
- Login: 5 tentativas/minuto por IP
- Global: 200 req/dia, 50 req/hora
- Bloqueio de conta após 5 falhas (aumentado de 3)

#### 6. Mensagens de Erro Genéricas - ALTO ✅
**Antes:**
```python
flash("❌ Usuário não encontrado!")  # Revela existência
flash(f"❌ Senha incorreta! Tentativa {attempts}/3")  # Revela contador
```

**Depois:**
```python
flash("❌ Credenciais inválidas.")  # Genérica
# Não revela se usuário existe ou quantas tentativas
```

**Benefícios:**
- Não revela existência de usuários
- Não revela contador de tentativas
- Dificulta enumeração de contas

---

## 📁 Novos Arquivos Criados

### Configuração
- ✅ `.env` - Variáveis de ambiente (SECRET_KEY, configs)
- ✅ `.env.example` - Template para .env
- ✅ `config.py` - Configurações centralizadas por ambiente

### Deployment
- ✅ `wsgi.py` - Entry point WSGI
- ✅ `gunicorn_config.py` - Configuração Gunicorn
- ✅ `nginx.conf.example` - Configuração Nginx
- ✅ `systemd.service.example` - Service para Systemd

### Scripts
- ✅ `migrate_passwords.py` - Migração de passwords
- ✅ `setup.sh` - Setup automático

### Documentação
- ✅ `SECURITY.md` - Guia completo de segurança
- ✅ `DEPLOYMENT.md` - Guia de deployment
- ✅ `QUICKSTART.md` - Início rápido
- ✅ `CHANGELOG_SECURITY.md` - Este arquivo

---

## 🔄 Arquivos Modificados

### Código Principal
1. **app.py**
   - Import de Flask-WTF e Flask-Limiter
   - Configuração via `config.py`
   - Inicialização de CSRF e Limiter
   - Login seguro com `check_password()`
   - Mensagens de erro genéricas
   - Debug mode via environment
   - Rate limiting no login

2. **instance/base.py**
   - Import de `werkzeug.security`
   - Método `set_password()` adicionado
   - Método `check_password()` adicionado
   - Password hash automático no `__init__`

3. **instance/seeds/users.py**
   - Comentários sobre hashing automático
   - Print statements informativos
   - Documentação dos métodos

### Dependências
4. **requirements.txt**
   - ✅ Flask-WTF==1.2.1
   - ✅ Flask-Limiter==3.5.0
   - ✅ python-dotenv==1.0.0
   - ✅ gunicorn==21.2.0

### Configuração
5. **.gitignore**
   - Proteção de .env
   - Proteção de databases
   - Proteção de credentials
   - Arquivos Python e logs

---

## ✅ Checklist de Migração

Use este checklist para garantir que tudo está configurado:

### Antes de Iniciar
- [ ] Fazer backup do banco de dados: `cp instance/test.db instance/test.db.backup`
- [ ] Fazer backup do código atual (commit ou zip)
- [ ] Ler SECURITY.md e DEPLOYMENT.md

### Configuração Inicial
- [ ] Instalar novas dependências: `pip install -r requirements.txt`
- [ ] Criar arquivo .env: `cp .env.example .env`
- [ ] Gerar SECRET_KEY: `python -c "import secrets; print(secrets.token_hex(32))"`
- [ ] Adicionar SECRET_KEY ao .env
- [ ] Configurar FLASK_DEBUG=False no .env
- [ ] Verificar que .env não está no git: `git status`

### Migração de Dados
- [ ] Executar migração de passwords: `python migrate_passwords.py`
- [ ] Verificar que passwords foram migradas com sucesso
- [ ] Testar login com passwords antigas

### Testes de Funcionalidade
- [ ] Testar login com credenciais corretas
- [ ] Testar login com credenciais incorretas (deve mostrar mensagem genérica)
- [ ] Testar rate limiting (5 tentativas rápidas)
- [ ] Testar bloqueio de conta (5 falhas consecutivas)
- [ ] Testar todas as funcionalidades principais
- [ ] Verificar que formulários têm CSRF token
- [ ] Testar criação de novo usuário

### Segurança
- [ ] Verificar que debug=False
- [ ] Verificar que SECRET_KEY é fixa (reiniciar app, session continua válida)
- [ ] Verificar que .env não está no repositório
- [ ] Alterar passwords padrão (cubix e cadete)
- [ ] Verificar logs não expõem informações sensíveis

### Produção (se aplicável)
- [ ] Configurar HTTPS/SSL
- [ ] Configurar Nginx como reverse proxy
- [ ] Configurar Systemd service
- [ ] Configurar backups automáticos
- [ ] Configurar monitoramento
- [ ] Configurar firewall
- [ ] Testar em ambiente de staging primeiro

---

## 🔐 Níveis de Segurança Atingidos

| Vulnerabilidade | Antes | Depois | Impacto |
|----------------|-------|--------|---------|
| Password Storage | ❌ Texto plano | ✅ PBKDF2-SHA256 | CRÍTICO |
| SECRET_KEY | ❌ Aleatória | ✅ Fixa e segura | CRÍTICO |
| Debug Mode | ❌ Sempre True | ✅ False em prod | CRÍTICO |
| CSRF Protection | ❌ Nenhuma | ✅ Flask-WTF | CRÍTICO |
| Rate Limiting | ❌ Ilimitado | ✅ 5/min login | CRÍTICO |
| Error Messages | ❌ Específicas | ✅ Genéricas | ALTO |
| Session Security | ⚠️ Básica | ✅ HTTPOnly, Secure | MÉDIO |
| HTTPS Enforcement | ❌ Não | ✅ Nginx config | ALTO |

---

## 📊 Comparação de Código

### Login - Antes vs Depois

**ANTES (INSEGURO):**
```python
@app.route('/login', methods=["GET", "POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")

    user = User.query.filter_by(username=username).first()

    if not user:
        flash("❌ Usuário não encontrado!", "error")  # ❌ Revela info

    elif user.password != password:  # ❌ Comparação texto plano
        user.failed_login_attempts += 1
        flash(f"❌ Senha incorreta! Tentativa {user.failed_login_attempts}/3")  # ❌ Revela contador
```

**DEPOIS (SEGURO):**
```python
@app.route('/login', methods=["GET", "POST"])
@limiter.limit("5 per minute")  # ✅ Rate limiting
def login():
    username = request.form.get("username")
    password = request.form.get("password")

    user = User.query.filter_by(username=username).first()

    if not user:
        flash("❌ Credenciais inválidas.", "error")  # ✅ Genérica

    elif not user.check_password(password):  # ✅ Hash comparison
        user.failed_login_attempts += 1
        flash("❌ Credenciais inválidas.", "error")  # ✅ Não revela info
```

---

## 🚀 Próximos Passos Recomendados

1. **Imediato** (Agora)
   - Executar migração de passwords
   - Alterar passwords padrão
   - Verificar .env configurado

2. **Curto Prazo** (Esta Semana)
   - Implementar 2FA (Two-Factor Authentication)
   - Adicionar logs de auditoria
   - Configurar backups automáticos

3. **Médio Prazo** (Este Mês)
   - Implementar recuperação de password
   - Adicionar política de expiração de passwords
   - Configurar monitoring/alertas

4. **Longo Prazo** (Próximos 3 Meses)
   - Migrar para PostgreSQL
   - Implementar Redis para sessions
   - Adicionar WAF (ModSecurity)
   - Penetration testing

---

## 📞 Suporte

Dúvidas sobre a migração de segurança:
- **Documentação**: Veja SECURITY.md e DEPLOYMENT.md
- **Telefone**: +351 965 567 916

---

**Versão**: 1.0.0 - Security Hardening
**Data**: 2025-12-09
**Status**: ✅ Pronto para Produção
