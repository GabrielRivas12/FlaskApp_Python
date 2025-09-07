from flask import Flask, render_template, request, redirect, url_for, session
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

@app.route('/admin')  
def administrador():
    return render_template('admin.html')

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
            
                pass

        # Si usuario no encontrado o contraseña incorrecta, muestra login con error
        return render_template('login.html', error='Credenciales incorrectas')

    
    return render_template('login.html')

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