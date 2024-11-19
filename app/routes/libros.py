from flask import Blueprint, render_template, request, redirect, flash, jsonify, url_for,session
from werkzeug.utils import secure_filename
from models.controladordatabase import db, Libros, Prestamo,Autor,Genero,Editorial,Votacion,Usuario
from routes.login import login_required, admin_required
import os
import requests
from io import BytesIO
from PIL import Image
from sqlalchemy import or_, func, desc
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
    libros_mas_valorados = db.session.query(
        Libros.id,
        Libros.titulo,
        Libros.descripcion,
        Libros.img,
        Libros.precio,
        Libros.precio_alquiler,
        func.avg(Votacion.calificacion).label('promedio_estrellas')
    ).join(Votacion, Libros.id == Votacion.id_libro, isouter=True) \
    .group_by(Libros.id) \
    .order_by(desc('promedio_estrellas')) \
    .limit(6) \
    .all()

    return render_template('bienvenida.html', libros_mas_valorados=libros_mas_valorados)

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
    precio_alquiler = request.form.get('precio_alquiler', None)  
    isbn = request.form['isbn'] if request.form['isbn'] else None
    idioma = request.form['idioma']
    edicion = request.form['edicion']
    paginas = int(request.form['paginas'])
    formato = request.form['formato']

    imagen = request.files.get('imagen')
    imagen_url = request.form.get('imagen_url')
    img_name = None

    if imagen:  # Si se ha cargado una imagen local
        basepath = os.path.dirname(__file__)  # Ruta base del archivo actual
        filename = secure_filename(imagen.filename)  # Obtener el nombre original
        extension = os.path.splitext(filename)[1]  # Obtener la extensión del archivo
        nuevoNombreFile = stringAleatorio() + extension  # Generar un nombre único para la imagen

        upload_path = os.path.join(basepath, '../static/img', nuevoNombreFile) 
        imagen.save(upload_path)  
        img_name = nuevoNombreFile  

    elif imagen_url:  
        try:
            response = requests.get(imagen_url)
            if response.status_code == 200:
                basepath = os.path.dirname(__file__)
                extension = os.path.splitext(imagen_url)[1]  
                nuevoNombreFile = stringAleatorio() + extension  
                
                
                upload_path = os.path.join(basepath, '../static/img', nuevoNombreFile)
                image = Image.open(BytesIO(response.content))  
                image.save(upload_path)
                img_name = nuevoNombreFile  
            else:
                flash('No se pudo descargar la imagen desde la URL', 'danger')
                return redirect(url_for('libros.bienvenida'))
        except Exception as e:
            flash(f'Error al descargar la imagen: {str(e)}', 'danger')
            return redirect(url_for('libros.bienvenida'))

    nuevolibro = Libros(
        titulo=titulo,
        id_autor=id_autor, 
        id_genero=id_genero, 
        id_editorial=id_editorial,  
        descripcion=descripcion,
        fecha_emision=fecha_emision,
        stock=stock,
        precio=precio,
        precio_alquiler=precio_alquiler if precio_alquiler else None,  
        isbn=isbn if isbn else None,
        idioma=idioma,
        edicion=edicion,
        paginas=paginas,
        formato=formato,
        img=img_name if img_name else "sinimagen.jpg"  #
    )

    try:
        db.session.add(nuevolibro)
        db.session.commit()
        flash('Libro agregado exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al agregar el libro: {str(e)}', 'danger')

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
        return redirect(url_for('libros.agregar_autor'))

    autores = Autor.query.all()
    return render_template('libros/agregar_autor.html', autores=autores)


@libros.route('/editar_autor/<int:id>', methods=['POST'])
@admin_required
def editar_autor(id):
    autor = Autor.query.get_or_404(id)
    nuevo_nombre = request.form['nombre_autor']
    nuevo_apellido = request.form['apellido_autor']

    if autor.nombre != nuevo_nombre or autor.apellido != nuevo_apellido:
        autor.nombre = nuevo_nombre
        autor.apellido = nuevo_apellido
        try:
            db.session.commit()
            flash('Autor editado exitosamente', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error al editar autor: {str(e)}', 'danger')

    return redirect(url_for('libros.agregar_autor'))


@libros.route('/eliminar_autor/<int:id>', methods=['GET'])
@admin_required
def eliminar_autor(id):
    autor = Autor.query.get_or_404(id)

    libro_vinculado = Libros.query.filter_by(id_autor=id).first()

    if libro_vinculado:
        flash(f'El autor "{autor.nombre} {autor.apellido}" no puede ser eliminado porque tiene libros asociados.', 'danger')
    else:
        try:
            db.session.delete(autor)
            db.session.commit()
            flash('Autor eliminado exitosamente', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error al eliminar autor: {str(e)}', 'danger')

    return redirect(url_for('libros.agregar_autor'))


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
        return redirect(url_for('libros.agregar_genero'))

    generos = Genero.query.all()
    return render_template('libros/agregar_genero.html', generos=generos)


@libros.route('/editar_genero/<int:id>', methods=['POST'])
@admin_required
def editar_genero(id):
    genero = Genero.query.get_or_404(id)
    nuevo_nombre = request.form['nombre_genero']
    
    if genero.nombre != nuevo_nombre:
        genero.nombre = nuevo_nombre
        try:
            db.session.commit()
            flash('Género editado exitosamente', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error al editar género: {str(e)}', 'danger')

    return redirect(url_for('libros.agregar_genero'))


@libros.route('/eliminar_genero/<int:id>', methods=['GET'])
@admin_required
def eliminar_genero(id):
    genero = Genero.query.get_or_404(id)

    libro_vinculado = Libros.query.filter_by(id_genero=id).first()

    if libro_vinculado:
        flash(f'El género "{genero.nombre}" no puede ser eliminado porque tiene libros asociados.', 'danger')
    else:
        try:
            db.session.delete(genero)
            db.session.commit()
            flash('Género eliminado exitosamente', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error al eliminar género: {str(e)}', 'danger')

    return redirect(url_for('libros.agregar_genero'))


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
        return redirect(url_for('libros.agregar_editorial'))

    editoriales = Editorial.query.all()
    return render_template('libros/agregar_editorial.html', editoriales=editoriales)


@libros.route('/editar_editorial/<int:id>', methods=['POST'])
@admin_required
def editar_editorial(id):
    editorial = Editorial.query.get_or_404(id)
    nuevo_nombre = request.form['nombre_editorial']

    if editorial.nombre != nuevo_nombre:
        editorial.nombre = nuevo_nombre
        try:
            db.session.commit()
            flash('Editorial editada exitosamente', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error al editar editorial: {str(e)}', 'danger')

    return redirect(url_for('libros.agregar_editorial'))


@libros.route('/eliminar_editorial/<int:id>', methods=['GET'])
@admin_required
def eliminar_editorial(id):
    editorial = Editorial.query.get_or_404(id)

    libro_vinculado = Libros.query.filter_by(id_editorial=id).first()

    if libro_vinculado:
        flash(f'La editorial "{editorial.nombre}" no puede ser eliminada porque tiene libros asociados.', 'danger')
    else:
        try:
            db.session.delete(editorial)
            db.session.commit()
            flash('Editorial eliminada exitosamente', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error al eliminar editorial: {str(e)}', 'danger')

    return redirect(url_for('libros.agregar_editorial'))



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
        libro.id_autor = int(request.form['autor'])
        libro.id_genero = int(request.form['genero'])
        libro.id_editorial = int(request.form['editorial']) if request.form['editorial'] else None
        libro.descripcion = request.form['descripcion']
        libro.fecha_emision = request.form['fecha_publicacion']
        libro.stock = int(request.form['stock'])
        libro.precio = float(request.form['precio'])
        libro.precio_alquiler = float(request.form['precio_alquiler']) if request.form['precio_alquiler'] else None

        nuevo_isbn = request.form['isbn'] if request.form['isbn'] else None

        if nuevo_isbn != libro.isbn:
            isbn_existente = Libros.query.filter(Libros.isbn == nuevo_isbn, Libros.id != id).first()
            if isbn_existente:
                flash('Error: El ISBN ingresado ya está en uso por otro libro.', 'danger')
                return redirect(url_for('libros.editarlibro', id=id))
            else:
                libro.isbn = nuevo_isbn

        libro.idioma = request.form.get('idioma', '')
        libro.edicion = request.form['edicion']
        libro.paginas = request.form['paginas']
        libro.formato = request.form['formato']

        imagen_url = request.form.get('imagen_url')
        nueva_imagen = request.files.get('imagen')
        basepath = os.path.dirname(__file__)

        if nueva_imagen:
            filename = secure_filename(nueva_imagen.filename)
            extension = os.path.splitext(filename)[1]
            nuevoNombreFile = stringAleatorio() + extension

            upload_path = os.path.join(basepath, '../static/img', nuevoNombreFile)
            nueva_imagen.save(upload_path)

            # Si el libro ya tiene una imagen, eliminarla
            if libro.img and libro.img != "sinimagen.jpg":
                imagen_antigua = os.path.join(basepath, '../static/img', libro.img)
                if os.path.exists(imagen_antigua):
                    os.remove(imagen_antigua)

            libro.img = nuevoNombreFile

        elif imagen_url:
            try:
                response = requests.get(imagen_url)
                response.raise_for_status()
                img_bytes = BytesIO(response.content)
                img = Image.open(img_bytes)

                extension = os.path.splitext(imagen_url)[1]
                nuevoNombreFile = stringAleatorio() + extension
                upload_path = os.path.join(basepath, '../static/img', nuevoNombreFile)
                img.save(upload_path)

                # Si el libro ya tiene una imagen, eliminarla
                if libro.img and libro.img != "sinimagen.jpg":
                    imagen_antigua = os.path.join(basepath, '../static/img', libro.img)
                    if os.path.exists(imagen_antigua):
                        os.remove(imagen_antigua)

                libro.img = nuevoNombreFile

            except Exception as e:
                flash(f"Error al descargar la imagen: {str(e)}", "danger")
                return redirect(url_for('libros.bienvenida'))

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

    query = Libros.query

    if titulo:
        query = query.filter(Libros.titulo.ilike(f'%{titulo}%'))
    if autor:
        query = query.join(Autor).filter(or_(Autor.nombre.ilike(f'%{autor}%'), Autor.apellido.ilike(f'%{autor}%')))
    if editorial:
        query = query.join(Editorial).filter(Editorial.nombre.ilike(f'%{editorial}%'))
    if genero:
        query = query.join(Genero).filter(Genero.nombre.ilike(f'%{genero}%'))

    pagination = query.paginate(page=page, per_page=per_page)


    autores = db.session.query(Autor).join(Libros).filter(Libros.id_autor == Autor.id).distinct().all()

    
    generos = db.session.query(Genero).join(Libros).filter(Libros.id_genero == Genero.id).distinct().all()

    
    editoriales = db.session.query(Editorial).join(Libros).filter(Libros.id_editorial == Editorial.id).distinct().all()

    return render_template('libros/verlibros.html', pagination=pagination, autores=autores, editoriales=editoriales, generos=generos)


@libros.route('/libros', methods=['GET'])
def libross():
    titulo = request.args.get('titulo', '', type=str)
    autor = request.args.get('autor', '', type=str)
    editorial = request.args.get('editorial', '', type=str)
    genero = request.args.get('genero', '', type=str)

    page = request.args.get('page', 1, type=int)
    per_page = 10  

    query = Libros.query

    if titulo:
        query = query.filter(Libros.titulo.ilike(f'%{titulo}%'))
    if autor:
        query = query.join(Autor).filter(or_(Autor.nombre.ilike(f'%{autor}%'), Autor.apellido.ilike(f'%{autor}%')))
    if editorial:
        query = query.join(Editorial).filter(Editorial.nombre.ilike(f'%{editorial}%'))
    if genero:
        query = query.join(Genero).filter(Genero.nombre.ilike(f'%{genero}%'))

    pagination = query.paginate(page=page, per_page=per_page)

       
    autores = db.session.query(Autor).join(Libros).filter(Libros.id_autor == Autor.id).distinct().all()

    
    generos = db.session.query(Genero).join(Libros).filter(Libros.id_genero == Genero.id).distinct().all()

    
    editoriales = db.session.query(Editorial).join(Libros).filter(Libros.id_editorial == Editorial.id).distinct().all()

    return render_template('libros/libros.html', pagination=pagination, autores=autores, editoriales=editoriales, generos=generos)

@libros.route('/libros/<int:libro_id>')
def detalle(libro_id):
    libro = Libros.query.get_or_404(libro_id)
    
    promedio_calificacion = db.session.query(db.func.avg(Votacion.calificacion)).filter(Votacion.id_libro == libro_id).scalar()
    
    if promedio_calificacion is None:
        promedio_calificacion = 0  
    
    if "nombre" not in session:
        return render_template('libros/detalle.html', libro=libro, promedio_calificacion=promedio_calificacion)
    
    usuario_id = Usuario.query.filter_by(nombre=session['nombre']).first().id
    comentarios = libro.comentarios  
    votacion = Votacion.query.filter_by(id_libro=libro_id, id_usuario=usuario_id).first()

    return render_template('libros/detalle.html', libro=libro, promedio_calificacion=promedio_calificacion, comentarios=comentarios, votacion=votacion)


@libros.route("/terminosycondiciones")
def condiciones():
    return render_template("terminos_condiciones.html")



