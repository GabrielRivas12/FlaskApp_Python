from flask import Flask, render_template, request

app=Flask(__name__)

@app.route('/')  # Decorador de la ruta principal
def home():
    return render_template('index.html')

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

@app.route('/Registro') # 
def Registro():
    return render_template('Registro.html') 

if __name__ == '__main__':
    app.run(debug=True, port=8000) #ejecuta la aplicacion en modo depuracion