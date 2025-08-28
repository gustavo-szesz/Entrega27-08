from flask import render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from config import app

from models import *
from formulario import FormularioEvento, FormularioCriarconta, FormularioLogin

"""
pip install flask, flask-wtf
flask_sqlalchemy, flask_login

"""


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    # Se o usuário já está logado, redireciona para dashboard
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
        
    formulario = FormularioCriarconta()

    if formulario.validate_on_submit():
        nome = formulario.nome.data
        email = formulario.email.data
        senha = formulario.senha.data
        
        # Verificar se usuário já existe
        usuario_existente = User.query.filter_by(username=email).first()
        
        if usuario_existente:
            flash('Este email já está em uso.')
        else:
            # Criar novo usuário com senha criptografada
            hash_senha = generate_password_hash(senha)
            novo_usuario = User(username=email, password=hash_senha)
            db.session.add(novo_usuario)
            db.session.commit()
            flash('Conta criada com sucesso!')
            return redirect(url_for('login'))

    return render_template('register.html', form=formulario)


@app.route('/login', methods=['GET', 'POST'])
def login():
    # Se o usuário já está logado, redireciona para dashboard
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    formulario = FormularioLogin()
    
    if formulario.validate_on_submit():
        username = formulario.username.data
        password = formulario.password.data
        
        # Procurar usuário no banco de dados
        usuario = User.query.filter_by(username=username).first()
        
        # Verificar se o usuário existe e se a senha está correta
        if usuario and check_password_hash(usuario.password, password):
            # Fazer login do usuário
            login_user(usuario)
            
            # Verificar se há uma página de redirecionamento salva
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Login falhou. Verifique seu usuário e senha.')
    
    return render_template('login.html', form=formulario)


@app.route('/logout')
def logout():
    logout_user()
    flash('Você foi desconectado com sucesso.')
    return redirect(url_for('home'))


@app.route('/dashboard')
@login_required
def dashboard():
    # Buscar todos os eventos
    todos_eventos = Evento.query.all()

    # Buscar apenas os eventos do usuário atual
    meus_eventos = Evento.query.filter_by(id_usuario=current_user.id).all()

    return render_template(
        'dashboard.html',
        todos_eventos=todos_eventos,
        meus_eventos=meus_eventos
    )


@app.route('/create_event', methods=['GET', 'POST'])
@login_required
def create_event():
    formulario = FormularioEvento()

    if formulario.validate_on_submit():
        nome = formulario.nome.data
        desc = formulario.descricao.data
        dat = formulario.data.data

        # Associar o evento ao usuário atual
        novoEvento = Evento(nome=nome, descricao=desc, dataEvento=dat, id_usuario=current_user.id)
        db.session.add(novoEvento)
        db.session.commit()
        
        flash('Evento criado com sucesso!')
        return redirect(url_for('dashboard'))

    return render_template('create_event.html', form=formulario)


@app.route('/edit_event/<int:event_id>', methods=['GET', 'POST'])
@login_required
def edit_event(event_id):
    # Buscar o evento pelo ID
    evento = Evento.query.get_or_404(event_id)
    
    # Verificar se o evento pertence ao usuário atual
    if evento.id_usuario != current_user.id:
        flash('Você não tem permissão para editar este evento.')
        return redirect(url_for('dashboard'))
    
    formulario = FormularioEvento()
    
    if request.method == 'GET':
        # Preencher o formulário com os dados do evento
        formulario.nome.data = evento.nome
        formulario.descricao.data = evento.descricao
        formulario.data.data = evento.dataEvento
    
    if formulario.validate_on_submit():
        # Atualizar os dados do evento
        evento.nome = formulario.nome.data
        evento.descricao = formulario.descricao.data
        evento.dataEvento = formulario.data.data
        
        db.session.commit()
        flash('Evento atualizado com sucesso!')
        return redirect(url_for('dashboard'))
    
    return render_template('edit_event.html', form=formulario, evento=evento)


@app.route('/delete_event/<int:event_id>', methods=['POST'])
@login_required
def delete_event(event_id):
    # Buscar o evento pelo ID
    evento = Evento.query.get_or_404(event_id)
    
    # Verificar se o evento pertence ao usuário atual
    if evento.id_usuario != current_user.id:
        flash('Você não tem permissão para excluir este evento.')
        return redirect(url_for('dashboard'))
    
    # Excluir o evento
    db.session.delete(evento)
    db.session.commit()
    
    flash('Evento excluído com sucesso!')
    return redirect(url_for('dashboard'))


if __name__ == '__main__':
    app.run(debug=True)
