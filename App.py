from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL


app=Flask(__name__)

app.secret_key = 'appsecretkey' #clave secreta para la sesion

mysql=MySQL() #inicializa la conexion a la DB

# conexion a la DB
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_PORT'] = 3306
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'ventas'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql.init_app(app) #inicializa la conexion a la DB

@app.route('/')  # Decorador de la ruta principal
def home():
    return render_template('index.html')

@app.route('/logout')
def logout():
    return redirect(url_for('inicio'))

@app.route('/admin')  
def administrador():
    return render_template('admin.html')

@app.route('/listar')
def listar():
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM usuario')
    usuarios = cursor.fetchall()
    cursor.close()
    return render_template('listausuarios.html', usuarios=usuarios)

@app.route('/eliminar_usuario/<int:id>')
def eliminar_usuario(id):
    cursor = mysql.connection.cursor()
    cursor.execute('DELETE FROM usuario WHERE id = %s', (id,))
    mysql.connection.commit()
    cursor.close()
    flash('Usuario eliminado correctamente', 'success')
    return redirect(url_for('listar'))

@app.route('/editar_usuario_modal/<int:id>', methods=['POST'])
def editar_usuario_modal(id):
    nombre = request.form['nombre']
    email = request.form['email']
    password = request.form['password']

    cursor = mysql.connection.cursor()
    cursor.execute('UPDATE usuario SET nombre = %s, email = %s, password = %s WHERE id = %s',
                   (nombre, email, password, id))
    mysql.connection.commit()
    cursor.close()

    flash('Usuario actualizado correctamente', 'success')
    return redirect(url_for('listar'))

@app.route('/agregar_usuario', methods=['POST'])
def agregar_usuario():
    nombre = request.form['nombre']
    email = request.form['email']
    password = request.form['password']

    cursor = mysql.connection.cursor()
    cursor.execute('INSERT INTO usuario (nombre, email, password, id_rol) VALUES (%s, %s, %s, %s)',
                   (nombre, email, password, 2))
    mysql.connection.commit()
    cursor.close()

    flash('Usuario agregado correctamente', 'success')
    return redirect(url_for('listar'))

@app.route('/productos')
def productos():
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM productos')
    productos = cursor.fetchall()
    cursor.close()
    return render_template('listarproductos.html', productos=productos)

@app.route('/agregar_producto', methods=['POST'])
def agregar_producto():
    nombre = request.form['nombre']
    precio = request.form['precio']
    descripcion = request.form['descripcion']

    cursor = mysql.connection.cursor()
    cursor.execute('INSERT INTO productos (nombre, precio, descripcion) VALUES (%s, %s, %s)',
                   (nombre, precio, descripcion))
    mysql.connection.commit()
    cursor.close()

    flash('Producto agregado correctamente', 'success')
    return redirect(url_for('productos')) 

@app.route('/editar')
def editar():
    page = request.args.get('page', 1, type=int)
    buscar = request.args.get('buscar', '')
    
    cursor = mysql.connection.cursor()
    
    # Construir la consulta base
    if buscar:
        query = 'SELECT * FROM productos WHERE nombre LIKE %s ORDER BY id'
        count_query = 'SELECT COUNT(*) as total FROM productos WHERE nombre LIKE %s'
        params = (f'%{buscar}%',)
    else:
        query = 'SELECT * FROM productos ORDER BY id'
        count_query = 'SELECT COUNT(*) as total FROM productos'
        params = ()
    
    # Obtener el total de productos
    cursor.execute(count_query, params)
    total_result = cursor.fetchone()
    total = total_result['total'] if total_result else 0
    
    # Calcular paginación - CAMBIADO A 5 PRODUCTOS POR PÁGINA
    per_page = 5  # Solo 5 productos por página para probar
    pages = (total + per_page - 1) // per_page  # Cálculo de páginas totales
    
    # Calcular offset
    offset = (page - 1) * per_page
    
    # Consulta con paginación
    if buscar:
        query += ' LIMIT %s OFFSET %s'
        cursor.execute(query, (f'%{buscar}%', per_page, offset))
    else:
        query += ' LIMIT %s OFFSET %s'
        cursor.execute(query, (per_page, offset))
    
    productos_list = cursor.fetchall()
    cursor.close()
    
    # DEBUG: Verificar en consola
    print(f"DEBUG - Página: {page}, Total: {total}, Páginas: {pages}")
    print(f"DEBUG - Productos en esta página: {len(productos_list)}")
    
    # Crear objeto similar al de paginate de SQLAlchemy
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
    
    return render_template('editarproductos.html', productos=productos_paginados)


@app.route('/eliminar_producto/<int:id>')
def eliminar_producto(id):
    cursor = mysql.connection.cursor()
    cursor.execute('DELETE FROM productos WHERE id = %s', (id,))
    mysql.connection.commit()
    cursor.close()
    flash('Producto eliminado correctamente', 'success')
    return redirect(url_for('editar'))


@app.route('/editar_producto_modal/<int:id>', methods=['POST'])
def editar_producto_modal(id):
    nombre = request.form['nombre']
    precio = request.form['precio']
    descripcion = request.form['descripcion']

    cursor = mysql.connection.cursor()
    cursor.execute('UPDATE productos SET nombre = %s, precio = %s, descripcion = %s WHERE id = %s',
                   (nombre, precio, descripcion, id))
    mysql.connection.commit()
    cursor.close()

    flash('Producto actualizado correctamente', 'success')
    return redirect(url_for('editar'))

@app.route('/perfilusuario')
def perfilusuario():
    return render_template('perfilusuario.html')


@app.route('/accesologin', methods=['GET', 'POST'])
def accesologin():
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']

        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM usuario WHERE email = %s AND password = %s', (email, password))
        user = cursor.fetchone()
        cursor.close()

        if user:
            session['id_rol'] = user['id_rol']
            if user['id_rol'] == 1:
                return render_template('admin.html')
            elif user['id_rol'] == 2:
                return render_template('index.html')
        else:
            flash('Usuario y contraseña incorrectos', 'danger')
            return render_template('Login.html', error='Usuarios y contraseña incorrectos')  # Asegúrate que se llama Login.html

    return render_template('Login.html')


@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # Validar que las contraseñas coincidan
        if password != confirm_password:
            return render_template('Registro.html', error='Las contraseñas no coinciden')

        cursor = mysql.connection.cursor()

        # Verificar que no exista un usuario con ese email
        cursor.execute('SELECT * FROM usuario WHERE email = %s', (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            cursor.close()
            return render_template('Registro.html', error='El correo ya está registrado')

        # Insertar nuevo usuario (id_rol por defecto 2)
        cursor.execute('INSERT INTO usuario (nombre, email, password, id_rol) VALUES (%s, %s, %s, %s)',
                       (nombre, email, password, 2))
        mysql.connection.commit()
        cursor.close()

        return redirect(url_for('login'))

    # Si es GET solo mostrar el formulario
    return render_template('Registro.html')

@app.route('/inicio')  # Decorador de la ruta principal
def inicio():
    return render_template('index.html')

@app.route('/contacto')
def contacto(): # funtion de la ruta de contactos
    return render_template('Contactos.html')

@app.route('/contactopost', methods=['GET', 'POST'])
def contactopost():
    usuario={ #Diccionaroio para almacenar los datos del formulario
         'nombre': '',
         'email': '',
         'mensaje': ''
    }
    if request.method == 'POST':
       
       usuario['nombre'] = request.form.get('nombre')
       usuario['email'] = request.form.get('email')
       usuario['mensaje'] = request.form.get('mensaje')
    return render_template('Contactopost.html', user=usuario)

@app.route('/about') # funtion de la ruta de about
def about():
    return render_template('About.html')

@app.route('/login') # 
def login():
    return render_template('Login.html')

if __name__ == '__main__':
    app.run(debug=True, port=8000) #ejecuta la aplicacion en modo depuracion