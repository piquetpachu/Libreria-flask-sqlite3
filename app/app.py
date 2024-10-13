from flask import Flask
from routes.libros import libros
from routes.login import user
from routes.prestamo import prestamos
from routes.votaciones import votaciones
from flask_sqlalchemy import SQLAlchemy
from utils.db import db

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///libreria.db?timeout=10'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_timeout': 10
}
app.secret_key = 'LL4ves3cret4'
db
app.register_blueprint(libros)
app.register_blueprint(user)
app.register_blueprint(prestamos)
app.register_blueprint(votaciones)
