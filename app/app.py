from flask import Flask
from routes.libros import libros
from flask_sqlalchemy import SQLAlchemy
from utils.db import db
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///libreria.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db
app.register_blueprint(libros)