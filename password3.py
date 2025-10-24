from passlib.context import CryptContext

contexto = CryptContext(
    schemes=["pbkdf2_sha256"], 
    default="pbkdf2_sha256",
    pbkdf2_sha256__default_rounds=30000
    
)
texto = "x?1_p-M.4!eM"
texto_encriptado = contexto.hash(texto)
print(f"Contraseña encriptada: {texto_encriptado}")

print(f" verificando la contraseña... {contexto.verify(texto, texto_encriptado)}")

