from app.db.database import engine
from app.models.warehouse import Base

print("Creating EROI warehouse tables...")

Base.metadata.create_all(bind=engine)

print("EROI warehouse tables created successfully.")