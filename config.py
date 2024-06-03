import secrets
import string

def generate_secret_key(length=24):
    alphabet = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(alphabet) for _ in range(length))

# Générer une clé secrète de 32 caractères
secret_key = generate_secret_key(32)
print("Clé secrète générée :", secret_key)
