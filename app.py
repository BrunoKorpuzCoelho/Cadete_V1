from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import login_required, logout_user, current_user, login_user
import os
import base64
from extensions import db, login_manager
from instance.install_core import install_core
from datetime import datetime

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))

app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(basedir, 'instance', 'test.db')}"
app.config["SECRET_KEY"] = os.urandom(24)

db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = "login"  

@login_manager.user_loader
def load_user(user_id):
    from instance.base import User
    return User.query.get(int(user_id))

@app.route('/')
@login_required
def index():
    return render_template('dashboard.html')

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        from instance.base import User
        user = User.query.filter_by(username=username).first()

        if not user:
            flash("❌ Usuário não encontrado!", "error")
            return render_template("login.html")
        
        elif user.is_locked:
            flash("🚫 Usuário bloqueado! Entre em contato com o suporte.", "error")
            return render_template("login.html")
        
        elif user.password != password:
            if user.failed_login_attempts is None:
                user.failed_login_attempts = 0
            
            user.failed_login_attempts += 1

            if user.failed_login_attempts >= 3:
                user.is_locked = True
                flash(f"❌ Muitas tentativas falhas! Usuário bloqueado.", "error")
            else:
                flash(f"❌ Senha incorreta! Tentativa {user.failed_login_attempts}/3", "error")
            
            db.session.commit()
            return render_template("login.html")
        
        else:
            user.failed_login_attempts = 0
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            login_user(user)
            return redirect(url_for("index"))
    
    return render_template("login.html")

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login')) 

@app.route('/expenses')
@login_required
def expenses():
    return render_template('expenses.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        install_core()
    
    app.run(debug=True)