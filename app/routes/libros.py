from flask import Blueprint, render_template, request, redirect, flash, jsonify, url_for
from werkzeug.utils import secure_filename
from models.controladordatabase import db, Libros, Prestamo,Autor,Genero,Editorial,Votacion
from routes.login import login_required, admin_required
import os
from sqlalchemy import or_
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
    autores = Autor.query.all()
    generos = Genero.query.all()
    editoriales = Editorial.query.all()
    return render_template('libros/agregarlibro.html',autores=autores, generos=generos, editoriales=editoriales)



@libros.route('/agregarlibro', methods=['POST'])
@admin_required
def agregarlibro():
    titulo = request.form['titulo']
    id_autor = request.form['autor']
    id_genero = request.form['genero']
    id_editorial = request.form['editorial']
    descripcion = request.form['descripcion']
    fecha_emision = request.form['fecha_publicacion']
    stock = request.form['stock']
    precio = float(request.form['precio'])
    precio_alquiler = request.form.get('precio_alquiler', None)  # Puede ser opcional
    isbn = request.form.get('isbn') or None  # Si el campo está vacío, almacena None    
    idioma = request.form['idioma']
    edicion = request.form['edicion']
    paginas = int(request.form['paginas'])
    formato = request.form['formato']
    
    # Manejo de la imagen
    imagen = request.files['imagen']
    if imagen:
        basepath = os.path.dirname(__file__)  # Ruta base del archivo actual
        filename = secure_filename(imagen.filename)  # Obtener el nombre original
        extension = os.path.splitext(filename)[1]  # Obtener la extensión del archivo
        nuevoNombreFile = stringAleatorio() + extension  # Generar un nombre único para la imagen

        # Guardar la imagen en la carpeta static/img
        upload_path = os.path.join(basepath, '../static/img', nuevoNombreFile) 
        imagen.save(upload_path)  

        # Crear una nueva instancia del libro
        nuevolibro = Libros(
            titulo=titulo,
            id_autor=id_autor,  # Relación con la tabla Autores
            id_genero=id_genero,  # Relación con la tabla Géneros
            id_editorial=id_editorial,  # Relación con la tabla Editoriales
            descripcion=descripcion,
            fecha_emision=fecha_emision,
            stock=stock,
            precio=precio,
            precio_alquiler=precio_alquiler if precio_alquiler else None,  # Campo opcional
            isbn=isbn,
            idioma=idioma,
            edicion=edicion,
            paginas=paginas,
            formato=formato,
            img=nuevoNombreFile  # Almacenar el nombre de la imagen
        )

        try:
            db.session.add(nuevolibro)
            db.session.commit()
            flash('Libro agregado exitosamente', 'success')
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 400

    return redirect(url_for('libros.bienvenida'))

@libros.route('/agregarautor', methods=['GET', 'POST'])
@admin_required
def agregar_autor():
    if request.method == 'POST':
        nombre_autor = request.form['nombre_autor']
        apellido_autor = request.form['apellido_autor']
        nuevo_autor = Autor(nombre=nombre_autor, apellido=apellido_autor)
        try:
            db.session.add(nuevo_autor)
            db.session.commit()
            flash('Autor agregado exitosamente', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error al agregar autor: {str(e)}', 'danger')
        return redirect(url_for('libros.index'))
    
    return render_template('libros/agregar_autor.html')

@libros.route('/agregargenero', methods=['GET', 'POST'])
@admin_required
def agregar_genero():
    if request.method == 'POST':
        nombre_genero = request.form['nombre_genero']
        nuevo_genero = Genero(nombre=nombre_genero)
        try:
            db.session.add(nuevo_genero)
            db.session.commit()
            flash('Género agregado exitosamente', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error al agregar género: {str(e)}', 'danger')
        return redirect(url_for('libros.index'))
    
    return render_template('libros/agregar_genero.html')

@libros.route('/agregareditorial', methods=['GET', 'POST'])
@admin_required
def agregar_editorial():
    if request.method == 'POST':
        nombre_editorial = request.form['nombre_editorial']
        nueva_editorial = Editorial(nombre=nombre_editorial)
        try:
            db.session.add(nueva_editorial)
            db.session.commit()
            flash('Editorial agregada exitosamente', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error al agregar editorial: {str(e)}', 'danger')
        return redirect(url_for('libros.index'))
    
    return render_template('libros/agregar_editorial.html')




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
    libro = Libros.query.get_or_404(id)
    autores = Autor.query.all()
    generos = Genero.query.all()
    editoriales = Editorial.query.all()

    if request.method == "POST":
        libro.titulo = request.form['titulo']
        libro.autor_id = int(request.form['autor'])  # Actualizar la relación con el autor
        libro.genero_id = int(request.form['genero'])  # Actualizar la relación con el género
        libro.editorial_id = int(request.form['editorial']) if request.form['editorial'] else None
        libro.descripcion = request.form['descripcion']
        libro.fecha_emision = request.form['fecha_publicacion']
        libro.stock = int(request.form['stock'])
        libro.precio = float(request.form['precio'])
        libro.precio_alquiler = float(request.form['precio_alquiler']) if request.form['precio_alquiler'] else None

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
            flash(f'Error al actualizar el libro: {str(e)}', 'danger')

        return redirect(url_for('libros.verlibro'))

    return render_template('libros/editarlibro.html', libro=libro, autores=autores, generos=generos, editoriales=editoriales)


@libros.route('/verlibro')
@admin_required
def verlibro():
    page = request.args.get('page', 1, type=int)
    per_page = 10

    titulo = request.args.get('titulo', '', type=str)
    autor = request.args.get('autor', '', type=str)
    editorial = request.args.get('editorial', '', type=str)
    genero = request.args.get('genero', '', type=str)

   # Consulta básica de libros
    query = Libros.query

    # Aplicar filtros de búsqueda
    if titulo:
        query = query.filter(Libros.titulo.ilike(f'%{titulo}%'))
    if autor:
        query = query.join(Autor).filter(or_(Autor.nombre.ilike(f'%{autor}%'), Autor.apellido.ilike(f'%{autor}%')))
    if editorial:
        query = query.join(Editorial).filter(Editorial.nombre.ilike(f'%{editorial}%'))
    if genero:
        query = query.join(Genero).filter(Genero.nombre.ilike(f'%{genero}%'))

    pagination = query.paginate(page=page, per_page=per_page)


    # Obtener todos los autores, editoriales y géneros para los menús desplegables
    autores = Autor.query.all()
    editoriales = Editorial.query.all()
    generos = Genero.query.all()

    return render_template('libros/verlibros.html', pagination=pagination, autores=autores, editoriales=editoriales, generos=generos)


@libros.route('/libros', methods=['GET'])
def libross():
    # Obtener los parámetros de filtro desde la URL
    titulo = request.args.get('titulo', '', type=str)
    autor = request.args.get('autor', '', type=str)
    editorial = request.args.get('editorial', '', type=str)
    genero = request.args.get('genero', '', type=str)

    # Paginación
    page = request.args.get('page', 1, type=int)
    per_page = 10  # Número de libros por página

    # Consulta básica de libros
    query = Libros.query

    # Aplicar filtros de búsqueda
    if titulo:
        query = query.filter(Libros.titulo.ilike(f'%{titulo}%'))
    if autor:
        query = query.join(Autor).filter(or_(Autor.nombre.ilike(f'%{autor}%'), Autor.apellido.ilike(f'%{autor}%')))
    if editorial:
        query = query.join(Editorial).filter(Editorial.nombre.ilike(f'%{editorial}%'))
    if genero:
        query = query.join(Genero).filter(Genero.nombre.ilike(f'%{genero}%'))

    # Aplicar la paginación
    pagination = query.paginate(page=page, per_page=per_page)

    # Obtener todos los autores, editoriales y géneros para los menús desplegables
    autores = Autor.query.all()
    editoriales = Editorial.query.all()
    generos = Genero.query.all()

    return render_template('libros/libros.html', pagination=pagination, autores=autores, editoriales=editoriales, generos=generos)

@libros.route('/libros/<int:libro_id>')
def detalle(libro_id):
    libro = Libros.query.get_or_404(libro_id)
    promedio_calificacion = db.session.query(db.func.avg(Votacion.calificacion)).filter(Votacion.id_libro == libro_id).scalar()
    comentarios = libro.comentarios  # Recupera los comentarios asociados a este libro

    return render_template('libros/detalle.html', libro=libro,promedio_calificacion=promedio_calificacion,comentarios=comentarios)


@libros.route("/terminosycondiciones")
def condiciones():
    return render_template("terminos_condiciones.html")



