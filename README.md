# 🛒 E-commerce API

API construida con **FastAPI** y conectada a una base de datos **PostgreSQL**, que incluye autenticación segura, gestión de usuarios, carritos de compra y productos.

---

## 📁 Estructura del Proyecto

```bash
.
├── app/
│   ├── models/        # Modelos SQLAlchemy
│   │   ├── cart.py 
│   │   ├── product.py 
│   │   └── user.py
│   ├── routers/       # Rutas de la API
│   │   ├── carts.py
│   │   ├── products.py 
│   │   └── users.py
│   ├── schemas/       # Esquemas Pydantic
│   │   ├── cart.py 
│   │   ├── product.py
│   │   └── user.py
│   ├── database.py    # Configuración de la base de datos
│   └── utils.py       # Funciones utilitarias
├── .env               # Variables de entorno
├── main.py            # Punto de entrada
└── requirements.txt   # Dependencias
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
```

> Reemplaza `usuario`, `contraseña` y `nombre_db` con tus datos reales.

---

## ▶️ Ejecutar la Aplicación

1. Asegúrate de que PostgreSQL esté activo
2. Verifica las credenciales en `.env`
3. Ejecuta el servidor con:

```bash
uvicorn main:app --reload
```

4. Abre en tu navegador: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🔄 Endpoints Principales

### 🛍️ Carritos de Compra

| Método | Endpoint           | Descripción                |
| ------ | ------------------ | -------------------------- |
| POST   | `/carts/`          | Crear carrito              |
| GET    | `/carts/`          | Obtener todos los carritos |
| GET    | `/carts/{cart_id}` | Obtener carrito por ID     |

### 👤 Usuarios

| Método | Endpoint           | Descripción               |
| ------ | ------------------ | ------------------------- |
| POST   | `/users/`          | Crear nuevo usuario       |
| GET    | `/users/`          | Listar todos los usuarios |
| GET    | `/users/{user_id}` | Obtener usuario por ID    |

### 📦 Productos

| Método | Endpoint         | Descripción             |
| ------ | ---------------- | ----------------------- |
| POST   | `/products/`     | Crear nuevo producto    |
| GET    | `/products/`     | Listar productos        |
| GET    | `/products/{id}` | Obtener producto por ID |

---

## 📚 Documentación de la API

* [Swagger UI](http://localhost:8000/docs)
* [ReDoc](http://localhost:8000/redoc)

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
