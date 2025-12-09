# Quick Start Guide

## Início Rápido em 5 Minutos

### 1. Setup Automático (Recomendado)

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/Cadete_V1.git
cd Cadete_V1

# Execute o script de setup
chmod +x setup.sh
./setup.sh
```

O script irá:
- ✅ Criar ambiente virtual
- ✅ Instalar dependências
- ✅ Criar arquivo .env com SECRET_KEY única
- ✅ Configurar estrutura inicial

### 2. Setup Manual

```bash
# Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Instalar dependências
pip install -r requirements.txt

# Criar arquivo .env
cp .env.example .env

# Gerar SECRET_KEY e adicionar ao .env
python -c "import secrets; print('SECRET_KEY=' + secrets.token_hex(32))"

# Editar .env com a SECRET_KEY gerada
nano .env
```

### 3. Iniciar Aplicação

#### Modo Desenvolvimento

```bash
# Atualizar .env
FLASK_DEBUG=True

# Iniciar
python app.py
```

Acesse: http://localhost:5000

#### Modo Produção (Local)

```bash
# Atualizar .env
FLASK_DEBUG=False

# Iniciar com Gunicorn
gunicorn -c gunicorn_config.py wsgi:app
```

Acesse: http://localhost:8000

### 4. Login Inicial

**Credenciais padrão:**
- Admin: `cubix` / `cubix`
- Usuário: `cadete` / `cadete`

⚠️ **IMPORTANTE: Altere estas passwords imediatamente!**

## Estrutura do Projeto

```
Cadete_V1/
├── app.py                      # Aplicação principal
├── config.py                   # Configurações
├── wsgi.py                     # Entry point WSGI
├── instance/
│   ├── base.py                # Modelos de dados
│   └── seeds/
│       └── users.py           # Seeds de usuários
├── static/                    # Arquivos estáticos (CSS, JS)
├── templates/                 # Templates HTML
├── .env                       # Configurações (NÃO COMMITAR)
├── .env.example              # Template de configurações
├── requirements.txt          # Dependências Python
├── gunicorn_config.py       # Config Gunicorn
├── nginx.conf.example       # Config Nginx
├── systemd.service.example  # Config Systemd
├── migrate_passwords.py     # Script de migração
├── SECURITY.md             # Guia de segurança
├── DEPLOYMENT.md           # Guia de deployment
└── QUICKSTART.md           # Este arquivo
```

## Funcionalidades Principais

1. **Gestão de Empresas**: Criar e gerir múltiplas empresas
2. **Gestão de Despesas**: Registar receitas e despesas
3. **Gestão de Funcionários**: Controlo de colaboradores e salários
4. **Dashboard Financeiro**: Visualização de métricas e gráficos
5. **Relatórios**: Exportação de dados

## Segurança Implementada

✅ **Password Hashing**: PBKDF2-SHA256
✅ **CSRF Protection**: Flask-WTF
✅ **Rate Limiting**: 5 tentativas/minuto no login
✅ **SECRET_KEY Fixa**: De arquivo .env
✅ **Mensagens Genéricas**: Sem revelação de informação
✅ **Debug Off**: Por padrão em produção

## Comandos Úteis

```bash
# Migrar passwords existentes
python migrate_passwords.py

# Instalar novas dependências
pip install -r requirements.txt

# Congelar dependências
pip freeze > requirements.txt

# Criar backup do banco de dados
cp instance/test.db instance/test.db.backup

# Ver logs do Gunicorn
tail -f gunicorn.log

# Testar configuração
python -c "from config import get_config; print(get_config().__dict__)"
```

## Troubleshooting

### Erro: "SECRET_KEY not set"

```bash
# Verificar .env
cat .env | grep SECRET_KEY

# Se não existir, gerar nova
python -c "import secrets; print('SECRET_KEY=' + secrets.token_hex(32))" >> .env
```

### Erro: "No module named 'flask_wtf'"

```bash
# Reinstalar dependências
pip install -r requirements.txt
```

### Erro: "CSRF token missing"

- Verificar se `{{ csrf_token() }}` está nos formulários
- Limpar cookies do navegador
- Verificar se Flask-WTF está instalado

### Erro 500 ao fazer login

```bash
# Verificar se passwords foram migradas
python migrate_passwords.py

# Verificar logs
python app.py  # Ver output no console
```

## Próximos Passos

1. **Alterar passwords padrão** das contas cubix e cadete
2. **Configurar .env** com suas preferências
3. **Ler SECURITY.md** para entender as medidas de segurança
4. **Ler DEPLOYMENT.md** antes de fazer deploy em produção
5. **Configurar backups** do banco de dados

## Desenvolvimento

### Adicionar nova rota

```python
@app.route('/nova-rota')
@login_required
def nova_rota():
    return render_template('nova_rota.html')
```

### Adicionar novo modelo

```python
class NovoModelo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # ... campos
```

### Aplicar CSRF em formulários

```html
<form method="POST">
    {{ csrf_token() }}
    <!-- campos do formulário -->
</form>
```

## Suporte

- **Documentação Completa**: Veja SECURITY.md e DEPLOYMENT.md
- **Telefone**: +351 965 567 916
- **Issues**: GitHub Issues

## Licença

[Especificar licença aqui]

---

**Versão**: 1.0.0 (Segura)
**Última Atualização**: 2025-12-09
