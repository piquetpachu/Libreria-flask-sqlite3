from flask import Blueprint,render_template,request,redirect,flash,jsonify,url_for
from models.controladordatabase import db,Libros


libros = Blueprint('libros',__name__)

@libros.route('/')
def index():
    return render_template('libros/agregarlibro.html')

@libros.route('/agregarlibro', methods=['POST'])
def agregarlibro():
    titulo = request.form['nombre_libro']
    autor = request.form['autor']
    descripcion = request.form['descripcion']
    fecha_emision = request.form['fecha_creacion']
    stock = int(request.form['stock'])
    precio = float(request.form['precio'])
    img = request.form['imagen']
    nuevolibro = Libros(titulo,autor,descripcion,fecha_emision,stock,precio,img)
    try:
        db.session.add(nuevolibro)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400
    
    print(nuevolibro)
    return 'Libro añadido'
@libros.route('/eliminarlibro/<int:id>')
def eliminarlibro(id):
    libro = Libros.query.get(id)
    if libro:
        db.session.delete(libro)
        db.session.commit()
        flash(f'Libro {libro.titulo} eliminado con éxito', 'success')
    else:
        flash('Libro no encontrado', 'error')
    return redirect(url_for('libros.verlibro'))

@libros.route('/editarlibro/<int:id>', methods=['POST','GET'])
def editarlibro(id):
    libros = Libros.query.get(id)

    if request.method == "POST":

        libros.titulo = request.form['nombre_libro']
        libros.autor = request.form['autor']
        libros.descripcion = request.form['descripcion']
        libros.fecha_emision = request.form['fecha_creacion']
        libros.stock = request.form['stock']
        libros.precio = request.form['precio']
        libros.img = request.form['imagen']

        db.session.add(libros)
        db.session.commit()
        return redirect(url_for('libros.verlibro'))

    return render_template('libros/editarlibro.html',libros=libros)

@libros.route('/verlibro')
def verlibro():
    libros = Libros.query.all()  
    return render_template('libros/verlibros.html', libros=libros)

