from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

# CAMBIO AQUÍ: Importamos las clases específicas para que Python las lea sí o sí
from database import engine, get_db
from models import Base, User, Product, CartItem

# Ahora Base sí sabe que existen User, Product y CartItem, y creará las 3 tablas
Base.metadata.create_all(bind=engine)

app = FastAPI(title="E-Commerce API con IA")

@app.get("/")
def read_root():
    return {
        "status": "API Funcionando",
        "proyecto": "E-Commerce Backend"
    }

@app.get("/test-db")
def test_database(db: Session = Depends(get_db)):
    try:
        # Intentamos contar los usuarios usando la clase User directamente
        num_usuarios = db.query(User).count()
        return {
            "status": "Conexión exitosa",
            "mensaje": "La base de datos responde correctamente y las tablas existen",
            "usuarios_registrados": num_usuarios
        }
    except Exception as e:
        return {
            "status": "Error",
            "mensaje": f"No se pudo conectar a la base de datos: {str(e)}"
        }