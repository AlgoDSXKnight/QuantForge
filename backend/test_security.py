from app.core.security import hash_password, verify_password

password = "tejas123"

hashed = hash_password(password)

print("Original :", password)
print("Hashed   :", hashed)

print("\nVerification")

print(verify_password("tejas123", hashed))
print(verify_password("wrongpassword", hashed))