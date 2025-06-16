# E-Commerce Backend API

Esta API proporciona los endpoints necesarios para gestionar un e-commerce, incluyendo autenticación, gestión de usuarios, productos, carritos y órdenes.

## Configuración Base

La API está desplegada en: `https://e-comerce-backend-kudw.onrender.com`

Para todas las peticiones que requieren autenticación, incluir el token JWT en el header:
```typescript
headers: {
  'Authorization': 'Bearer ' + token
}
```

## Autenticación

### Registro de Usuario
```typescript
POST /auth/register
Content-Type: application/json

{
  "email": "usuario@ejemplo.com",
  "password": "Contraseña123!",
  "confirm_password": "Contraseña123!",
  "name": "Nombre",
  "lastname": "Apellido",
  "rol": "comprador" // o "vendedor"
}
```

### Iniciar Sesión
```typescript
POST /auth/login
Content-Type: application/json

{
  "email": "usuario@ejemplo.com",
  "password": "Contraseña123!"
}

// Respuesta
{
  "access_token": "...",
  "refresh_token": "...",
  "token_type": "bearer"
}
```

## Gestión de Usuario

### Obtener Perfil
```typescript
GET /user/my-profile
Headers: {
  'Authorization': 'Bearer ' + token
}

// Respuesta
{
  "id": 1,
  "email": "usuario@ejemplo.com",
  "name": "Nombre",
  "lastname": "Apellido",
  "is_active": true,
  "rol": "comprador"
}
```

### Actualizar Perfil
```typescript
PUT /user/update-profile
Headers: {
  'Authorization': 'Bearer ' + token
}
Content-Type: application/json

{
  "name": "Nuevo Nombre",      // opcional
  "lastname": "Nuevo Apellido",// opcional
  "email": "nuevo@email.com"   // opcional
}
```

### Cambiar Contraseña
```typescript
POST /user/change-password
Headers: {
  'Authorization': 'Bearer ' + token
}
Content-Type: application/json

{
  "current_password": "Contraseña123!",
  "new_password": "NuevaContraseña123!",
  "confirm_password": "NuevaContraseña123!"
}
```

## Gestión de Productos

### Listar Productos
```typescript
GET /products
Query params:
- skip: number (opcional, por defecto 0)
- limit: number (opcional, por defecto 100)
```

### Buscar Productos
```typescript
GET /products/search?q=término
```

### Obtener Producto por ID
```typescript
GET /products/{product_id}
```

### Crear Producto (Solo vendedores)
```typescript
POST /products
Headers: {
  'Authorization': 'Bearer ' + token
}
Content-Type: application/json

{
  "name": "Nombre del producto",
  "description": "Descripción detallada",
  "price": 99.99,
  "stock": 100,
  "category": "Categoría"
}
```

## Carrito de Compras

### Obtener Carrito
```typescript
GET /cart
Headers: {
  'Authorization': 'Bearer ' + token
}
```

### Agregar Producto al Carrito
```typescript
POST /cart/add
Headers: {
  'Authorization': 'Bearer ' + token
}
Content-Type: application/json

{
  "product_id": 1,
  "quantity": 2
}
```

### Actualizar Cantidad
```typescript
PUT /cart/update
Headers: {
  'Authorization': 'Bearer ' + token
}
Content-Type: application/json

{
  "product_id": 1,
  "quantity": 3
}
```

### Eliminar Producto del Carrito
```typescript
DELETE /cart/remove/{product_id}
Headers: {
  'Authorization': 'Bearer ' + token
}
```

## Órdenes

### Crear Orden
```typescript
POST /orders
Headers: {
  'Authorization': 'Bearer ' + token
}
```

### Listar Órdenes del Usuario
```typescript
GET /orders
Headers: {
  'Authorization': 'Bearer ' + token
}
```

### Obtener Orden por ID
```typescript
GET /orders/{order_id}
Headers: {
  'Authorization': 'Bearer ' + token
}
```

## Validaciones

### Contraseña
La contraseña debe cumplir con los siguientes requisitos:
- Mínimo 8 caracteres
- Al menos una letra mayúscula
- Al menos una letra minúscula
- Al menos un número
- Al menos un carácter especial

### Roles
- `comprador`: Puede comprar productos
- `vendedor`: Puede vender productos y gestionar su inventario

## Manejo de Errores

La API devuelve errores en el siguiente formato:
```json
{
  "detail": "Mensaje descriptivo del error"
}
```

Códigos de error comunes:
- 400: Error de validación o datos inválidos
- 401: No autenticado o token inválido
- 403: No autorizado para realizar la acción
- 404: Recurso no encontrado
- 500: Error interno del servidor

## Ejemplos de Integración

### Angular - Servicio de Autenticación
```typescript
@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private apiUrl = 'https://e-comerce-backend-kudw.onrender.com';

  constructor(private http: HttpClient) {}

  login(email: string, password: string) {
    return this.http.post<any>(`${this.apiUrl}/auth/login`, {
      email,
      password
    }).pipe(
      tap(response => {
        localStorage.setItem('token', response.access_token);
        localStorage.setItem('refresh_token', response.refresh_token);
      })
    );
  }

  getProfile() {
    return this.http.get<any>(`${this.apiUrl}/user/my-profile`);
  }

  // Interceptor para agregar el token a todas las peticiones
  intercept(request: HttpRequest<any>, next: HttpHandler) {
    const token = localStorage.getItem('token');
    
    if (token) {
      request = request.clone({
        headers: request.headers.set('Authorization', `Bearer ${token}`)
      });
    }
    
    return next.handle(request);
  }
}
```

### Angular - Servicio de Productos
```typescript
@Injectable({
  providedIn: 'root'
})
export class ProductService {
  private apiUrl = 'https://e-comerce-backend-kudw.onrender.com/products';

  constructor(private http: HttpClient) {}

  getProducts(skip = 0, limit = 10) {
    return this.http.get<any>(`${this.apiUrl}?skip=${skip}&limit=${limit}`);
  }

  searchProducts(query: string) {
    return this.http.get<any>(`${this.apiUrl}/search?q=${query}`);
  }

  getProduct(id: number) {
    return this.http.get<any>(`${this.apiUrl}/${id}`);
  }
}
```

### Angular - Servicio de Carrito
```typescript
@Injectable({
  providedIn: 'root'
})
export class CartService {
  private apiUrl = 'https://e-comerce-backend-kudw.onrender.com/cart';

  constructor(private http: HttpClient) {}

  getCart() {
    return this.http.get<any>(this.apiUrl);
  }

  addToCart(productId: number, quantity: number) {
    return this.http.post<any>(`${this.apiUrl}/add`, {
      product_id: productId,
      quantity
    });
  }

  updateQuantity(productId: number, quantity: number) {
    return this.http.put<any>(`${this.apiUrl}/update`, {
      product_id: productId,
      quantity
    });
  }

  removeFromCart(productId: number) {
    return this.http.delete<any>(`${this.apiUrl}/remove/${productId}`);
  }
}
```

## Recomendaciones de Implementación

1. Manejo de Tokens:
   - Guarda el token en localStorage o sessionStorage
   - Implementa un interceptor HTTP para incluir el token en todas las peticiones
   - Maneja la renovación automática del token cuando expire

2. Manejo de Errores:
   - Implementa un interceptor HTTP para manejar errores de forma centralizada
   - Muestra mensajes de error amigables al usuario
   - Redirecciona al login cuando recibas un 401

3. Estado del Carrito:
   - Mantén el estado del carrito en un servicio
   - Actualiza el contador del carrito en tiempo real
   - Implementa persistencia local para el carrito

4. Caché:
   - Implementa caché para los productos más visitados
   - Usa BehaviorSubject para compartir el estado entre componentes
   - Implementa una estrategia de recarga de datos

5. Optimizaciones:
   - Implementa paginación en las listas de productos
   - Usa lazy loading para las imágenes
   - Implementa debounce en las búsquedas
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
