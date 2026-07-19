from app.database.base import Base
from app.database.connection import engine

import app.models


print("Creating tables...")

Base.metadata.create_all(bind=engine)

print("Done!")