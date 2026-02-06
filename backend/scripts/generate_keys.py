import secrets
from cryptography.fernet import Fernet

# Generate SECRET_KEY for JWT
secret_key = secrets.token_hex(32)
print(f"SECRET_KEY={secret_key}")

# Generate ENCRYPTION_KEY for Fernet
encryption_key = Fernet.generate_key().decode()
print(f"ENCRYPTION_KEY={encryption_key}")