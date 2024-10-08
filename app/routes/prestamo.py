from flask import Blueprint, render_template, request, redirect, flash, url_for,session
from models.controladordatabase import db, Prestamo, Libros, Usuario
from datetime import date
from routes.login import login_required,admin_required
from datetime import date, timedelta

prestamos = Blueprint('prestamos', __name__)

@prestamos.route('/todos-los-prestamos')
@admin_required
def ver_todos_prestamos():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    nombre_usuario = request.args.get('usuario')
    titulo_libro = request.args.get('titulo_libro', '', type=str)

    query = db.session.query(Prestamo, Libros, Usuario).join(Libros, Prestamo.id_libro == Libros.id).join(Usuario, Prestamo.id_usuario == Usuario.id)

    if nombre_usuario:
        query = query.filter(Usuario.nombre.ilike(f"%{nombre_usuario}%"))
    if titulo_libro:
        query = query.filter(Libros.titulo.ilike(f"%{titulo_libro}%"))

    prestamos = query.all()
    pagination = query.paginate(page=page, per_page=per_page)

    return render_template('prestamos/todos.html', prestamos=prestamos,pagination=pagination)

from datetime import datetime

@prestamos.route('/editar-prestamo/<int:id>', methods=['GET', 'POST'])
@admin_required
def editar_prestamo(id):
    prestamo = Prestamo.query.get_or_404(id)
    
    if request.method == 'POST':
        fecha_devolucion = request.form.get('fecha_devolucion')
        if fecha_devolucion:
            try:
                # Convertir la fecha a un objeto date de Python
                prestamo.fecha_devolucion = datetime.strptime(fecha_devolucion, '%Y-%m-%d').date()
                db.session.commit()
                flash('Préstamo actualizado con éxito.', 'success')
            except ValueError as ve:
                flash(f'Formato de fecha inválido: {str(ve)}', 'error')
            except Exception as e:
                db.session.rollback()
                flash(f'Error al actualizar el préstamo: {str(e)}', 'error')
        
        return redirect(url_for('prestamos.ver_todos_prestamos'))
    
    return render_template('prestamos/editar.html', prestamo=prestamo)

@prestamos.route('/eliminar-prestamo/<int:id>', methods=['POST','GET'])
@login_required
def eliminar_prestamo(id):
    prestamo = Prestamo.query.get_or_404(id)
    libro = Libros.query.get_or_404(prestamo.id_libro)  
    
    try:
        libro.stock += 1  

        db.session.delete(prestamo)

        db.session.commit()

        flash('Préstamo eliminado y stock del libro actualizado con éxito.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar el préstamo: {str(e)}', 'error')
    
    return redirect(request.referrer)


@prestamos.route('/mis-prestamos')
@login_required
def listar_prestamos():
    
    usuario_id = Usuario.query.filter_by(nombre=session['nombre']).first().id
    
    # Obtener todos los préstamos del usuario
    prestamos = db.session.query(Prestamo, Libros).join(Libros, Prestamo.id_libro == Libros.id).filter(Prestamo.id_usuario == usuario_id).all()
    
    total_precios = round(sum([prestamo.precio_final for prestamo, _ in prestamos]))

    return render_template('prestamos/listar.html', prestamos=prestamos, total_precios=total_precios)


@prestamos.route('/solicitar-prestamo/<int:libro_id>', methods=['POST'])
@login_required
def solicitar_prestamo(libro_id):
    libro = Libros.query.get_or_404(libro_id)

    if libro.stock <= 0:
        flash('No hay stock disponible para este libro.', 'error')
        return redirect(url_for('libros.detalle', libro_id=libro.id))

    usuario_id = Usuario.query.filter_by(nombre=session['nombre']).first().id

    duracion_dias = int(request.form['duracion'])
    fecha_prestamo = date.today()
    fecha_devolucion = fecha_prestamo + timedelta(days=duracion_dias)

    if duracion_dias == 30:
        precio_final = libro.precio * 2
    else:
        precio_final = libro.precio
    
    nuevo_prestamo = Prestamo(
        id_libro=libro.id,
        id_usuario=usuario_id,
        fecha_prestamo=fecha_prestamo,
        fecha_devolucion=fecha_devolucion,
        precio_final=precio_final  
    )
    
    libro.stock -= 1  
    
    try:
        db.session.add(nuevo_prestamo)
        db.session.commit()
        flash(f'Préstamo del libro "{libro.titulo}" realizado con éxito. Precio final: ${precio_final}', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al realizar el préstamo: {str(e)}', 'error')
    
    return redirect(url_for('prestamos.listar_prestamos'))
