import sys
sys.dont_write_bytecode = True

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, logout_user, current_user, login_user
import os
import base64
from extensions import db, login_manager
from instance.install_core import install_core
from datetime import datetime
from instance.base import Expenses, Employee

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
    page = request.args.get('page', 1, type=int)  
    per_page = 100  
    user_type = current_user.type
    
    pagination = Expenses.query.order_by(Expenses.create_date.desc()).paginate(page=page, per_page=per_page, error_out=False)
    
    all_expenses = pagination.items
    
    return render_template('expenses.html',  user_type=user_type,  expenses=all_expenses, pagination=pagination)

@app.route('/add-expenses', methods=['POST'])
@login_required
def add_expense():
    try:
        transaction_type = request.form.get('transaction_type')
        description = request.form.get('description')
        gross_value = float(request.form.get('gross_value'))
        iva_rate = float(request.form.get('iva_rate'))
        iva_value = float(request.form.get('iva_value'))
        net_value = float(request.form.get('net_value'))
        
        if not all([transaction_type, description, gross_value >= 0, iva_rate >= 0]):
            flash('❌ Por favor, preencha todos os campos corretamente.', 'error')
            return redirect(url_for('expenses'))
        
        new_expense = Expenses(
            transaction_type=transaction_type,
            description=description,
            gross_value=gross_value,
            iva_rate=iva_rate,
            iva_value=iva_value,
            net_value=net_value,
            user_id=current_user.id
        )
        
        db.session.add(new_expense)
        db.session.commit()
        
        flash('✅ Transação adicionada com sucesso!', 'success')
        return redirect(url_for('expenses'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Erro ao adicionar transação: {str(e)}', 'error')
        return redirect(url_for('expenses'))
    
@app.route('/delete-expense/<int:expense_id>', methods=['POST'])
@login_required
def delete_expense(expense_id):
    try:
        expense = Expenses.query.get_or_404(expense_id)
        
        if expense.user_id != current_user.id:
            return jsonify({'success': False, 'message': 'Acesso negado'}), 403
        
        db.session.delete(expense)
        db.session.commit()
        
        return jsonify({'success': True}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
    
@app.route('/get-expense/<int:expense_id>')
@login_required
def get_expense(expense_id):
    try:
        expense = Expenses.query.get_or_404(expense_id)
        
        if expense.user_id != current_user.id and current_user.type != 'Admin':
            return jsonify({'success': False, 'message': 'Acesso negado'}), 403
        
        expense_dict = {
            'id': expense.id,
            'transaction_type': expense.transaction_type,
            'description': expense.description,
            'gross_value': expense.gross_value,
            'iva_rate': expense.iva_rate,
            'iva_value': expense.iva_value,
            'net_value': expense.net_value
        }
        
        return jsonify({'success': True, 'expense': expense_dict})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/update-expense/<int:expense_id>', methods=['POST'])
@login_required
def update_expense(expense_id):
    try:
        expense = Expenses.query.get_or_404(expense_id)
        
        if expense.user_id != current_user.id and current_user.type != 'Admin':
            flash('❌ Você não tem permissão para editar esta transação.', 'error')
            return redirect(url_for('expenses'))
        
        expense.transaction_type = request.form.get('transaction_type')
        expense.description = request.form.get('description')
        expense.gross_value = float(request.form.get('gross_value'))
        expense.iva_rate = float(request.form.get('iva_rate'))
        expense.iva_value = float(request.form.get('iva_value'))
        expense.net_value = float(request.form.get('net_value'))
        
        db.session.commit()
        
        flash('✅ Transação atualizada com sucesso!', 'success')
        return redirect(url_for('expenses'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Erro ao atualizar transação: {str(e)}', 'error')
        return redirect(url_for('expenses'))
    
@app.route('/employee')
@login_required
def employee():
    return render_template('employee.html')

@app.route('/add-employee', methods=['POST'])
@login_required
def add_employee():
    try:
        name = request.form.get('employeeName')
        position = request.form.get('employeePosition')
        gross_salary = float(request.form.get('employeeSalary', 0))
        social_security_rate = float(request.form.get('employeeSocialSecurity', 11.0))
        
        if not name or gross_salary <= 0:
            return jsonify({
                'success': False, 
                'message': 'Por favor, preencha todos os campos obrigatórios corretamente.'
            }), 400
        
        new_employee = Employee(
            name=name,
            position=position,
            gross_salary=gross_salary,
            social_security_rate=social_security_rate
        )
        
        db.session.add(new_employee)
        db.session.commit()
        
        employee_data = {
            'id': new_employee.id,
            'name': new_employee.name,
            'position': new_employee.position,
            'gross_salary': new_employee.gross_salary,
            'social_security_rate': new_employee.social_security_rate,
            'is_active': new_employee.is_active
        }
        
        return jsonify({
            'success': True, 
            'message': 'Empregado adicionado com sucesso!',
            'employee': employee_data
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False, 
            'message': f'Erro ao adicionar empregado: {str(e)}'
        }), 500

@app.route('/get-employees')
@login_required
def get_employees():
    try:
        employees = Employee.query.all()
        employees_list = []
        
        for emp in employees:
            employees_list.append({
                'id': emp.id,
                'name': emp.name,
                'position': emp.position,
                'gross_salary': emp.gross_salary,
                'social_security_rate': emp.social_security_rate,
                'is_active': emp.is_active
            })
        
        return jsonify({
            'success': True,
            'employees': employees_list
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao buscar empregados: {str(e)}'
        }), 500
    
@app.route('/update-employee/<int:employee_id>', methods=['POST'])
@login_required
def update_employee(employee_id):
    try:
        employee = Employee.query.get_or_404(employee_id)
        
        employee.name = request.form.get('employeeName')
        employee.position = request.form.get('employeePosition')
        employee.gross_salary = float(request.form.get('employeeSalary', 0))
        employee.social_security_rate = float(request.form.get('employeeSocialSecurity', 11.0))
        
        db.session.commit()
        
        employee_data = {
            'id': employee.id,
            'name': employee.name,
            'position': employee.position,
            'gross_salary': employee.gross_salary,
            'social_security_rate': employee.social_security_rate,
            'is_active': employee.is_active
        }
        
        return jsonify({
            'success': True,
            'message': 'Empregado atualizado com sucesso!',
            'employee': employee_data
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Erro ao atualizar empregado: {str(e)}'
        }), 500
    
@app.route('/delete-employee/<int:employee_id>', methods=['POST'])
@login_required
def delete_employee(employee_id):
    try:
        employee = Employee.query.get_or_404(employee_id)
        
        db.session.delete(employee)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Empregado removido com sucesso!'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Erro ao remover empregado: {str(e)}'
        }), 500
    
@app.route('/get-employee/<int:employee_id>')
@login_required
def get_employee(employee_id):
    try:
        employee = Employee.query.get_or_404(employee_id)
        
        employee_data = {
            'id': employee.id,
            'name': employee.name,
            'position': employee.position,
            'gross_salary': employee.gross_salary,
            'social_security_rate': employee.social_security_rate,
            'is_active': employee.is_active
        }
        
        return jsonify({
            'success': True,
            'employee': employee_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao buscar empregado: {str(e)}'
        }), 500
    
@app.route('/toggle-employee-status/<int:employee_id>', methods=['POST'])
@login_required
def toggle_employee_status(employee_id):
    try:
        employee = Employee.query.get_or_404(employee_id)
        new_status = request.form.get('is_active', '')
        
        if new_status.lower() == 'true':
            employee.is_active = True
        else:
            employee.is_active = False
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Status do empregado atualizado com sucesso!',
            'is_active': employee.is_active
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Erro ao atualizar status do empregado: {str(e)}'
        }), 500
    
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard_viewer.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        install_core()
    
    app.run(debug=True, host='0.0.0.0', port=5000)