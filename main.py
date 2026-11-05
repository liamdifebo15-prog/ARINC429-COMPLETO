print("CRUD de usuarios y juegos")
print("El programa funciona correctamente")
ç

print("CRUD de usuarios y juegos")
print("El programa funciona correctamente")
python3 main.py
import sqlite3

# ==========================================
# CONEXION A LA BASE DE DATOS
# ==========================================

conexion = sqlite3.connect("usuarios_juegos.db")
conexion.execute("PRAGMA foreign_keys = ON")

cursor = conexion.cursor()


# ==========================================
# CREACION DE LAS TABLAS
# ==========================================

def crear_tablas():

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS juegos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            genero TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios_juegos (
            usuario_id INTEGER NOT NULL,
            juego_id INTEGER NOT NULL,

            PRIMARY KEY (usuario_id, juego_id),

            FOREIGN KEY (usuario_id)
                REFERENCES usuarios(id) ON DELETE CASCADE,

            FOREIGN KEY (juego_id)
                REFERENCES juegos(id) ON DELETE CASCADE
        )
    """)

    conexion.commit()


# ==========================================
# CRUD DE USUARIOS
# ==========================================

def crear_usuario():

    print("\n--- CREAR USUARIO ---")

    nombre = input("Nombre: ").strip()
    email = input("Email: ").strip()

    if not nombre or not email:
        print("Error: todos los campos son obligatorios.")
        return

    try:
        cursor.execute("""
            INSERT INTO usuarios (nombre, email)
            VALUES (?, ?)
        """, (nombre, email))

        conexion.commit()
        print("Usuario creado correctamente.")

    except sqlite3.IntegrityError:
        print("Error: ese email ya esta registrado.")


def listar_usuarios():

    print("\n--- LISTA DE USUARIOS ---")

    cursor.execute("""
        SELECT id, nombre, email
        FROM usuarios
        ORDER BY id
    """)

    usuarios = cursor.fetchall()

    if not usuarios:
        print("No hay usuarios registrados.")
        return

    for usuario in usuarios:
        print(
            f"ID: {usuario[0]} | "
            f"Nombre: {usuario[1]} | "
            f"Email: {usuario[2]}"
        )


def modificar_usuario():

    print("\n--- MODIFICAR USUARIO ---")

    listar_usuarios()

    try:
        id_usuario = int(input("\nID del usuario: "))
    except ValueError:
        print("El ID debe ser un numero.")
        return

    cursor.execute(
        "SELECT id FROM usuarios WHERE id = ?",
        (id_usuario,)
    )

    if cursor.fetchone() is None:
        print("Usuario no encontrado.")
        return

    nombre = input("Nuevo nombre: ").strip()
    email = input("Nuevo email: ").strip()

    if not nombre or not email:
        print("Error: todos los campos son obligatorios.")
        return

    try:
        cursor.execute("""
            UPDATE usuarios
            SET nombre = ?, email = ?
            WHERE id = ?
        """, (nombre, email, id_usuario))

        conexion.commit()
        print("Usuario modificado correctamente.")

    except sqlite3.IntegrityError:
        print("Error: ese email ya pertenece a otro usuario.")


def eliminar_usuario():

    print("\n--- ELIMINAR USUARIO ---")

    listar_usuarios()

    try:
        id_usuario = int(input("\nID del usuario a eliminar: "))
    except ValueError:
        print("El ID debe ser un numero.")
        return

    cursor.execute(
        "SELECT nombre FROM usuarios WHERE id = ?",
        (id_usuario,)
    )

    usuario = cursor.fetchone()

    if usuario is None:
        print("Usuario no encontrado.")
        return

    confirmar = input(
        f"¿Eliminar a {usuario[0]}? (s/n): "
    ).strip().lower()

    if confirmar == "s":
        cursor.execute(
            "DELETE FROM usuarios WHERE id = ?",
            (id_usuario,)
        )

        conexion.commit()
        print("Usuario eliminado correctamente.")
    else:
        print("Operacion cancelada.")


# ==========================================
# CRUD DE JUEGOS
# ==========================================

def crear_juego():

    print("\n--- CREAR JUEGO ---")

    nombre = input("Nombre del juego: ").strip()
    genero = input("Genero: ").strip()

    if not nombre or not genero:
        print("Error: todos los campos son obligatorios.")
        return

    cursor.execute("""
        INSERT INTO juegos (nombre, genero)
        VALUES (?, ?)
    """, (nombre, genero))

    conexion.commit()
    print("Juego creado correctamente.")


def listar_juegos():

    print("\n--- LISTA DE JUEGOS ---")

    cursor.execute("""
        SELECT id, nombre, genero
        FROM juegos
        ORDER BY id
    """)

    juegos = cursor.fetchall()

    if not juegos:
        print("No hay juegos registrados.")
        return

    for juego in juegos:
        print(
            f"ID: {juego[0]} | "
            f"Nombre: {juego[1]} | "
            f"Genero: {juego[2]}"
        )


def modificar_juego():

    print("\n--- MODIFICAR JUEGO ---")

    listar_juegos()

    try:
        id_juego = int(input("\nID del juego: "))
    except ValueError:
        print("El ID debe ser un numero.")
        return

    cursor.execute(
        "SELECT id FROM juegos WHERE id = ?",
        (id_juego,)
    )

    if cursor.fetchone() is None:
        print("Juego no encontrado.")
        return

    nombre = input("Nuevo nombre: ").strip()
    genero = input("Nuevo genero: ").strip()

    if not nombre or not genero:
        print("Error: todos los campos son obligatorios.")
        return

    cursor.execute("""
        UPDATE juegos
        SET nombre = ?, genero = ?
        WHERE id = ?
    """, (nombre, genero, id_juego))

    conexion.commit()
    print("Juego modificado correctamente.")


def eliminar_juego():

    print("\n--- ELIMINAR JUEGO ---")

    listar_juegos()

    try:
        id_juego = int(input("\nID del juego a eliminar: "))
    except ValueError:
        print("El ID debe ser un numero.")
        return

    cursor.execute(
        "SELECT nombre FROM juegos WHERE id = ?",
        (id_juego,)
    )

    juego = cursor.fetchone()

    if juego is None:
        print("Juego no encontrado.")
        return

    confirmar = input(
        f"¿Eliminar {juego[0]}? (s/n): "
    ).strip().lower()

    if confirmar == "s":
        cursor.execute(
            "DELETE FROM juegos WHERE id = ?",
            (id_juego,)
        )

        conexion.commit()
        print("Juego eliminado correctamente.")
    else:
        print("Operacion cancelada.")


# ==========================================
# RELACION USUARIOS Y JUEGOS
# ==========================================

def asignar_juego():

    print("\n--- ASIGNAR JUEGO A USUARIO ---")

    listar_usuarios()

    try:
        id_usuario = int(input("\nID del usuario: "))
    except ValueError:
        print("El ID debe ser un numero.")
        return

    cursor.execute(
        "SELECT nombre FROM usuarios WHERE id = ?",
        (id_usuario,)
    )

    usuario = cursor.fetchone()

    if usuario is None:
        print("Usuario no encontrado.")
        return

    listar_juegos()

    try:
        id_juego = int(input("\nID del juego: "))
    except ValueError:
        print("El ID debe ser un numero.")
        return

    cursor.execute(
        "SELECT nombre FROM juegos WHERE id = ?",
        (id_juego,)
    )

    juego = cursor.fetchone()

    if juego is None:
        print("Juego no encontrado.")
        return

    try:
        cursor.execute("""
            INSERT INTO usuarios_juegos (usuario_id, juego_id)
            VALUES (?, ?)
        """, (id_usuario, id_juego))

        conexion.commit()

        print(
            f"{juego[0]} fue asignado a {usuario[0]} correctamente."
        )

    except sqlite3.IntegrityError:
        print("Ese juego ya esta asignado a ese usuario.")


def consultar_usuarios_juegos():

    print("\n--- USUARIOS Y SUS JUEGOS ---")

    cursor.execute("""
        SELECT
            usuarios.id,
            usuarios.nombre,
            usuarios.email,
            juegos.id,
            juegos.nombre,
            juegos.genero
        FROM usuarios_juegos
        INNER JOIN usuarios
            ON usuarios.id = usuarios_juegos.usuario_id
        INNER JOIN juegos
            ON juegos.id = usuarios_juegos.juego_id
        ORDER BY usuarios.nombre, juegos.nombre
    """)

    resultados = cursor.fetchall()

    if not resultados:
        print("No hay juegos asignados a usuarios.")
        return

    for fila in resultados:
        print(
            f"Usuario: {fila[1]} ({fila[2]}) | "
            f"Juego: {fila[4]} | "
            f"Genero: {fila[5]}"
        )


def consultar_juegos_usuario():

    print("\n--- CONSULTAR JUEGOS DE UN USUARIO ---")

    listar_usuarios()

    try:
        id_usuario = int(input("\nID del usuario: "))
    except ValueError:
        print("El ID debe ser un numero.")
        return

    cursor.execute("""
        SELECT nombre
        FROM usuarios
        WHERE id = ?
    """, (id_usuario,))

    usuario = cursor.fetchone()

    if usuario is None:
        print("Usuario no encontrado.")
        return

    cursor.execute("""
        SELECT juegos.nombre, juegos.genero
        FROM usuarios_juegos
        INNER JOIN juegos
            ON juegos.id = usuarios_juegos.juego_id
        WHERE usuarios_juegos.usuario_id = ?
        ORDER BY juegos.nombre
    """, (id_usuario,))

    juegos = cursor.fetchall()

    print(f"\nJuegos de {usuario[0]}:")

    if not juegos:
        print("Este usuario no tiene juegos asignados.")
        return

    for juego in juegos:
        print(f"- {juego[0]} | Genero: {juego[1]}")


# ==========================================
# MENU PRINCIPAL
# ==========================================

def menu():

    crear_tablas()

    while True:

        print("""
========================================
       CRUD DE USUARIOS Y JUEGOS
========================================

USUARIOS
1. Crear usuario
2. Listar usuarios
3. Modificar usuario
4. Eliminar usuario

JUEGOS
5. Crear juego
6. Listar juegos
7. Modificar juego
8. Eliminar juego

RELACIONES
9. Asignar juego a usuario
10. Consultar usuarios y juegos
11. Consultar juegos de un usuario

0. Salir
========================================
""")

        opcion = input("Selecciona una opcion: ").strip()

        if opcion == "1":
            crear_usuario()

        elif opcion == "2":
            listar_usuarios()

        elif opcion == "3":
            modificar_usuario()

        elif opcion == "4":
            eliminar_usuario()

        elif opcion == "5":
            crear_juego()

        elif opcion == "6":
            listar_juegos()

        elif opcion == "7":
            modificar_juego()

        elif opcion == "8":
            eliminar_juego()

        elif opcion == "9":
            asignar_juego()

        elif opcion == "10":
            consultar_usuarios_juegos()

        elif opcion == "11":
            consultar_juegos_usuario()

        elif opcion == "0":
            print("Cerrando el programa...")
            break

        else:
            print("Opcion no valida. Intenta nuevamente.")


# ==========================================
# INICIO DEL PROGRAMA
# ==========================================

try:
    menu()
finally:
    conexion.close()
