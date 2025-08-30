from flask import Flask, render_template

app=Flask(__name__)

@app.route('/inicio')  # Decorador de la ruta principal
def inicio():
    return render_template('index.html')

@app.route('/contacto')
def contacto(): # funtion de la ruta de contactos
    return render_template('Contactos.html')

@app.route('/about') # funtion de la ruta de about
def about():
    return render_template('About.html')

@app.route('/login') # 
def login():
    return render_template('Login.html')

@app.route('/Registro') # 
def Registro():
    return "render_template('Registro.html')" 

if __name__ == '__main__':
    app.run(debug=True, port=8000) #ejecuta la aplicacion en modo depuracion