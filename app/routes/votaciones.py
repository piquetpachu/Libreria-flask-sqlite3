from flask import Blueprint, request, redirect, url_for, flash, session
from models.controladordatabase import db, Votacion, Libros, Usuario,Comentario
from routes.login import login_required
from datetime import datetime


votaciones = Blueprint('votaciones', __name__)

@votaciones.route('/votar/<int:libro_id>', methods=['POST'])
@login_required
def votar(libro_id):
    # Obtener la calificación del formulario
    calificacion = int(request.form.get('calificacion'))
    
    # Obtener el ID del usuario actual
    usuario_id = Usuario.query.filter_by(nombre=session['nombre']).first().id
    
    # Verificar si el usuario ya votó por este libro
    votacion = Votacion.query.filter_by(id_libro=libro_id, id_usuario=usuario_id).first()

    if votacion:
        # Si ya votó, actualizar la calificación
        votacion.calificacion = calificacion
        flash(f'Has actualizado tu voto a {calificacion} estrellas.', 'success')
    else:
        # Si no ha votado, crear una nueva votación
        nueva_votacion = Votacion(id_libro=libro_id, id_usuario=usuario_id, calificacion=calificacion)
        db.session.add(nueva_votacion)
        flash(f'Has votado {calificacion} estrellas para este libro.', 'success')
    
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        flash(f'Error al registrar tu voto: {str(e)}', 'error')

    return redirect(url_for('libros.detalle', libro_id=libro_id))

@votaciones.route('/libro/<int:libro_id>/comentar', methods=['POST'])
def agregar_comentario(libro_id):
    usuario_id = session.get('usuario_id')  # Asegúrate de obtener el ID del usuario desde la sesión
    
    if usuario_id is None:  # Si no hay usuario en la sesión
        flash('Debes iniciar sesión para comentar.')
        return redirect(url_for('user.index_login'))  # Redirige a la página de inicio de sesión
    
    contenido_comentario = request.form.get('comentario')  # Obtén el comentario desde el formulario

    if not contenido_comentario:
        flash('El comentario no puede estar vacío.')
        print("************")
        print(session)  # Verifica qué valores están almacenados en la sesión
        print("************")
        print(contenido_comentario)
        print("************")
        return redirect(url_for('libros.detalle', libro_id=libro_id))

    try:
        # Crea el nuevo comentario
        nuevo_comentario = Comentario(id_libro=libro_id, id_usuario=usuario_id, comentario=contenido_comentario)
        db.session.add(nuevo_comentario)
        db.session.commit()
        flash('Comentario agregado con éxito.')
    except Exception as e:
        db.session.rollback()
        flash('Hubo un error al agregar el comentario.')
        print(f"Error: {str(e)}")
        print("************")
        print(session)  # Verifica qué valores están almacenados en la sesión
        print("************")

    return redirect(url_for('libros.detalle', libro_id=libro_id))

@votaciones.route('/comentario/eliminar/<int:comentario_id>', methods=['POST'])
def eliminar_comentario(comentario_id):
    # Buscar el comentario en la base de datos
    comentario = Comentario.query.get_or_404(comentario_id)
    
    # Verificar si el usuario es el dueño del comentario o un admin
    if session['rol'] == 'admin' or session['usuario_id'] == comentario.id_usuario:
        try:
            db.session.delete(comentario)
            db.session.commit()
            flash('Comentario eliminado con éxito.')
        except Exception as e:
            db.session.rollback()
            flash(f'Hubo un error al eliminar el comentario: {str(e)}')
    else:
        flash('No tienes permiso para eliminar este comentario.')
    
    # Redirigir a la página del libro
    return redirect(url_for('libros.detalle', libro_id=comentario.id_libro))
