from flask import Flask, render_template

app=Flask(__name__)

@app.route('/')  # Decorador de la ruta principal
def inicio():
    return render_template('index.html')

@app.route('/contacto')
def contacto(): # funtion de la ruta de contactos
    return "Pagina de contactosss"

@app.route('/about') # funtion de la ruta de about
def about():
    return "esta es el acerca de"

@app.route('/servicios/<nombre>')
def servicios (nombre):
    return 'El nomnre del servicio es %s ' % nombre


if __name__ == '__main__':
    app.run(debug=True, port=8000) #ejecuta la aplicacion en modo depuracion