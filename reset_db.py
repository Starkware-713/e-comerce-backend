from app.database import engine
from app.models.user import Base as UserBase
from app.models.product import Base as ProductBase
from app.models.cart import Base as CartBase

def reset_database():
    # Drop all tables
    UserBase.metadata.drop_all(bind=engine)
    ProductBase.metadata.drop_all(bind=engine)
    CartBase.metadata.drop_all(bind=engine)
    print("Tablas eliminadas correctamente")

    # Create all tables
    UserBase.metadata.create_all(bind=engine)
    ProductBase.metadata.create_all(bind=engine)
    CartBase.metadata.create_all(bind=engine)
    print("Tablas creadas correctamente")

if __name__ == "__main__":
    confirmation = input("¿Estás seguro de que deseas reiniciar la base de datos? Todos los datos serán eliminados. (s/N): ")
    if confirmation.lower() == 's':
        reset_database()
        print("Base de datos reiniciada correctamente")
    else:
        print("Operación cancelada")
