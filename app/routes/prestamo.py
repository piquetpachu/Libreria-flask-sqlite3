from flask import Blueprint, render_template, request, redirect, flash, url_for,session
from models.controladordatabase import db, Prestamo, Libros, Usuario
from datetime import date
from routes.login import login_required,admin_required
from datetime import date, timedelta

prestamos = Blueprint('prestamos', __name__)

@prestamos.route('/todos-los-prestamos')
@admin_required
def ver_todos_prestamos():
    # Obtener todos los préstamos junto con los detalles del libro y del usuario
    prestamos = db.session.query(Prestamo, Libros, Usuario).join(Libros, Prestamo.id_libro == Libros.id).join(Usuario, Prestamo.id_usuario == Usuario.id).all()
    return render_template('prestamos/todos.html', prestamos=prestamos)

@prestamos.route('/editar-prestamo/<int:id>', methods=['GET', 'POST'])
@admin_required
def editar_prestamo(id):
    prestamo = Prestamo.query.get_or_404(id)
    
    if request.method == 'POST':
        fecha_devolucion = request.form.get('fecha_devolucion')
        if fecha_devolucion:
            prestamo.fecha_devolucion = fecha_devolucion
        
        try:
            db.session.commit()
            flash('Préstamo actualizado con éxito.', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar el préstamo: {str(e)}', 'error')
        
        return redirect(url_for('prestamos.ver_todos_prestamos'))
    
    return render_template('prestamos/editar.html', prestamo=prestamo)

@prestamos.route('/eliminar-prestamo/<int:id>', methods=['POST'])
@admin_required
def eliminar_prestamo(id):
    prestamo = Prestamo.query.get_or_404(id)
    
    try:
        db.session.delete(prestamo)
        db.session.commit()
        flash('Préstamo eliminado con éxito.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar el préstamo: {str(e)}', 'error')
    
    return redirect(url_for('prestamos.ver_todos_prestamos'))



@prestamos.route('/mis-prestamos')
@login_required
def listar_prestamos():
    # Obtener el ID del usuario desde la sesión
    usuario_id = Usuario.query.filter_by(nombre=session['nombre']).first().id
    prestamos = Prestamo.query.filter_by(id_usuario=usuario_id).all()
    return render_template('prestamos/listar.html', prestamos=prestamos)

@prestamos.route('/solicitar-prestamo/<int:libro_id>', methods=['POST'])
@login_required
def solicitar_prestamo(libro_id):
    libro = Libros.query.get_or_404(libro_id)

    if libro.stock <= 0:
        flash('No hay stock disponible para este libro.', 'error')
        return redirect(url_for('libros.detalle', libro_id=libro.id))

    # Obtener el ID del usuario desde la sesión
    usuario_id = Usuario.query.filter_by(nombre=session['nombre']).first().id

    # Obtener la duración del préstamo desde el formulario
    duracion_dias = int(request.form['duracion'])
    fecha_prestamo = date.today()
    fecha_devolucion = fecha_prestamo + timedelta(days=duracion_dias)
    
    nuevo_prestamo = Prestamo(
        id_libro=libro.id,
        id_usuario=usuario_id,
        fecha_prestamo=fecha_prestamo,
        fecha_devolucion=fecha_devolucion
    )
    
    libro.stock -= 1  # Reducir el stock del libro
    
    try:
        db.session.add(nuevo_prestamo)
        db.session.commit()
        flash(f'Préstamo del libro "{libro.titulo}" realizado con éxito.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al realizar el préstamo: {str(e)}', 'error')
    
    return redirect(url_for('prestamos.listar_prestamos'))
