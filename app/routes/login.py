from flask import Blueprint,render_template,request,redirect,flash,jsonify,url_for,session
from models.controladordatabase import db,Usuario

user = Blueprint('user',__name__)

@user.route("/index_login")
def index_login():
    if "nombre" in session:
        return redirect(url_for('libros.index'))
    return render_template("usuarios/login.html")



@user.route("/login", methods=["POST"])
def login():
    nombre = request.form['nombre']
    contrasena = request.form['contrasena']
    user = Usuario.query.filter_by(nombre=nombre).first()
    if user and user.check_password(contrasena):
        session['nombre'] = nombre
        return redirect(url_for('libros.index'))
    else:
        return render_template("usuarios/login.html")
    
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
            return redirect(url_for('index'))
    return render_template("usuarios/register.html")

@user.route("/logout")
def logout():
    session.pop('nombre',None)
    return redirect(url_for('user.index_login'))

    