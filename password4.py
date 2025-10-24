from cryptography.fernet import Fernet

texto = "x21"

# Generar una clave y crear un objeto fernet

clave = Fernet.generate_key()
objeto = Fernet(clave)

#Encriptar el texto
texto_encriptado = objeto.encrypt(texto.encode())
print(f"Texto encriptado {texto_encriptado}")

# Desencriptar el texto
texto_desencriptado = objeto.decrypt(texto_encriptado).decode()
print(f"Texto encontrado: {texto_desencriptado}")