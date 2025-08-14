import sys
sys.dont_write_bytecode = True

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, logout_user, current_user, login_user
import os
import base64
from extensions import db, login_manager
from instance.install_core import install_core
from datetime import datetime
from instance.base import Expenses, Employee, Company

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

@app.route('/main-menu/<company_id>')
@login_required
def index(company_id):
    if company_id:
        return render_template('dashboard.html', company_id=company_id)
    else:
        return redirect(url_for('company'))
    
@app.route('/')
@login_required
def main():
    return render_template("login.html")

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
            return redirect(url_for("company"))
    
    return render_template("login.html")

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login')) 

@app.route('/expenses/<int:company_id>')
@login_required
def expenses(company_id):
    page = request.args.get('page', 1, type=int)  
    per_page = 100  
    user_type = current_user.type
    
    pagination = Expenses.query.filter_by(company_id=company_id).order_by(Expenses.create_date.desc()).paginate(page=page, per_page=per_page, error_out=False)
    
    all_expenses = pagination.items

    return render_template('expenses.html', user_type=user_type, expenses=all_expenses, pagination=pagination, company_id=company_id)

@app.route('/add-expenses', methods=['POST'])
@login_required
def add_expense():
    try:
        company_id = request.form.get('company_id')
        
        if not company_id:
            flash('❌ ID da empresa não fornecido.', 'error')
            return redirect(url_for('company'))
            
        transaction_type = request.form.get('transaction_type')
        description = request.form.get('description')
        gross_value = float(request.form.get('gross_value'))
        iva_rate = float(request.form.get('iva_rate'))
        iva_value = float(request.form.get('iva_value'))
        net_value = float(request.form.get('net_value'))
        
        if not all([transaction_type, description, gross_value >= 0, iva_rate >= 0]):
            flash('❌ Por favor, preencha todos os campos corretamente.', 'error')
            return redirect(url_for('expenses', company_id=company_id))
        
        new_expense = Expenses(
            transaction_type=transaction_type,
            description=description,
            gross_value=gross_value,
            iva_rate=iva_rate,
            iva_value=iva_value,
            net_value=net_value,
            user_id=current_user.id,
            company_id=int(company_id) 
        )
        
        db.session.add(new_expense)
        db.session.commit()
        
        flash('✅ Transação adicionada com sucesso!', 'success')
        return redirect(url_for('expenses', company_id=company_id))
        
    except Exception as e:
        db.session.rollback()
        company_id = request.form.get('company_id')
        if company_id:
            flash(f'❌ Erro ao adicionar transação: {str(e)}', 'error')
            return redirect(url_for('expenses', company_id=company_id))
        else:
            flash(f'❌ Erro ao adicionar transação: {str(e)}', 'error')
            return redirect(url_for('company'))
    
@app.route('/delete-expense/<int:expense_id>', methods=['POST'])
@login_required
def delete_expense(expense_id):
    try:
        expense = Expenses.query.get_or_404(expense_id)
        
        if expense.user_id != current_user.id:
            return jsonify({'success': False, 'message': 'Acesso negado'}), 403
        
        company = Company.query.get(expense.company_id)
        if company and company.user_id != current_user.id:
            return jsonify({'success': False, 'message': 'Acesso negado à empresa'}, 403)
        
        db.session.delete(expense)
        db.session.commit()
        
        return jsonify({'success': True, 'company_id': expense.company_id}), 200
        
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
            'net_value': expense.net_value,
            'company_id': expense.company_id 
        }
        
        return jsonify({'success': True, 'expense': expense_dict})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/update-expense/<int:expense_id>', methods=['POST'])
@login_required
def update_expense(expense_id):
    try:
        expense = Expenses.query.get_or_404(expense_id)
        
        company_id = request.form.get('company_id')
        if not company_id:
            company_id = expense.company_id
        
        if expense.user_id != current_user.id and current_user.type != 'Admin':
            flash('❌ Você não tem permissão para editar esta transação.', 'error')
            return redirect(url_for('expenses', company_id=company_id))
        
        expense.transaction_type = request.form.get('transaction_type')
        expense.description = request.form.get('description')
        expense.gross_value = float(request.form.get('gross_value'))
        expense.iva_rate = float(request.form.get('iva_rate'))
        expense.iva_value = float(request.form.get('iva_value'))
        expense.net_value = float(request.form.get('net_value'))
        
        db.session.commit()
        
        flash('✅ Transação atualizada com sucesso!', 'success')
        return redirect(url_for('expenses', company_id=company_id))
        
    except Exception as e:
        db.session.rollback()
        
        company_id = request.form.get('company_id')
        if not company_id and expense:
            company_id = expense.company_id
            
        flash(f'❌ Erro ao atualizar transação: {str(e)}', 'error')
        
        if company_id:
            return redirect(url_for('expenses', company_id=company_id))
        else:
            return redirect(url_for('company'))
    
@app.route('/employee/<int:company_id>')
@login_required
def employee(company_id):
    company = Company.query.get_or_404(company_id)
    return render_template('employee.html', company_id=company_id, company=company)

@app.route('/add-employee', methods=['POST'])
@login_required
def add_employee():
    try:
        name = request.form.get('employeeName')
        position = request.form.get('employeePosition')
        gross_salary = float(request.form.get('employeeSalary', 0))
        social_security_rate = float(request.form.get('employeeSocialSecurity', 11.0))
        employer_social_security_rate = float(request.form.get('employerSocialSecurity', 23.75))
        irs_rate = float(request.form.get('employeeIRS', 0))
        extra_payment = float(request.form.get('extraPayment', 0))
        extra_payment_description = request.form.get('extraPaymentDescription', '')
        company_id = request.form.get('company_id')
        
        if not all([name, position, gross_salary > 0, company_id]):
            return jsonify({
                'success': False, 
                'message': 'Por favor, preencha todos os campos obrigatórios corretamente.'
            }), 400
        
        company = Company.query.get(company_id)
        if not company or company.user_id != current_user.id:
            return jsonify({
                'success': False,
                'message': 'Empresa inválida ou sem permissão de acesso.'
            }), 403
        
        new_employee = Employee(
            name=name,
            position=position,
            gross_salary=gross_salary,
            social_security_rate=social_security_rate,
            employer_social_security_rate=employer_social_security_rate,
            irs_rate=irs_rate,
            extra_payment=extra_payment,
            extra_payment_description=extra_payment_description,
            company_id=int(company_id)
        )
        
        db.session.add(new_employee)
        db.session.commit()
        
        employee_data = {
            'id': new_employee.id,
            'name': new_employee.name,
            'position': new_employee.position,
            'gross_salary': new_employee.gross_salary,
            'social_security_rate': new_employee.social_security_rate,
            'employer_social_security_rate': new_employee.employer_social_security_rate,
            'irs_rate': new_employee.irs_rate,
            'extra_payment': new_employee.extra_payment,
            'extra_payment_description': new_employee.extra_payment_description,
            'is_active': new_employee.is_active,
            'company_id': new_employee.company_id
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

@app.route('/get-employees/<int:company_id>')
@login_required
def get_employees(company_id):
    try:
        company = Company.query.get_or_404(company_id)
        if company.user_id != current_user.id:
            return jsonify({
                'success': False,
                'message': 'Acesso negado a esta empresa.'
            }), 403
        
        employees = Employee.query.filter_by(company_id=company_id).all()
        employees_list = []
        
        for emp in employees:
            employees_list.append({
                'id': emp.id,
                'name': emp.name,
                'position': emp.position,
                'gross_salary': emp.gross_salary,
                'social_security_rate': emp.social_security_rate,
                'employer_social_security_rate': emp.employer_social_security_rate,
                'irs_rate': emp.irs_rate,
                'extra_payment': emp.extra_payment,
                'extra_payment_description': emp.extra_payment_description,
                'is_active': emp.is_active,
                'company_id': emp.company_id
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
        
        company = Company.query.get(employee.company_id)
        if not company or company.user_id != current_user.id:
            return jsonify({
                'success': False,
                'message': 'Acesso negado a este empregado.'
            }), 403
        
        company_id = request.form.get('company_id', employee.company_id)
        
        if int(company_id) != employee.company_id:
            new_company = Company.query.get(company_id)
            if not new_company or new_company.user_id != current_user.id:
                return jsonify({
                    'success': False,
                    'message': 'Acesso negado à empresa de destino.'
                }), 403
        
        employee.name = request.form.get('employeeName')
        employee.position = request.form.get('employeePosition')
        employee.gross_salary = float(request.form.get('employeeSalary', 0))
        employee.social_security_rate = float(request.form.get('employeeSocialSecurity', 11.0))
        employee.employer_social_security_rate = float(request.form.get('employerSocialSecurity', 23.75))
        employee.irs_rate = float(request.form.get('employeeIRS', 0))
        employee.extra_payment = float(request.form.get('extraPayment', 0))
        employee.extra_payment_description = request.form.get('extraPaymentDescription', '')
        employee.company_id = int(company_id)
        
        db.session.commit()
        
        employee_data = {
            'id': employee.id,
            'name': employee.name,
            'position': employee.position,
            'gross_salary': employee.gross_salary,
            'social_security_rate': employee.social_security_rate,
            'employer_social_security_rate': employee.employer_social_security_rate,
            'irs_rate': employee.irs_rate,
            'extra_payment': employee.extra_payment,
            'extra_payment_description': employee.extra_payment_description,
            'is_active': employee.is_active,
            'company_id': employee.company_id
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
        
        company = Company.query.get(employee.company_id)
        if not company or company.user_id != current_user.id:
            return jsonify({
                'success': False,
                'message': 'Acesso negado a este empregado.'
            }), 403
        
        company_id = employee.company_id
        
        db.session.delete(employee)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Empregado removido com sucesso!',
            'company_id': company_id
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
        
        company = Company.query.get(employee.company_id)
        if not company or company.user_id != current_user.id:
            return jsonify({
                'success': False,
                'message': 'Acesso negado a este empregado.'
            }), 403
        
        employee_data = {
            'id': employee.id,
            'name': employee.name,
            'position': employee.position,
            'gross_salary': employee.gross_salary,
            'social_security_rate': employee.social_security_rate,
            'employer_social_security_rate': employee.employer_social_security_rate,
            'irs_rate': employee.irs_rate,
            'extra_payment': employee.extra_payment,
            'extra_payment_description': employee.extra_payment_description,
            'is_active': employee.is_active,
            'company_id': employee.company_id
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
        
        company = Company.query.get(employee.company_id)
        if not company or company.user_id != current_user.id:
            return jsonify({
                'success': False,
                'message': 'Acesso negado a este empregado.'
            }), 403
        
        new_status = request.form.get('is_active', '')
        
        if new_status.lower() == 'true':
            employee.is_active = True
        else:
            employee.is_active = False
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Status do empregado atualizado com sucesso!',
            'is_active': employee.is_active,
            'company_id': employee.company_id
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Erro ao atualizar status do empregado: {str(e)}'
        }), 500
    
@app.route('/dashboard/<int:company_id>')
@login_required
def dashboard(company_id):
    company = Company.query.get_or_404(company_id)
    return render_template('dashboard_viewer.html', company_id=company_id, company=company)

@app.route('/company')
@login_required
def company():
    companies = Company.query.filter_by(user_id=current_user.id).all()
    return render_template('company.html', companies=companies)

@app.route('/add-company', methods=['POST'])
@login_required
def add_company():
    try:
        name = request.form.get('name')
        location = request.form.get('location', '')
        relationship_type = request.form.get('relationship_type', '')
        tax_id = request.form.get('tax_id')
        phone = request.form.get('phone')
        email = request.form.get('email')
        contact_person = request.form.get('contact_person')
        notes = request.form.get('notes')
        
        if not name:
            return jsonify({
                'success': False,
                'message': 'O nome da empresa é obrigatório.'
            }), 400
            
        new_company = Company(
            name=name,
            location=location,
            relationship_type=relationship_type,
            user_id=current_user.id,
            tax_id=tax_id,
            phone=phone,
            email=email,
            contact_person=contact_person,
            notes=notes,
            is_active=True
        )
        
        db.session.add(new_company)
        db.session.commit()
        
        company_data = {
            'id': new_company.id,
            'name': new_company.name,
            'location': new_company.location,
            'relationship_type': new_company.relationship_type,
            'tax_id': new_company.tax_id
        }
        
        return jsonify({
            'success': True,
            'message': 'Empresa criada com sucesso!',
            'company': company_data
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Erro ao criar empresa: {str(e)}'
        }), 500

@app.route('/get-companies')
@login_required
def get_companies():
    try:
        companies = Company.query.filter_by(user_id=current_user.id).all()
        companies_list = []
        
        for company in companies:
            companies_list.append({
                'id': company.id,
                'name': company.name,
                'location': company.location,
                'relationship_type': company.relationship_type,
                'tax_id': company.tax_id,
                'is_active': company.is_active
            })
        
        return jsonify({
            'success': True,
            'companies': companies_list
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao buscar empresas: {str(e)}'
        }), 500
    
@app.route('/get-company/<int:company_id>')
@login_required
def get_company(company_id):
    try:
        company = Company.query.get_or_404(company_id)
        
        if company.user_id != current_user.id:
            return jsonify({
                'success': False,
                'message': 'Acesso negado a esta empresa.'
            }), 403
        
        company_data = {
            'id': company.id,
            'name': company.name,
            'location': company.location,
            'relationship_type': company.relationship_type,
            'tax_id': company.tax_id,
            'phone': company.phone,
            'email': company.email,
            'contact_person': company.contact_person,
            'notes': company.notes,
            'is_active': company.is_active
        }
        
        return jsonify({
            'success': True,
            'company': company_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao buscar empresa: {str(e)}'
        }), 500

@app.route('/update-company/<int:company_id>', methods=['POST'])
@login_required
def update_company(company_id):
    try:
        company = Company.query.get_or_404(company_id)
        
        if company.user_id != current_user.id:
            return jsonify({
                'success': False,
                'message': 'Acesso negado a esta empresa.'
            }), 403
        
        company.name = request.form.get('name')
        company.location = request.form.get('location', '')
        company.relationship_type = request.form.get('relationship_type', '')
        company.tax_id = request.form.get('tax_id')
        company.phone = request.form.get('phone')
        company.email = request.form.get('email')
        company.contact_person = request.form.get('contact_person')
        company.notes = request.form.get('notes')
        
        db.session.commit()
        
        company_data = {
            'id': company.id,
            'name': company.name,
            'location': company.location,
            'relationship_type': company.relationship_type,
            'tax_id': company.tax_id
        }
        
        return jsonify({
            'success': True,
            'message': 'Empresa atualizada com sucesso!',
            'company': company_data
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Erro ao atualizar empresa: {str(e)}'
        }), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        install_core()
    
    app.run(debug=True, host='0.0.0.0', port=5000)