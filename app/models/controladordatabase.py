from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash
from utils.db import db

class Libros(db.Model):
    __tablename__ = 'Libros'

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    autor = db.Column(db.String(100), nullable=False)
    genero = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    fecha_emision = db.Column(db.Text, nullable=False, default=date.today)
    stock = db.Column(db.Integer, nullable=False)
    precio = db.Column(db.Float, nullable=False)
    img = db.Column(db.String(200), nullable=True, default="sinimagen.jpg")

    prestamos = db.relationship('Prestamo', backref='libro', lazy=True)

    def __init__(self, titulo, autor, genero, descripcion, fecha_emision, stock, precio, img):
        self.titulo = titulo
        self.autor = autor
        self.genero = genero
        self.descripcion = descripcion
        self.fecha_emision = fecha_emision
        self.stock = stock
        self.precio = precio
        self.img = img

class Prestamo(db.Model):
    __tablename__ = 'Prestamo'

    id = db.Column(db.Integer, primary_key=True)
    id_libro = db.Column(db.Integer, db.ForeignKey('Libros.id'), nullable=False)
    id_usuario = db.Column(db.Integer, db.ForeignKey('Usuario.id'), nullable=False)
    fecha_prestamo = db.Column(db.Date, nullable=False, default=date.today)
    fecha_devolucion = db.Column(db.Date, nullable=True)
    precio_final = db.Column(db.Float, nullable=False)

class Usuario(db.Model):
    __tablename__ = 'Usuario'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    correo = db.Column(db.String(100), unique=True, nullable=True)
    contrasena = db.Column(db.String(100), nullable=False)  # Asegúrate de que es 'contrasena'
    tel_cel = db.Column(db.String(20), nullable=True, default='12345678')
    rol = db.Column(db.Enum('admin', 'comun'), nullable=True, default='comun')

    prestamos = db.relationship('Prestamo', backref='usuario', lazy=True)

    def set_password(self, contrasena):
        self.contrasena = generate_password_hash(contrasena)
    
    def check_password(self, contrasena):
        return check_password_hash(self.contrasena, contrasena)