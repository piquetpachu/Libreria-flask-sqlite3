from datetime import date, datetime
from werkzeug.security import generate_password_hash, check_password_hash
from utils.db import db

# Tabla de Autores
class Autor(db.Model):
    __tablename__ = 'Autores'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    nacionalidad = db.Column(db.String(100), nullable=True)

    libros = db.relationship('Libros', backref='autor', lazy=True)

    def __init__(self, nombre, apellido, nacionalidad=None):
        self.nombre = nombre
        self.apellido = apellido
        self.nacionalidad = nacionalidad

# Tabla de Géneros
class Genero(db.Model):
    __tablename__ = 'Generos'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)

    libros = db.relationship('Libros', backref='genero', lazy=True)

    def __init__(self, nombre):
        self.nombre = nombre

# Tabla de Editorial
class Editorial(db.Model):
    __tablename__ = 'Editorial'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    pais = db.Column(db.String(100), nullable=True)  # País de la editorial

    libros = db.relationship('Libros', backref='editorial', lazy=True)

    def __init__(self, nombre, pais=None):
        self.nombre = nombre
        self.pais = pais

# Tabla de Libros
class Libros(db.Model):
    __tablename__ = 'Libros'

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    fecha_emision = db.Column(db.Text, nullable=False, default=date.today)
    stock = db.Column(db.Integer, nullable=False)
    precio = db.Column(db.Float, nullable=False)
    precio_alquiler = db.Column(db.Float, nullable=True)  # Precio de alquiler
    img = db.Column(db.String(200), nullable=True, default="sinimagen.jpg")

    # Relaciones foráneas
    id_autor = db.Column(db.Integer, db.ForeignKey('Autores.id'), nullable=False)
    id_genero = db.Column(db.Integer, db.ForeignKey('Generos.id'), nullable=False)
    id_editorial = db.Column(db.Integer, db.ForeignKey('Editorial.id'), nullable=True)

    # Otros campos adicionales
    isbn = db.Column(db.String(13), unique=True, nullable=True)  # ISBN
    idioma = db.Column(db.String(50), nullable=True)  # Idioma
    edicion = db.Column(db.String(50), nullable=True)  # Edición
    paginas = db.Column(db.Integer, nullable=True)  # Páginas
    fecha_publicacion = db.Column(db.Text, nullable=True,  default=date.today)  # Fecha de publicación
    formato = db.Column(db.Enum('Tapa dura', 'Tapa blanda', 'eBook', 'Audiolibro', 'Otro'), nullable=True)  # Formato
    calificacion_promedio = db.Column(db.Float, nullable=True, default=0.0)  # Calificación promedio

    prestamos = db.relationship('Prestamo', backref='libro', lazy=True)
    comentarios = db.relationship('Comentario', backref='libro', lazy=True)

    def __init__(self, titulo, id_autor, id_genero,id_editorial, descripcion, fecha_emision, stock, precio,precio_alquiler, img, isbn=None, idioma=None,
                 edicion=None, paginas=None, fecha_publicacion=None, formato=None, calificacion_promedio=0.0, num_resenas=0):
        self.titulo = titulo
        self.id_autor = id_autor
        self.id_genero = id_genero
        self.id_editorial = id_editorial
        self.descripcion = descripcion
        self.fecha_emision = fecha_emision
        self.stock = stock
        self.precio = precio
        self.precio_alquiler = precio_alquiler
        self.img = img
        self.isbn = isbn
        self.idioma = idioma
        self.edicion = edicion
        self.paginas = paginas
        self.fecha_publicacion = fecha_publicacion
        self.formato = formato
        self.calificacion_promedio = calificacion_promedio

# Tabla de Usuarios
class Usuario(db.Model):
    __tablename__ = 'Usuario'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    correo = db.Column(db.String(100), unique=True, nullable=True)
    contrasena = db.Column(db.String(100), nullable=False)
    tel_cel = db.Column(db.String(20), nullable=True, default='12345678')
    rol = db.Column(db.Enum('admin', 'comun'), nullable=True, default='comun')

    prestamos = db.relationship('Prestamo', backref='usuario', lazy=True)

    def set_password(self, contrasena):
        self.contrasena = generate_password_hash(contrasena)
    
    def check_password(self, contrasena):
        return check_password_hash(self.contrasena, contrasena)

# Tabla de Préstamos
class Prestamo(db.Model):
    __tablename__ = 'Prestamo'

    id = db.Column(db.Integer, primary_key=True)
    id_libro = db.Column(db.Integer, db.ForeignKey('Libros.id'), nullable=False)
    id_usuario = db.Column(db.Integer, db.ForeignKey('Usuario.id'), nullable=False)
    fecha_prestamo = db.Column(db.Text, nullable=False, default=date.today)
    fecha_devolucion = db.Column(db.Text, nullable=True)
    precio_final = db.Column(db.Float, nullable=False)

    def __init__(self, id_libro, id_usuario, precio_final, fecha_devolucion=None):
        self.id_libro = id_libro
        self.id_usuario = id_usuario
        self.precio_final = precio_final
        self.fecha_devolucion = fecha_devolucion

class Votacion(db.Model):
    __tablename__ = 'Votacion'
    
    id = db.Column(db.Integer, primary_key=True)
    id_libro = db.Column(db.Integer, db.ForeignKey('Libros.id'), nullable=False)
    id_usuario = db.Column(db.Integer, db.ForeignKey('Usuario.id'), nullable=False)
    calificacion = db.Column(db.Integer, nullable=False)  # La calificación (1-5 estrellas)

    # Unicidad: un usuario no puede votar más de una vez por libro
    __table_args__ = (db.UniqueConstraint('id_libro', 'id_usuario', name='unique_user_book_vote'),)
    
    def __init__(self, id_libro, id_usuario, calificacion):
        self.id_libro = id_libro
        self.id_usuario = id_usuario
        self.calificacion = calificacion

class Comentario(db.Model):
    __tablename__ = 'Comentarios'
    id = db.Column(db.Integer, primary_key=True)
    id_libro = db.Column(db.Integer, db.ForeignKey('Libros.id'), nullable=False)
    id_usuario = db.Column(db.Integer, db.ForeignKey('Usuario.id'), nullable=False)
    comentario = db.Column(db.Text, nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    usuario = db.relationship('Usuario', backref='comentarios', lazy=True)


    def __init__(self, id_libro, id_usuario, comentario, fecha=None):
        self.id_libro = id_libro
        self.id_usuario = id_usuario
        self.comentario = comentario
        self.fecha = fecha or datetime.utcnow()  # Si no se proporciona la fecha, usa la fecha actual

