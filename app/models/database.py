import sqlite3
from datetime import date

conn = sqlite3.connect('libreria.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS Libros (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT NOT NULL,
    autor TEXT NOT NULL,
    descripcion TEXT,
    fecha_emision TEXT NOT NULL,
    stock INTEGER NOT NULL,
    precio REAL NOT NULL,
    img TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS Prestamos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_libro INTEGER NOT NULL,
    id_usuario INTEGER NOT NULL,
    fecha_prestamo DATE NOT NULL,
    fecha_devolucion DATE,
    FOREIGN KEY(id_libro) REFERENCES Libros(id),
    FOREIGN KEY(id_usuario) REFERENCES Usuarios(id)
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS Usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    correo TEXT NOT NULL UNIQUE,
    contrasena TEXT NOT NULL,
    tel_cel TEXT,
    rol TEXT CHECK(rol IN ('admin', 'comun')) NOT NULL DEFAULT 'comun'
)
''')

def insertar_libro(titulo, autor, descripcion, fecha_emision, stock, precio, img):
    cursor.execute('''
    INSERT INTO Libros (titulo, autor, descripcion, fecha_emision, stock, precio, img)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (titulo, autor, descripcion, fecha_emision, stock, precio, img))
    conn.commit()

def insertar_prestamo(id_libro, id_usuario, fecha_prestamo, fecha_devolucion=None):
    cursor.execute('''
    INSERT INTO Prestamos (id_libro, id_usuario, fecha_prestamo, fecha_devolucion)
    VALUES (?, ?, ?, ?)
    ''', (id_libro, id_usuario, fecha_prestamo, fecha_devolucion))
    conn.commit()

def insertar_usuario(nombre, correo, contrasena, tel_cel=None, rol='comun'):
    cursor.execute('''
    INSERT INTO Usuarios (nombre, correo, contrasena, tel_cel, rol)
    VALUES (?, ?, ?, ?, ?)
    ''', (nombre, correo, contrasena, tel_cel, rol))
    conn.commit()

def editar_libro(id_libro, titulo, autor, descripcion, fecha_emision, stock, precio, img):
    cursor.execute('''
    UPDATE Libros SET titulo = ?, autor = ?, descripcion = ?, fecha_emision = ?, stock = ?, precio = ?, img = ?
    WHERE id = ?
    ''', (titulo, autor, descripcion, fecha_emision, stock, precio, img, id_libro))
    conn.commit()

def editar_prestamo(id_prestamo, id_libro, id_usuario, fecha_prestamo, fecha_devolucion):
    cursor.execute('''
    UPDATE Prestamos SET id_libro = ?, id_usuario = ?, fecha_prestamo = ?, fecha_devolucion = ?
    WHERE id = ?
    ''', (id_libro, id_usuario, fecha_prestamo, fecha_devolucion, id_prestamo))
    conn.commit()

def editar_usuario(id_usuario, nombre, correo, contrasena, tel_cel, rol):
    cursor.execute('''
    UPDATE Usuarios SET nombre = ?, correo = ?, contrasena = ?, tel_cel = ?, rol = ?
    WHERE id = ?
    ''', (nombre, correo, contrasena, tel_cel, rol, id_usuario))
    conn.commit()

def eliminar_libro(id_libro):
    cursor.execute('''
    DELETE FROM Libros WHERE id = ?
    ''', (id_libro,))
    conn.commit()

def eliminar_prestamo(id_prestamo):
    cursor.execute('''
    DELETE FROM Prestamos WHERE id = ?
    ''', (id_prestamo,))
    conn.commit()

def eliminar_usuario(id_usuario):
    cursor.execute('''
    DELETE FROM Usuarios WHERE id = ?
    ''', (id_usuario,))
    conn.commit()


# Insertar un libro
#insertar_libro("El señor de los anillos", "J.K Rollin", "un mundo fantasioso", "", 0, 0, "")

# Editar un libro
#editar_libro(1, "Don Quijote de la Mancha", "Miguel de Cervantes", "Una novela clásica y famosa", "1605-01-16", 5, 24.99, "don_quijote.jpg")

# Eliminar un libro
#eliminar_libro(1)

# Cerrar la conexión
conn.close()
