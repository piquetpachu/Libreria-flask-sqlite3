from flask import Blueprint, render_template, request, redirect, flash, jsonify, url_for
from werkzeug.utils import secure_filename
from models.controladordatabase import db, Libros, Prestamo
from routes.login import login_required, admin_required
import os
from random import sample


libros = Blueprint('libros',__name__)

def stringAleatorio():
    string_aleatorio = "0123456789abcdefghijklmnopqrstuvwxyz_"
    longitud = 20
    secuencia = string_aleatorio.upper()
    resultado_aleatorio = sample(secuencia, longitud)
    return "".join(resultado_aleatorio)

@libros.route('/')
def bienvenida():
    libros_destacados = Libros.query.filter(Libros.precio < 15.0 ).all()
    return render_template('bienvenida.html', libros_destacados=libros_destacados)

@libros.route('/formulariolibros')
@admin_required
def index():
    return render_template('libros/agregarlibro.html')

@libros.route('/agregarlibro', methods=['POST'])
@admin_required
def agregarlibro():
    titulo = request.form['nombre_libro']
    autor = request.form['autor']
    genero = request.form['genero']
    descripcion = request.form['descripcion']
    fecha_emision = request.form['fecha_creacion']
    stock = int(request.form['stock'])
    precio = float(request.form['precio'])
    
    # Manejo de la imagen
    imagen = request.files['imagen']
    if imagen:
        # Generar un nombre seguro y único para el archivo
        basepath = os.path.dirname(__file__)  # Ruta base del archivo actual
        filename = secure_filename(imagen.filename)  # Obtener el nombre original
        extension = os.path.splitext(filename)[1]  # Obtener la extensión
        nuevoNombreFile = stringAleatorio() + extension  # Generar nuevo nombre único

        upload_path = os.path.join(basepath, '../static/img', nuevoNombreFile) 
        imagen.save(upload_path)  

        nuevolibro = Libros(
            titulo=titulo,
            autor=autor,
            genero=genero,
            descripcion=descripcion,
            fecha_emision=fecha_emision,
            stock=stock,
            precio=precio,
            img=nuevoNombreFile  
        )

        try:
            db.session.add(nuevolibro)
            db.session.commit()
            flash('Libro agregado exitosamente', 'success')
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 400
    
    return redirect(url_for('libros.bienvenida'))

@libros.route('/eliminarlibro/<int:id>')
@admin_required
def eliminarlibro(id):
    libro = Libros.query.get(id)

    if libro:
        prestamo_activo = Prestamo.query.filter_by(id_libro=id).first()

        if prestamo_activo:
            flash(f'El libro "{libro.titulo}" no puede ser eliminado porque está prestado.', 'error')
        else:
            db.session.delete(libro)
            db.session.commit()
            flash(f'Libro "{libro.titulo}" eliminado con éxito', 'success')
    else:
        flash('Libro no encontrado', 'error')

    return redirect(url_for('libros.verlibro'))

@libros.route('/editarlibro/<int:id>', methods=['POST', 'GET'])
@admin_required
def editarlibro(id):
    libro = Libros.query.get(id)

    if request.method == "POST":
        libro.titulo = request.form['nombre_libro']
        libro.autor = request.form['autor']
        libro.genero = request.form['genero']
        libro.descripcion = request.form['descripcion']
        libro.fecha_emision = request.form['fecha_creacion']
        libro.stock = request.form['stock']
        libro.precio = request.form['precio']

        nueva_imagen = request.files.get('imagen')
        if nueva_imagen:
            basepath = os.path.dirname(__file__)
            filename = secure_filename(nueva_imagen.filename)
            extension = os.path.splitext(filename)[1]
            nuevoNombreFile = stringAleatorio() + extension

            upload_path = os.path.join(basepath, '../static/img', nuevoNombreFile)
            nueva_imagen.save(upload_path)

            # Opción para eliminar la imagen anterior (si existe)
            if libro.img:
                imagen_antigua = os.path.join(basepath, '../static/img', libro.img)
                if os.path.exists(imagen_antigua):
                    os.remove(imagen_antigua)

            # Actualizar el nombre de la imagen en la base de datos
            libro.img = nuevoNombreFile

        try:
            db.session.commit()
            flash('Libro actualizado exitosamente', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar el libro: {str(e)}', 'error')

        return redirect(url_for('libros.verlibro'))

    return render_template('libros/editarlibro.html', libro=libro)

@libros.route('/verlibro')
@admin_required
def verlibro():
    page = request.args.get('page', 1, type=int)
    per_page = 10

    titulo = request.args.get('titulo', '', type=str)
    autor = request.args.get('autor', '', type=str)
    genero = request.args.get('genero', '', type=str)

    query = Libros.query

    if titulo:
        query = query.filter(Libros.titulo.ilike(f"%{titulo}%"))
    if autor:
        query = query.filter(Libros.autor.ilike(f"%{autor}%"))
    if genero:
        query = query.filter(Libros.genero.ilike(f"%{genero}%"))


    pagination = query.paginate(page=page, per_page=per_page)

    return render_template('libros/verlibros.html', pagination=pagination, query=query)


@libros.route('/libros')
def libross():
    page = request.args.get('page', 1, type=int)
    per_page = 12

    titulo = request.args.get('titulo', '', type=str)
    autor = request.args.get('autor', '', type=str)
    genero = request.args.get('genero', '', type=str)
    anio = request.args.get('anio', type=int)

    query = Libros.query

    if titulo:
        query = query.filter(Libros.titulo.ilike(f"%{titulo}%"))
    if autor:
        query = query.filter(Libros.autor.ilike(f"%{autor}%"))
    if genero:
        query = query.filter(Libros.genero.ilike(f"%{genero}%"))
    if anio:
        query = query.filter(db.extract('year', Libros.fecha_emision) == anio)
    pagination = query.paginate(page=page, per_page=per_page)
    return render_template('libros/libros.html', pagination=pagination, query=query)

@libros.route('/libros/<int:libro_id>')
def detalle(libro_id):
    libro = Libros.query.get_or_404(libro_id)
    return render_template('libros/detalle.html', libro=libro)

@libros.route("/terminosycondiciones")
def condiciones():
    return render_template("terminos_condiciones.html")



