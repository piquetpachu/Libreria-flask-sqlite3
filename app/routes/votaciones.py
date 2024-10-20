from flask import Blueprint, request, redirect, url_for, flash, session
from models.controladordatabase import db, Votacion, Libros, Usuario,Comentario
from routes.login import login_required
from datetime import datetime


votaciones = Blueprint('votaciones', __name__)

@votaciones.route('/votar/<int:libro_id>', methods=['POST'])
@login_required
def votar(libro_id):
    calificacion = int(request.form.get('calificacion'))
    
    usuario_id = Usuario.query.filter_by(nombre=session['nombre']).first().id
    
    votacion = Votacion.query.filter_by(id_libro=libro_id, id_usuario=usuario_id).first()

    if votacion:
        votacion.calificacion = calificacion
        flash(f'Has actualizado tu voto a {calificacion} estrellas.', 'success')
    else:
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
@login_required
def agregar_comentario(libro_id):
    usuario_id = session.get('usuario_id')  
     
    contenido_comentario = request.form.get('comentario')  

    if not contenido_comentario:
        flash('El comentario no puede estar vacío.')
        print("************")
        print(session)  
        print("************")
        print(contenido_comentario)
        print("************")
        return redirect(url_for('libros.detalle', libro_id=libro_id))

    try:
        nuevo_comentario = Comentario(id_libro=libro_id, id_usuario=usuario_id, comentario=contenido_comentario)
        db.session.add(nuevo_comentario)
        db.session.commit()
        flash('Comentario agregado con éxito.')
    except Exception as e:
        db.session.rollback()
        flash('Hubo un error al agregar el comentario.')
        print(f"Error: {str(e)}")
        print("************")
        print(session) 
        print("************")

    return redirect(url_for('libros.detalle', libro_id=libro_id))

@votaciones.route('/comentario/eliminar/<int:comentario_id>', methods=['POST'])
def eliminar_comentario(comentario_id):
    comentario = Comentario.query.get_or_404(comentario_id)
    
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
    
    return redirect(url_for('libros.detalle', libro_id=comentario.id_libro))
