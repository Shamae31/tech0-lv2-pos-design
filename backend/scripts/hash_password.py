from getpass import getpass
from passlib.context import CryptContext

password = getpass("Password: ")
if not password:
    raise SystemExit("Password must not be empty")
if len(password.encode("utf-8")) > 72:
    raise SystemExit("Password must be at most 72 UTF-8 bytes")
print(CryptContext(schemes=["bcrypt"], deprecated="auto").hash(password))
