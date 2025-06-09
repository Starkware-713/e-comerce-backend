# FastAPI PostgreSQL API

Este proyecto es una API basada en FastAPI que se conecta a una base de datos PostgreSQL. Incluye autenticación y registro de usuarios con métodos de seguridad.

## Estructura del Proyecto
```
.
├── app/
│   ├── models/         # Modelos SQLAlchemy
│   ├── routers/        # Rutas de la API
│   ├── schemas/        # Esquemas Pydantic
│   ├── database.py     # Configuración de la base de datos
│   └── utils.py        # Utilidades
├── .env               # Variables de entorno
├── main.py            # Punto de entrada de la aplicación
└── requirements.txt   # Dependencias del proyecto
```

## Características
- Registro de usuarios
- Autenticación de usuarios
- Manejo seguro de contraseñas
- Integración con PostgreSQL
- Validación de datos con Pydantic
- Estructura modular y escalable

## Requisitos Previos

1. **Python**
   - Instalar Python 3.9 o superior desde [python.org](https://www.python.org/downloads/)
   - Asegurarse de marcar la opción "Add Python to PATH" durante la instalación

2. **PostgreSQL**
   - Descargar e instalar PostgreSQL desde [postgresql.org](https://www.postgresql.org/download/)
   - Anotar la contraseña del usuario 'postgres' durante la instalación
   - Crear una base de datos para el proyecto

## Configuración del Entorno

1. **Clonar el Repositorio**
   ```bash
   git clone https://github.com/Starkware-713/e-comerce-backend
   cd e-comerce-backend
   ```

2. **Crear y Activar el Entorno Virtual**
   ```bash
   # Crear el entorno virtual
   python -m venv .venv

   # Activar el entorno virtual
   # En Windows (PowerShell):
   .venv\Scripts\Activate.ps1
   # En Windows (CMD):
   .venv\Scripts\activate.bat
   ```

3. **Instalar Dependencias**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar Variables de Entorno**
   - Crear un archivo `.env` en la raíz del proyecto
   - Agregar la siguiente configuración:
     ```env
     DATABASE_URL=postgresql://usuario:contraseña@localhost/nombre_db
     ```
   - Reemplazar 'usuario', 'contraseña' y 'nombre_db' con tus credenciales de PostgreSQL

## Iniciar la Aplicación

1. **Verificar la Conexión a la Base de Datos**
   - Asegurarse de que PostgreSQL esté corriendo
   - Verificar que las credenciales en `.env` sean correctas

2. **Ejecutar el Servidor**
   ```bash
   uvicorn main:app --reload
   ```

3. **Verificar la Instalación**
   - Abrir en el navegador: http://localhost:8000/docs
   - Deberías ver la documentación Swagger UI de la API

## Solución de Problemas Comunes

1. **Error de Conexión a la Base de Datos**
   - Verificar que PostgreSQL esté corriendo
   - Comprobar las credenciales en el archivo `.env`
   - Asegurarse de que la base de datos existe

2. **Error al Activar el Entorno Virtual**
   - Ejecutar PowerShell como administrador
   - Ejecutar: `Set-ExecutionPolicy RemoteSigned`
   - Intentar activar el entorno virtual nuevamente

3. **Error al Instalar Dependencias**
   - Actualizar pip: `python -m pip install --upgrade pip`
   - Intentar instalar las dependencias nuevamente

## Endpoints

### Usuarios
- `POST /users/`: Crear nuevo usuario
- `GET /users/`: Listar usuarios
- `GET /users/{user_id}`: Obtener usuario por ID

## Documentación API
Una vez que el servidor esté corriendo, puedes acceder a:
- Documentación Swagger UI: http://localhost:8000/docs
- Documentación ReDoc: http://localhost:8000/redoc
