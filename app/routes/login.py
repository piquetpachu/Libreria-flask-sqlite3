from flask import Blueprint,render_template,request,redirect,flash,jsonify,url_for,session
from models.controladordatabase import db,Usuario
from functools import wraps


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "nombre" not in session:
            flash("Por favor, inicia sesión para acceder a esta página.")
            return redirect(url_for('user.index_login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "nombre" not in session: 
            flash("Acceso denegado: Debes iniciar sesión.")
            return redirect(url_for('user.index_login'))  
        
        if session.get('rol') != 'admin':  
            flash("Acceso denegado: Se requiere rol de administrador.")
            return redirect(url_for('libros.bienvenida'))  
            
        return f(*args, **kwargs)
    return decorated_function


user = Blueprint('user',__name__)

@user.route("/index_login")
def index_login():
    if "nombre" in session:
        return redirect(url_for('libros.bienvenida'))
    return render_template("usuarios/login.html")



@user.route("/login", methods=["POST"])
def login():
    nombre = request.form['nombre']
    contrasena = request.form['contrasena']
    
    # Buscar al usuario en la base de datos por nombre
    user = Usuario.query.filter_by(nombre=nombre).first()
    
    # Verificar si el usuario existe y si la contraseña es correcta
    if user and user.check_password(contrasena):
        # Guardar los datos del usuario en la sesión
        session['nombre'] = nombre
        session['rol'] = user.rol
        session['usuario_id'] = user.id  # Asegúrate de guardar el id del usuario
    
        return redirect(url_for('libros.bienvenida'))
    else:
        return render_template("usuarios/login.html", error="Credenciales incorrectas")

    
@user.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        nombre = request.form['nombre']
        contrasena = request.form['contrasena']
        correo = request.form['correo']
        tel_cel = request.form['tel_cel']

        user = Usuario.query.filter_by(nombre=nombre).first()
        if user:
            return render_template("usuarios/register.html", error="Usuario ya registrado")
        else:
            nuevo_usuario = Usuario(nombre=nombre, correo=correo, tel_cel=tel_cel)
            nuevo_usuario.set_password(contrasena)
            db.session.add(nuevo_usuario)
            db.session.commit()
            session['nombre'] = nombre 
            return redirect(url_for('libros.bienvenida'))
    return render_template("usuarios/register.html")

@user.route("/logout")
def logout():
    session.pop('nombre', None)
    session.pop('rol', None)
    session.pop('usuario_id', None)
    return redirect(url_for('user.index_login'))
