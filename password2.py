
from werkzeug.security import generate_password_hash, check_password_hash

texto = "x?1_p-M.4!eM"

texto_encriptado = generate_password_hash(texto)
print(f"Texto encriptado: {texto_encriptado}")

print(f"¿El texto es correcto? {check_password_hash(texto_encriptado, texto)}")