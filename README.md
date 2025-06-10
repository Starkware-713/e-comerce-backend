# 🛒 E-commerce API

API construida con **FastAPI** y conectada a una base de datos **PostgreSQL**, que incluye autenticación segura, gestión de usuarios, carritos de compra y productos.

---

## 📁 Estructura del Proyecto

```bash
.
├── app/
│   ├── models/        # Modelos SQLAlchemy
│   │   ├── __init__.py
│   │   ├── cart.py
│   │   ├── product.py 
│   │   └── user.py
│   ├── routers/       # Rutas de la API
│   │   ├── auth.py
│   │   ├── carts.py
│   │   ├── products.py 
│   │   └── users.py
│   ├── schemas/       # Esquemas Pydantic
│   │   ├── auth.py 
│   │   ├── cart.py 
│   │   ├── product.py
│   │   └── user.py
│   ├── utils/         # Funciones utilitarias
│   │   ├── __init__.py
│   │   └── auth.py
│   └── database.py    # Configuración de la base de datos
├── main.py           # Punto de entrada
└── requirements.txt  # Dependencias
```

---

## 🚀 Características

* 🧾 Registro y autenticación de usuarios
* 🔐 Seguridad con hashing de contraseñas
* 🛍️ Gestión de carritos de compra y productos
* 🧩 Estructura modular y escalable
* 🗄️ Conexión con PostgreSQL
* ✅ Validación robusta con Pydantic

---

## ⚙️ Requisitos Previos

### 1. Python 3.9+

* Descargar desde [python.org](https://www.python.org/downloads/)
* Asegúrate de activar la opción **"Add Python to PATH"** durante la instalación

### 2. PostgreSQL

* Instalar desde [postgresql.org](https://www.postgresql.org/download/)
* Guardar la contraseña del usuario `postgres`
* Crear una base de datos para el proyecto

---

## 🛠️ Configuración del Entorno

### 1. Clonar el Repositorio

```bash
git clone https://github.com/Starkware-713/e-comerce-backend
cd e-comerce-backend
```

### 2. Crear y Activar el Entorno Virtual

```bash
# Crear entorno virtual
python -m venv .venv

# Activar en PowerShell
.venv\Scripts\Activate.ps1

# Activar en CMD
.venv\Scripts\activate.bat
```

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 4. Crear archivo `.env`

```env
DATABASE_URL=postgresql://usuario:contraseña@localhost/nombre_db
PORT=8000  # Puerto opcional, por defecto 8000
```

> Reemplaza `usuario`, `contraseña` y `nombre_db` con tus datos reales.

---

## ▶️ Ejecutar la Aplicación

1. Asegúrate de que PostgreSQL esté activo
2. Verifica las credenciales en `.env`
3. Ejecuta el servidor con:

```bash
python main.py
# O alternativamente:
uvicorn main:app --reload
```

4. Abre en tu navegador: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🔄 Endpoints de la API

### 🔐 Autenticación

| Método | Endpoint          | Descripción                                      | Acceso     |
| ------ | ---------------- | ------------------------------------------------ | ---------- |
| POST   | `/auth/register` | Registrar nuevo usuario (comprador/vendedor)      | Público    |
| POST   | `/auth/login`    | Iniciar sesión y obtener tokens                  | Público    |
| POST   | `/auth/refresh`  | Renovar token de acceso usando refresh token     | Público    |

### 👤 Usuarios

| Método | Endpoint           | Descripción                 | Acceso      |
| ------ | ----------------- | --------------------------- | ----------- |
| POST   | `/users/`         | Crear nuevo usuario         | Público     |
| GET    | `/users/`         | Listar todos los usuarios   | Admin       |
| GET    | `/users/{id}`     | Obtener usuario por ID      | Autenticado |
| PUT    | `/users/{id}`     | Actualizar usuario          | Autenticado |
| DELETE | `/users/{id}`     | Eliminar usuario            | Admin       |

### 📦 Productos

| Método | Endpoint           | Descripción                | Acceso      |
| ------ | ----------------- | -------------------------- | ----------- |
| POST   | `/products/`      | Crear nuevo producto       | Vendedor    |
| GET    | `/products/`      | Listar todos los productos | Público     |
| GET    | `/products/{id}`  | Obtener producto por ID    | Público     |
| PUT    | `/products/{id}`  | Actualizar producto        | Vendedor    |
| DELETE | `/products/{id}`  | Eliminar producto          | Vendedor    |

### 🛍️ Carritos de Compra

| Método | Endpoint                    | Descripción                      | Acceso      |
| ------ | -------------------------- | -------------------------------- | ----------- |
| POST   | `/carts/`                  | Crear nuevo carrito              | Autenticado |
| GET    | `/carts/`                  | Listar carritos del usuario      | Autenticado |
| GET    | `/carts/{id}`              | Obtener carrito por ID          | Autenticado |
| POST   | `/carts/{id}/items`        | Agregar producto al carrito     | Autenticado |
| DELETE | `/carts/{id}/items/{item}` | Eliminar producto del carrito   | Autenticado |
| PUT    | `/carts/{id}/checkout`     | Procesar compra del carrito     | Autenticado |

---

## 📚 Documentación Detallada

### 🔑 Autenticación y Autorización

La API utiliza autenticación basada en JWT (JSON Web Tokens) con:
* Access Token: Para acceso a recursos protegidos (duración: 30 minutos)
* Refresh Token: Para renovar el access token (duración: 7 días)

#### Roles de Usuario
* 👑 **Admin**: Acceso total al sistema
* 🏪 **Vendedor**: Gestión de productos
* 🛒 **Comprador**: Gestión de carritos de compra

### 📖 Documentación Interactiva
* [Swagger UI](http://localhost:8000/docs): Interfaz interactiva para probar endpoints
* [ReDoc](http://localhost:8000/redoc): Documentación detallada y esquemas

---

## 🧰 Solución de Problemas

### ❌ Error de Conexión a la Base de Datos

* Asegúrate de que PostgreSQL está activo
* Verifica las credenciales del archivo `.env`
* Confirma que la base de datos fue creada

### ⚠️ Error al Activar el Entorno Virtual

```bash
Set-ExecutionPolicy RemoteSigned
```

> Ejecutar como administrador en PowerShell

### 🐍 Problemas con Dependencias

```bash
python -m pip install --upgrade pip
```

> Luego reinstala: `pip install -r requirements.txt`

---
