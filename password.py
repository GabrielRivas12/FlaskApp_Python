from flask import Flask 
from flask_bcrypt import Bcrypt

App = Flask(__name__)
bcrypt = Bcrypt(App)

password = "mi_contraseña_secreta"
hash_password = bcrypt.generate_password_hash(password).decode('utf-8')
print(f"Hashed Password: {hash_password}")

# Verificación de la contraseña
contraseña_interna = bcrypt.check_password_hash(hash_password, password)
print(f"La contraseña es correcta:? {contraseña_interna}")