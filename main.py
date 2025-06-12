from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

from app.database import engine, Base
from app.routers import users, carts, products, auth, orders, sales, order_management, payment

# Carga de variables de entorno
load_dotenv()

# Crear la aplicación FastAPI
app = FastAPI(
    title="API E-commerce con FastAPI y PostgreSQL",
    description="API para una webapp de e-commerce utilizando FastAPI y PostgreSQL",
    version="1.0.0"
)

# Crear las tablas en la base de datos
create_tables()

# Agregar middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Incluir rutas
app.include_router(auth.router)  #rutas de autenticación
app.include_router(users.router) #rutas de usuarios 
app.include_router(carts.router) #rutas de carritos
app.include_router(products.router) #rutas de productos 
app.include_router(orders.router) #rutas de órdenes
app.include_router(order_management.router) #rutas de gestión de órdenes
app.include_router(sales.router) #rutas de ventas
app.include_router(payment.router) #rutas de pagos

@app.get("/")
def read_root():
    return {"message": "Bienvenido a la api"}

# Obtener el puerto de la variable de entorno o usar el predeterminado
port = 8000

# Para despliegue
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port)
