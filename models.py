from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from config import db, login_manager

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)

    events = db.relationship('Evento', backref='owner', lazy=True)

class Evento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String, nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    dataEvento = db.Column(db.Date, nullable=False)
    id_usuario = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

