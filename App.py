from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
from passlib.hash import pbkdf2_sha256
from datetime import datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

app = Flask(__name__)

app.secret_key = 'appsecretkey'  # clave secreta para la sesion

mysql = MySQL()  # inicializa la conexion a la DB

# conexion a la DB
app.config['MYSQL_HOST'] = 'bhkpenjua0fqusqf6wi0-mysql.services.clever-cloud.com'
app.config['MYSQL_PORT'] = 3306
app.config['MYSQL_USER'] = 'uyckttcjtyg86kts'
app.config['MYSQL_PASSWORD'] = '15PRdRINHs4qQ3QFb15W'
app.config['MYSQL_DB'] = 'bhkpenjua0fqusqf6wi0'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql.init_app(app)  # inicializa la conexion a la DB

# Ruta para diagnosticar la estructura de la tabla
@app.route('/debug_table')
def debug_table():
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("DESCRIBE reservaciones")
        estructura = cursor.fetchall()
        cursor.close()
        
        resultado = "<h3>Estructura de la tabla reservaciones:</h3>"
        for columna in estructura:
            resultado += f"<p><strong>{columna['Field']}</strong>: {columna['Type']} - Null: {columna['Null']} - Default: {columna['Default']}</p>"
        
        return resultado
    except Exception as e:
        return f"Error: {str(e)}"

@app.route('/')  # Decorador de la ruta principal
def home():
    return render_template('index.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Sesión cerrada correctamente', 'info')
    return redirect(url_for('inicio'))

@app.route('/admin')
def administrador():
    if 'id_rol' not in session or session['id_rol'] != 1:
        flash('Acceso denegado. Se requieren privilegios de administrador.', 'danger')
        return redirect(url_for('login'))
    
    cursor = mysql.connection.cursor()
    
    # Obtener conteo de usuarios
    cursor.execute('SELECT COUNT(*) as total FROM usuario')
    total_usuarios = cursor.fetchone()['total']
    
    # Obtener conteo de productos/viajes
    cursor.execute('SELECT COUNT(*) as total FROM productos')
    total_productos = cursor.fetchone()['total']
    
    # Obtener conteo de reservaciones/habitaciones
    cursor.execute('SELECT COUNT(*) as total FROM reservaciones')
    total_reservaciones = cursor.fetchone()['total']
    
    cursor.close()
    
    return render_template('admin.html', 
                         total_usuarios=total_usuarios,
                         total_productos=total_productos,
                         total_reservaciones=total_reservaciones)

@app.route('/listar')
def listar():
    if 'id_rol' not in session or session['id_rol'] != 1:
        flash('Acceso denegado. Se requieren privilegios de administrador.', 'danger')
        return redirect(url_for('login'))
    
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM usuario ORDER BY id')
    usuarios = cursor.fetchall()
    cursor.close()
    return render_template('listausuarios.html', usuarios=usuarios)

@app.route('/eliminar_usuario/<int:id>')
def eliminar_usuario(id):
    if 'id_rol' not in session or session['id_rol'] != 1:
        flash('Acceso denegado. Se requieren privilegios de administrador.', 'danger')
        return redirect(url_for('login'))
    
    cursor = mysql.connection.cursor()
    cursor.execute('DELETE FROM usuario WHERE id = %s', (id,))
    mysql.connection.commit()
    cursor.close()
    flash('Usuario eliminado correctamente', 'success')
    return redirect(url_for('listar'))

@app.route('/agregar_usuario', methods=['POST'])
def agregar_usuario():
    if 'id_rol' not in session or session['id_rol'] != 1:
        flash('Acceso denegado. Se requieren privilegios de administrador.', 'danger')
        return redirect(url_for('login'))
    
    nombre = request.form['nombre']
    email = request.form['email']
    password = request.form['password']
    id_rol = request.form['id_rol']
    
    # Validar que las contraseñas coincidan
    confirm_password = request.form['confirm_password']
    if password != confirm_password:
        flash('Las contraseñas no coinciden', 'danger')
        return redirect(url_for('listar'))
    
    # Encriptar la contraseña
    hashed_password = pbkdf2_sha256.hash(password)

    cursor = mysql.connection.cursor()
    
    # Verificar si el email ya existe
    cursor.execute('SELECT * FROM usuario WHERE email = %s', (email,))
    existing_user = cursor.fetchone()
    
    if existing_user:
        flash('El correo electrónico ya está registrado', 'danger')
        cursor.close()
        return redirect(url_for('listar'))
    
    cursor.execute('INSERT INTO usuario (nombre, email, password, id_rol) VALUES (%s, %s, %s, %s)',
                   (nombre, email, hashed_password, id_rol))
    mysql.connection.commit()
    cursor.close()

    flash('Usuario agregado correctamente', 'success')
    return redirect(url_for('listar'))

@app.route('/editar_usuario_modal/<int:id>', methods=['POST'])
def editar_usuario_modal(id):
    if 'id_rol' not in session or session['id_rol'] != 1:
        flash('Acceso denegado. Se requieren privilegios de administrador.', 'danger')
        return redirect(url_for('login'))
    
    nombre = request.form['nombre']
    email = request.form['email']
    password = request.form['password']
    id_rol = request.form['id_rol']

    cursor = mysql.connection.cursor()
    
    # Verificar si el email ya existe en otro usuario
    cursor.execute('SELECT * FROM usuario WHERE email = %s AND id != %s', (email, id))
    existing_user = cursor.fetchone()
    
    if existing_user:
        flash('El correo electrónico ya está registrado por otro usuario', 'danger')
        cursor.close()
        return redirect(url_for('listar'))
    
    # Si se proporcionó una nueva contraseña, encriptarla
    if password and password != "":
        if not password.startswith('$pbkdf2-sha256$'):
            hashed_password = pbkdf2_sha256.hash(password)
            cursor.execute('UPDATE usuario SET nombre = %s, email = %s, password = %s, id_rol = %s WHERE id = %s',
                           (nombre, email, hashed_password, id_rol, id))
        else:
            cursor.execute('UPDATE usuario SET nombre = %s, email = %s, password = %s, id_rol = %s WHERE id = %s',
                           (nombre, email, password, id_rol, id))
    else:
        cursor.execute('UPDATE usuario SET nombre = %s, email = %s, id_rol = %s WHERE id = %s',
                       (nombre, email, id_rol, id))
    
    mysql.connection.commit()
    cursor.close()

    flash('Usuario actualizado correctamente', 'success')
    return redirect(url_for('listar'))  

@app.route('/productos')
def productos():
    if 'id_rol' not in session or session['id_rol'] != 1:
        flash('Acceso denegado. Se requieren privilegios de administrador.', 'danger')
        return redirect(url_for('login'))
    
    page = request.args.get('page', 1, type=int)
    buscar = request.args.get('buscar', '')
    por_pagina = request.args.get('por_pagina', 5, type=int)

    cursor = mysql.connection.cursor()

    # Construir la consulta base para PRODUCTOS
    if buscar:
        query = '''SELECT * FROM productos 
                   WHERE nombre LIKE %s OR origen LIKE %s OR destino LIKE %s OR aerolinea LIKE %s 
                   ORDER BY id DESC'''
        count_query = '''SELECT COUNT(*) as total FROM productos 
                         WHERE nombre LIKE %s OR origen LIKE %s OR destino LIKE %s OR aerolinea LIKE %s'''
        params = (f'%{buscar}%', f'%{buscar}%', f'%{buscar}%', f'%{buscar}%')
    else:
        query = 'SELECT * FROM productos ORDER BY id DESC'
        count_query = 'SELECT COUNT(*) as total FROM productos'
        params = ()

    # Obtener el total de productos
    cursor.execute(count_query, params)
    total_result = cursor.fetchone()
    total = total_result['total'] if total_result else 0

    # Calcular paginación
    per_page = por_pagina
    pages = (total + per_page - 1) // per_page

    # Calcular offset
    offset = (page - 1) * per_page

    # Consulta con paginación
    if buscar:
        query += ' LIMIT %s OFFSET %s'
        cursor.execute(query, (f'%{buscar}%', f'%{buscar}%', f'%{buscar}%', f'%{buscar}%', per_page, offset))
    else:
        query += ' LIMIT %s OFFSET %s'
        cursor.execute(query, (per_page, offset))

    productos_list = cursor.fetchall()
    cursor.close()

    # Crear objeto de paginación
    class Pagination:
        def __init__(self, items, page, per_page, total, pages):
            self.items = items
            self.page = page
            self.per_page = per_page
            self.total = total
            self.pages = pages
            self.has_prev = page > 1
            self.has_next = page < pages
            self.prev_num = page - 1 if page > 1 else None
            self.next_num = page + 1 if page < pages else None

        def iter_pages(self, left_edge=2, left_current=2, right_current=3, right_edge=2):
            last = 0
            for num in range(1, self.pages + 1):
                if (num <= left_edge or
                    (num > self.page - left_current - 1 and num < self.page + right_current) or
                    num > self.pages - right_edge):
                    if last + 1 != num:
                        yield None
                    yield num
                    last = num

    productos_paginados = Pagination(
        items=productos_list,
        page=page,
        per_page=per_page,
        total=total,
        pages=pages
    )

    return render_template('listarDestinos.html', productos=productos_paginados)

@app.route('/agregar_producto', methods=['POST'])
def agregar_producto():
    if 'id_rol' not in session or session['id_rol'] != 1:
        flash('Acceso denegado. Se requieren privilegios de administrador.', 'danger')
        return redirect(url_for('login'))
    
    nombre = request.form['nombre']
    precio = request.form['precio']
    descripcion = request.form['descripcion']
    origen = request.form['origen']
    destino = request.form['destino']
    fecha_salida = request.form['fecha_salida']
    fecha_regreso = request.form['fecha_regreso']
    aerolinea = request.form['aerolinea']

    cursor = mysql.connection.cursor()
    cursor.execute('''INSERT INTO productos (nombre, precio, descripcion, origen, destino, fecha_salida, fecha_regreso, aerolinea) 
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s)''',
                   (nombre, precio, descripcion, origen, destino, fecha_salida, fecha_regreso, aerolinea))
    mysql.connection.commit()
    cursor.close()

    flash('Destino agregado correctamente', 'success')
    return redirect(url_for('productos'))

@app.route('/eliminar_producto/<int:id>')
def eliminar_producto(id):
    if 'id_rol' not in session or session['id_rol'] != 1:
        flash('Acceso denegado. Se requieren privilegios de administrador.', 'danger')
        return redirect(url_for('login'))
    
    cursor = mysql.connection.cursor()
    cursor.execute('DELETE FROM productos WHERE id = %s', (id,))
    mysql.connection.commit()
    cursor.close()
    flash('Producto eliminado correctamente', 'success')
    return redirect(url_for('productos'))

@app.route('/editar_producto/<int:id>', methods=['POST'])
def editar_producto(id):
    if 'id_rol' not in session or session['id_rol'] != 1:
        flash('Acceso denegado. Se requieren privilegios de administrador.', 'danger')
        return redirect(url_for('login'))
    
    nombre = request.form['nombre']
    precio = request.form['precio']
    descripcion = request.form['descripcion']
    origen = request.form['origen']
    destino = request.form['destino']
    fecha_salida = request.form['fecha_salida']
    fecha_regreso = request.form['fecha_regreso']
    aerolinea = request.form['aerolinea']

    cursor = mysql.connection.cursor()
    cursor.execute('''UPDATE productos SET 
                   nombre = %s, precio = %s, descripcion = %s, origen = %s, 
                   destino = %s, fecha_salida = %s, fecha_regreso = %s, aerolinea = %s 
                   WHERE id = %s''',
                   (nombre, precio, descripcion, origen, destino, fecha_salida, fecha_regreso, aerolinea, id))
    mysql.connection.commit()
    cursor.close()

    flash('Producto actualizado correctamente', 'success')
    return redirect(url_for('productos'))

@app.route('/editar')
def editar():
    if 'id_rol' not in session or session['id_rol'] != 1:
        flash('Acceso denegado. Se requieren privilegios de administrador.', 'danger')
        return redirect(url_for('login'))
    
    page = request.args.get('page', 1, type=int)
    buscar = request.args.get('buscar', '')
    por_pagina = request.args.get('por_pagina', 5, type=int)

    cursor = mysql.connection.cursor()

    # Construir la consulta base para RESERVACIONES
    if buscar:
        query = 'SELECT * FROM reservaciones WHERE nombrelugar LIKE %s OR ubicacion LIKE %s ORDER BY id'
        count_query = 'SELECT COUNT(*) as total FROM reservaciones WHERE nombrelugar LIKE %s OR ubicacion LIKE %s'
        params = (f'%{buscar}%', f'%{buscar}%')
    else:
        query = 'SELECT * FROM reservaciones ORDER BY id'
        count_query = 'SELECT COUNT(*) as total FROM reservaciones'
        params = ()

    # Obtener el total de reservaciones
    cursor.execute(count_query, params)
    total_result = cursor.fetchone()
    total = total_result['total'] if total_result else 0

    # Calcular paginación
    per_page = por_pagina
    pages = (total + per_page - 1) // per_page

    # Calcular offset
    offset = (page - 1) * per_page

    # Consulta con paginación
    if buscar:
        query += ' LIMIT %s OFFSET %s'
        cursor.execute(query, (f'%{buscar}%', f'%{buscar}%', per_page, offset))
    else:
        query += ' LIMIT %s OFFSET %s'
        cursor.execute(query, (per_page, offset))

    reservaciones_list = cursor.fetchall()
    cursor.close()

    # Crear objeto de paginación
    class Pagination:
        def __init__(self, items, page, per_page, total, pages):
            self.items = items
            self.page = page
            self.per_page = per_page
            self.total = total
            self.pages = pages
            self.has_prev = page > 1
            self.has_next = page < pages
            self.prev_num = page - 1 if page > 1 else None
            self.next_num = page + 1 if page < pages else None

        def iter_pages(self, left_edge=2, left_current=2, right_current=3, right_edge=2):
            last = 0
            for num in range(1, self.pages + 1):
                if (num <= left_edge or
                    (num > self.page - left_current - 1 and num < self.page + right_current) or
                    num > self.pages - right_edge):
                    if last + 1 != num:
                        yield None
                    yield num
                    last = num

    reservaciones_paginadas = Pagination(
        items=reservaciones_list,
        page=page,
        per_page=per_page,
        total=total,
        pages=pages
    )

    return render_template('listarReservas.html', reservaciones=reservaciones_paginadas)

@app.route('/reservaciones')
def reservaciones():
    if 'id_rol' not in session:
        flash('Debes iniciar sesión para ver las reservaciones', 'warning')
        return redirect(url_for('login'))
    
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM reservaciones ORDER BY id DESC LIMIT 5')
    reservaciones = cursor.fetchall()
    cursor.close()
    return render_template('listarReservas.html', reservaciones=reservaciones)

@app.route('/agregar_reservacion', methods=['POST'])
def agregar_reservacion():
    if 'id_rol' not in session:
        flash('Debes iniciar sesión para agregar reservaciones', 'warning')
        return redirect(url_for('login'))
    
    try:
        nombrelugar = request.form['nombrelugar']
        nhabitacion = request.form['nhabitacion']
        tipohabitacion = request.form['tipohabitacion']
        cantidadh = int(request.form['cantidadh'])

        # Leer input de precio como string
        precio_input = request.form.get('precionoche', '').strip()
        if precio_input == '':
            flash('El precio es requerido', 'danger')
            return redirect(url_for('editar'))

        # Usar Decimal para evitar problemas de precisión
        try:
            precionoche = Decimal(precio_input)
        except InvalidOperation:
            flash('Precio inválido. Usa un formato numérico, p.ej. 123.45', 'danger')
            return redirect(url_for('editar'))

        # Validaciones de rango (ajusta maximo_si_necesario)
        if precionoche < 0:
            flash('El precio no puede ser negativo', 'danger')
            return redirect(url_for('editar'))

        # Límite razonable (ejemplo: 9,999,999.99)
        maximo = Decimal('9999999.99')
        if precionoche > maximo:
            flash('El precio es demasiado alto', 'danger')
            return redirect(url_for('editar'))

        # Redondear a 2 decimales (mitad hacia arriba)
        precionoche = precionoche.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        descripcion = request.form['descripcion']
        ubicacion = request.form['ubicacion']

        # DEBUG (opcional)
        print(f"DEBUG: Insertando precio: {precionoche} (tipo: {type(precionoche)})")

        cursor = mysql.connection.cursor()
        cursor.execute('''INSERT INTO reservaciones 
                       (nombrelugar, nhabitacion, tipohabitacion, cantidadh, precionoche, descripcion, ubicacion) 
                       VALUES (%s, %s, %s, %s, %s, %s, %s)''',
                       (nombrelugar, nhabitacion, tipohabitacion, cantidadh, str(precionoche), descripcion, ubicacion))
        mysql.connection.commit()
        cursor.close()

        flash('Reservación agregada correctamente', 'success')
        return redirect(url_for('editar'))
    
    except ValueError:
        flash('Error en los datos numéricos. Verifica que cantidad y precio sean números válidos.', 'danger')
        return redirect(url_for('editar'))
    except Exception as e:
        flash(f'Error al agregar reservación: {str(e)}', 'danger')
        return redirect(url_for('editar'))
    
@app.route('/eliminar_reservacion/<int:id>')
def eliminar_reservacion(id):
    if 'id_rol' not in session or session['id_rol'] != 1:
        flash('Acceso denegado. Se requieren privilegios de administrador.', 'danger')
        return redirect(url_for('login'))
    
    cursor = mysql.connection.cursor()
    cursor.execute('DELETE FROM reservaciones WHERE id = %s', (id,))
    mysql.connection.commit()
    cursor.close()
    flash('Reservación eliminada correctamente', 'success')
    return redirect(url_for('editar'))

@app.route('/accesologin', methods=['GET', 'POST'])
def accesologin():
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password_candidate = request.form['password']

        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM usuario WHERE email = %s', (email,))
        user = cursor.fetchone()
        cursor.close()

        if user:
            if pbkdf2_sha256.verify(password_candidate, user['password']):
                session['id_rol'] = user['id_rol']
                session['user_email'] = user['email']
                session['user_id'] = user['id']
                session['user_nombre'] = user['nombre']

                if user['id_rol'] == 1:
                    flash('Bienvenido Administrador', 'success')
                    return redirect(url_for('administrador'))
                elif user['id_rol'] == 2:
                    flash('Bienvenido Usuario', 'success')
                    return redirect(url_for('iniciou'))
            else:
                flash('Contraseña incorrecta', 'danger')
                return render_template('Login.html', error='Contraseña incorrecta')
        else:
            flash('Usuario no encontrado', 'danger')
            return render_template('Login.html', error='Usuario no encontrado')

    return render_template('Login.html')

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            return render_template('Registro.html', error='Las contraseñas no coinciden')

        hashed_password = pbkdf2_sha256.hash(password)

        cursor = mysql.connection.cursor()

        cursor.execute('SELECT * FROM usuario WHERE email = %s', (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            cursor.close()
            return render_template('Registro.html', error='El correo ya está registrado')

        cursor.execute('INSERT INTO usuario (nombre, email, password, id_rol) VALUES (%s, %s, %s, %s)',
                       (nombre, email, hashed_password, 2))
        mysql.connection.commit()
        cursor.close()

        flash('Registro exitoso. Ahora puedes iniciar sesión.', 'success')
        return redirect(url_for('login'))

    return render_template('Registro.html')

@app.route('/perfilusuario')
def perfilusuario():
    if 'id_rol' not in session:
        flash('Debes iniciar sesión para ver tu perfil', 'warning')
        return redirect(url_for('login'))

    cursor = mysql.connection.cursor()

    if 'user_email' in session:
        cursor.execute('SELECT * FROM usuario WHERE email = %s', (session['user_email'],))
    else:
        flash('Sesión inválida, por favor inicia sesión nuevamente', 'error')
        return redirect(url_for('login'))

    usuario = cursor.fetchone()
    cursor.close()

    if usuario:
        return render_template('perfilusuario.html',
                             nombre=usuario['nombre'],
                             email=usuario['email'])
    else:
        flash('No se pudo encontrar la información del usuario', 'error')
        return redirect(url_for('inicio'))

@app.route('/inicio')
def inicio():
    return render_template('index.html')

@app.route('/contacto')
def contacto():
    return render_template('Contactos.html')

@app.route('/iniciousuario')
def iniciou():
    if 'id_rol' not in session or session['id_rol'] != 2:
        flash('Debes iniciar sesión como usuario', 'warning')
        return redirect(url_for('login'))
    return render_template('iniciousuario.html')

@app.route('/contactopost', methods=['GET', 'POST'])
def contactopost():
    usuario = {
         'nombre': '',
         'email': '',
         'mensaje': ''
    }
    if request.method == 'POST':
       usuario['nombre'] = request.form.get('nombre')
       usuario['email'] = request.form.get('email')
       usuario['mensaje'] = request.form.get('mensaje')
    return render_template('Contactopost.html', user=usuario)

@app.route('/editar_producto_modal/<int:id>', methods=['POST'])
def editar_producto_modal(id):
    if 'id_rol' not in session or session['id_rol'] != 1:
        flash('Acceso denegado. Se requieren privilegios de administrador.', 'danger')
        return redirect(url_for('login'))
    
    try:
        nombrelugar = request.form['nombrelugar']
        nhabitacion = request.form['nhabitacion']
        tipohabitacion = request.form['tipohabitacion']
        cantidadh = int(request.form['cantidadh'])
        
        # Misma solución para editar
        precio_input = request.form['precionoche']
        precionoche = float(precio_input)
        precionoche = round(precionoche, 2)  # 2 decimales para precios
        
        descripcion = request.form['descripcion']
        ubicacion = request.form['ubicacion']

        cursor = mysql.connection.cursor()
        cursor.execute('''UPDATE reservaciones SET 
                       nombrelugar = %s, nhabitacion = %s, tipohabitacion = %s, cantidadh = %s, 
                       precionoche = %s, descripcion = %s, ubicacion = %s 
                       WHERE id = %s''',
                       (nombrelugar, nhabitacion, tipohabitacion, cantidadh, precionoche, descripcion, ubicacion, id))
        mysql.connection.commit()
        cursor.close()

        flash('Reservación actualizada correctamente', 'success')
        return redirect(url_for('editar'))
    
    except ValueError as e:
        flash('Error en los datos numéricos. Verifica que cantidad y precio sean números válidos.', 'danger')
        return redirect(url_for('editar'))
    except Exception as e:
        flash(f'Error al actualizar reservación: {str(e)}', 'danger')
        return redirect(url_for('editar'))

@app.route('/about')
def about():
    return render_template('About.html')

@app.route('/login')
def login():
    return render_template('Login.html')

if __name__ == '__main__':
    app.run(debug=True, port=8000)