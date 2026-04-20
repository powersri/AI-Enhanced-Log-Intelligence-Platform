from passlib.context import CryptContext

# Use PBKDF2 with SHA-256 for password hashing, which is a secure choice for modern applications. 
# The "deprecated" option is set to "auto" to allow for future updates to the hashing scheme without breaking existing hashes.

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)