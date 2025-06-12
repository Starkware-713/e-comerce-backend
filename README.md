# 🛒 E-commerce API

API REST desarrollada con **FastAPI** y conectada a una base de datos **PostgreSQL**, que incluye autenticación JWT, gestión de usuarios con roles, carritos de compra, productos, órdenes, pagos y sistema de facturación.

## ✨ Características Principales

- 🔐 Autenticación JWT con tokens de acceso y refresco
- 👥 Gestión de usuarios con roles (comprador, vendedor)
- 🛒 Sistema de carrito de compras
- 📦 Gestión de productos
- 📋 Sistema de órdenes y ventas
- 💳 Procesamiento de pagos con múltiples métodos
- 📧 Envío de correos electrónicos de confirmación
- 📄 Generación automática de facturas con IVA
- 📚 Documentación automática con Swagger/OpenAPI

---

## 🛠️ Endpoints de la API

### 🔑 Autenticación (`/auth`)

| Método | Endpoint          | Descripción                                |
|--------|------------------|------------------------------------------|
| POST   | `/auth/register` | Registro de usuarios (comprador/vendedor)  |
| POST   | `/auth/login`    | Inicio de sesión y obtención de tokens    |
| POST   | `/auth/refresh`  | Renovación de token de acceso             |

### 👥 Usuarios (`/users`)

| Método | Endpoint        | Descripción                    |
|--------|----------------|--------------------------------|
| POST   | `/users/`      | Crear nuevo usuario            |
| GET    | `/users/`      | Listar usuarios (rol admin)    |
| GET    | `/users/{id}`  | Obtener detalles de usuario    |

### 📦 Productos (`/products`)

| Método | Endpoint           | Descripción                |
|--------|------------------|----------------------------|
| POST   | `/products/`     | Crear producto (vendedor)   |
| GET    | `/products/`     | Listar productos           |
| GET    | `/products/{id}` | Obtener producto           |
| PUT    | `/products/{id}` | Actualizar producto        |
| DELETE | `/products/{id}` | Eliminar producto          |

### 🛒 Carrito (`/carts`)

| Método | Endpoint          | Descripción                |
|--------|------------------|----------------------------|
| POST   | `/carts/`        | Crear carrito             |
| GET    | `/carts/`        | Ver carrito actual        |
| POST   | `/carts/items`   | Agregar producto          |
| DELETE | `/carts/items`   | Eliminar producto         |
| PUT    | `/carts/items`   | Actualizar cantidad       |

### 📋 Órdenes (`/orders`)

| Método | Endpoint          | Descripción                |
|--------|------------------|----------------------------|
| POST   | `/orders/`       | Crear orden desde carrito  |
| GET    | `/orders/`       | Listar órdenes            |
| GET    | `/orders/{id}`   | Ver detalles de orden     |

### 💳 Pagos (`/payment`)

| Método | Endpoint            | Descripción                      |
|--------|-------------------|----------------------------------|
| POST   | `/payment/process` | Procesar pago de orden          |

### 📊 Ventas (`/sales`)

| Método | Endpoint          | Descripción                |
|--------|------------------|----------------------------|
| GET    | `/sales/`        | Listar ventas             |
| GET    | `/sales/{id}`    | Ver detalles de venta     |


## 📦 Modelo de Datos

![Modelo de Datos](docs/modelo%20de%20datos.png)

| Entidad   | Atributos |
|-----------|-----------|
| **Usuario** | ID, Nombre, Apellido, Email, Contraseña (hasheada), Rol (comprador/vendedor), Estado activo |
| **Producto** | ID, Nombre, Descripción, Precio, Stock, Categoría, Vendedor ID |
| **Carrito** | ID, Usuario ID, Items, Total, Estado |
| **Orden** | ID, Usuario ID, Items, Total, Estado, Fecha de creación, Fecha de pago |
| **Pago** | ID, Orden ID, Monto, Método de pago, Estado, ID de transacción, Fecha |
| **Venta** | ID, Orden ID, Número de factura, Monto total, IVA, Estado, Fecha |

---

## 🔒 Seguridad y Autenticación

### Autenticación JWT
- Access Token (30 minutos)
- Refresh Token (7 días)
- Payload con rol de usuario

### Roles y Permisos
- 👤 Comprador: Gestión de carrito y órdenes
- 🏪 Vendedor: Gestión de productos
- 👑 Admin: Acceso total al sistema

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

## 🔧 Variables de Entorno Requeridas

```env
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
PORT=8000
EMAIL_ADDRESS=your-email@gmail.com
EMAIL_PASSWORD=your-email-password
```

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
pip install -r requirements.txt
```

## 📦 Estado del Proyecto

En desarrollo activo. Versión actual: 1.0.0

## 📚 Documentación API

La documentación completa de la API está disponible en:
- 🔍 Swagger UI: `http://localhost:8000/docs`
- 📖 ReDoc: `http://localhost:8000/redoc`
