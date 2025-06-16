# 🛒 E-Commerce Backend API

> 🚀 Proyecto desarrollado como parte de la **Instancia Institucional de las Olimpiadas Nacionales de Educación Técnico Profesional (ETP) 2025**, en el área de **Programación**, siguiendo los lineamientos del [documento oficial del certamen (INET)](https://www.inet.edu.ar/wp-content/uploads/2025/06/ONETP_2025_Programacion_Estudiantes.pdf).

---

## 📚 Tabla de Contenidos

- [🌐 Despliegue y Documentación](#-despliegue-y-documentación)
- [🧩 Descripción General](#-descripción-general)
- [⚙️ Requisitos Previos](#️-requisitos-previos)
- [🛠️ Instalación](#️-instalación)
- [▶️ Ejecutar la Aplicación](#️-ejecutar-la-aplicación)
- [🧪 Autenticación](#-autenticación)
- [👤 Gestión de Usuario](#-gestión-de-usuario)
- [🛍️ Gestión de Productos](#️-gestión-de-productos)
- [🛒 Carrito](#-carrito)
- [📦 Órdenes](#-órdenes)
- [💳 Pagos (simulado)](#-pagos-simulado)
- [🧾 Validaciones](#-validaciones)
- [📦 Modelo de Datos](#-modelo-de-datos)
- [🔐 Seguridad](#-seguridad)
- [📁 Estructura del Proyecto](#-estructura-del-proyecto)
- [🧠 Recomendaciones](#-recomendaciones)
- [📌 Estado del Proyecto](#-estado-del-proyecto)
- [🙌 Créditos](#-créditos)
- [📝 Licencia](#-licencia)

---

## 🌐 Despliegue y Documentación

- 🔗 Producción: [https://e-comerce-backend-kudw.onrender.com](https://e-comerce-backend-kudw.onrender.com)
- 📘 Swagger UI: [https://e-comerce-backend-kudw.onrender.com/docs](https://e-comerce-backend-kudw.onrender.com/docs)
- 📕 ReDoc: [https://e-comerce-backend-kudw.onrender.com/redoc](https://e-comerce-backend-kudw.onrender.com/redoc)

---

## 🧩 Descripción General

API REST para la gestión completa de un sistema de e-commerce. Incluye:

- 🔐 Autenticación con JWT y Refresh Tokens
- 👥 Gestión de usuarios (comprador, vendedor, jefe de ventas)
- 🛍️ Catálogo de productos con filtros de búsqueda
- 🛒 Carrito de compras persistente
- 📦 Procesamiento y seguimiento de órdenes
- 💳 Pagos simulados con Mercado Pago
- 📚 Documentación generada automáticamente con Swagger / OpenAPI

---

## ⚙️ Requisitos Previos

- Python 3.9+
- PostgreSQL
- Git

---

## 🛠️ Instalación

```bash
# 1. Clonar el repositorio
git clone https://github.com/Starkware-713/e-comerce-backend
cd e-comerce-backend

# 2. Crear y activar entorno virtual
python -m venv .venv

# Linux/macOS
source .venv/bin/activate

# Windows
.venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
cp .env.example .env
````

Ejemplo `.env`:

```env
DATABASE_URL=postgresql://usuario:contraseña@localhost/nombre_db
PORT=8000
EMAIL_ADDRESS=your-email@gmail.com
EMAIL_PASSWORD=your-email-password
```

---

## ▶️ Ejecutar la Aplicación

```bash
uvicorn main:app --reload
```

Ir a [http://localhost:8000/docs](http://localhost:8000/docs) para explorar la documentación interactiva.

---

## 🧪 Autenticación

### 🔐 Registro

```http
POST /auth/register
```

```json
{
  "email": "usuario@ejemplo.com",
  "password": "Contraseña123!",
  "confirm_password": "Contraseña123!",
  "name": "Nombre",
  "lastname": "Apellido",
  "rol": "comprador"
}
```

### 🔓 Login

```http
POST /auth/login
```

Respuesta:

```json
{
  "access_token": "...",
  "refresh_token": "...",
  "token_type": "bearer"
}
```

---

## 👤 Gestión de Usuario

* Obtener perfil: `GET /user/my-profile`
* Actualizar perfil: `PUT /user/update-profile`
* Cambiar contraseña: `POST /user/change-password`

---

## 🛍️ Gestión de Productos

* Listar productos: `GET /products`
* Buscar productos: `GET /products/search?q=...`
* Crear producto: `POST /products` (solo vendedores o jefe de ventas)
* Obtener por ID: `GET /products/{id}`

---

## 🛒 Carrito

* Ver carrito: `GET /cart`
* Agregar: `POST /cart/add`
* Actualizar: `PUT /cart/update`
* Eliminar: `DELETE /cart/remove/{product_id}`

---

## 📦 Órdenes

* Crear orden: `POST /orders`
* Listar órdenes: `GET /orders`
* Ver orden: `GET /orders/{order_id}`

---

## 💳 Pagos (simulado)

* Procesar: `POST /payment/process`

---

## 🧾 Validaciones

**Contraseña:**

* Mínimo 8 caracteres
* Al menos una mayúscula, una minúscula, un número y un símbolo

**Roles permitidos:**

* `comprador`
* `vendedor`
* `jefe_ventas`

---

## 📦 Modelo de Datos

![Modelo de Datos](docs/modelo%20de%20datos.png)

### Entidades Principales

| Entidad      | Atributos                                                      |
| ------------ | -------------------------------------------------------------- |
| **Usuario**  | ID, Nombre, Apellido, Email, Contraseña, Rol, Estado           |
| **Producto** | ID, Nombre, Descripción, Precio, Stock, Categoría, Vendedor ID |
| **Carrito**  | ID, Usuario ID, Items, Total, Estado                           |
| **Orden**    | ID, Usuario ID, Items, Total, Estado, Fechas                   |
| **Pago**     | ID, Orden ID, Monto, Método, Estado, Fecha                     |
| **Venta**    | ID, Orden ID, Factura, Total, IVA, Estado, Fecha               |

---

## 🔐 Seguridad

* Autenticación con JWT + Refresh Tokens
* Middleware de autorización basado en roles:

  * 👤 Comprador: acceso a órdenes y carrito
  * 🏪 Vendedor: gestión de productos y ventas
  * 👑 Jefe de ventas: acceso total al sistema

---

## 📁 Estructura del Proyecto

```bash
.
├── app/
│   ├── models/
│   ├── routers/
│   ├── schemas/
│   ├── utils/
│   └── database.py
├── main.py
├── requirements.txt
└── docs/
```

---

## 🧠 Recomendaciones

* Implementar interceptores HTTP en el frontend
* Centralizar manejo de errores
* Usar caché para productos populares
* Guardar carrito en `localStorage`
* Utilizar debounce en el buscador

---

## 📌 Estado del Proyecto

🚧 En desarrollo activo. Versión actual: `1.0.0`

---

## 🙌 Créditos

Desarrollado por **Walter Carrasco**, estudiante de 7mo año de ETP en la **Escuela N.º 713 'Juan Abdala Chayep'**, Esquel, Chubut.
Participación en la **Olimpíada Nacional INET 2025** – Área Programación.

---

## 📝 Licencia

Este proyecto se distribuye bajo licencia educativa con fines exclusivamente académicos y formativos en el marco de las Olimpiadas ETP 2025.


