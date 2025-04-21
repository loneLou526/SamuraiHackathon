from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

password = "hello"  # Здесь укажи нужный пароль
hashed_password = pwd_context.hash(password)

print("Хэш пароля:", hashed_password)