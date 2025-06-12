# Guía de Implementación de la API E-commerce

## Índice
- [Autenticación](#autenticación)
- [Productos](#productos)
- [Carrito](#carrito)
- [Pedidos](#pedidos)
- [Gestión de Pedidos (Vendedores)](#gestión-de-pedidos-vendedores)

## Configuración TypeScript

Primero, define las interfaces principales que utilizaremos:

```typescript
interface User {
  id: number;
  email: string;
  is_active: boolean;
}

interface Product {
  id: number;
  name: string;
  description: string;
  price: number;
  is_active: boolean;
}

interface CartItem {
  id: number;
  cart_id: number;
  product: Product;
  quantity: number;
}

interface Cart {
  id: number;
  user: User;
  items: CartItem[];
}

interface OrderItem {
  id: number;
  product: Product;
  quantity: number;
  unit_price: number;
}

interface Order {
  id: number;
  order_number: string;
  user: User;
  items: OrderItem[];
  status: string;
  total_amount: number;
  created_at: string;
}

interface OrderHistory {
  id: number;
  order_number: string;
  user: User;
  items: OrderHistoryItem[];
  status: string;
  total_amount: number;
  created_at: string;
  delivered_at?: string;
  cancelled_at?: string;
}
```

## Autenticación

### Registro de Usuario
```typescript
// POST /auth/register
interface RegisterRequest {
  email: string;
  password: string;
  confirm_password: string;
  rol: 'comprador' | 'vendedor';
}

const response = await fetch('http://localhost:8000/auth/register', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify(registerData),
});
```

### Inicio de Sesión
```typescript
// POST /auth/login
interface LoginRequest {
  email: string;
  password: string;
}

interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

const response = await fetch('http://localhost:8000/auth/login', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify(loginData),
});
```

## Productos

### Obtener Productos
```typescript
// GET /products?skip=0&limit=10
const response = await fetch('http://localhost:8000/products?skip=0&limit=10', {
  headers: {
    'Authorization': `Bearer ${token}`,
  },
});
```

### Crear Producto (Vendedor)
```typescript
// POST /products
interface CreateProductRequest {
  name: string;
  description: string;
  price: number;
}

const response = await fetch('http://localhost:8000/products', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json',
  },
  body: JSON.stringify(productData),
});
```

## Carrito

### Crear Carrito
```typescript
// POST /carts
interface CreateCartRequest {
  items: Array<{
    product: Product;
    quantity: number;
  }>;
}

const response = await fetch('http://localhost:8000/carts', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json',
  },
  body: JSON.stringify(cartData),
});
```

### Actualizar Cantidad de Producto
```typescript
// PUT /carts/{cart_id}/items/{item_id}
const response = await fetch(`http://localhost:8000/carts/${cartId}/items/${itemId}`, {
  method: 'PUT',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({ quantity: newQuantity }),
});
```

## Pedidos

### Crear Pedido
```typescript
// POST /orders/create
const response = await fetch('http://localhost:8000/orders/create', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({ cart_id: cartId }),
});
```

### Obtener Mis Pedidos
```typescript
// GET /orders/my-orders?status=pending
const response = await fetch('http://localhost:8000/orders/my-orders?status=pending', {
  headers: {
    'Authorization': `Bearer ${token}`,
  },
});
```

## Gestión de Pedidos (Vendedores)

### Obtener Pedidos Pendientes
```typescript
// GET /orders/management/pending
const response = await fetch('http://localhost:8000/orders/management/pending', {
  headers: {
    'Authorization': `Bearer ${token}`,
  },
});
```

### Marcar Pedido como Entregado
```typescript
// POST /orders/management/{order_id}/deliver
const response = await fetch(`http://localhost:8000/orders/management/${orderId}/deliver`, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
  },
});
```

### Cancelar Pedido
```typescript
// POST /orders/management/{order_id}/cancel
const response = await fetch(`http://localhost:8000/orders/management/${orderId}/cancel`, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
  },
});
```

### Obtener Historial de Pedidos
```typescript
// GET /orders/management/history
const response = await fetch('http://localhost:8000/orders/management/history', {
  headers: {
    'Authorization': `Bearer ${token}`,
  },
});
```

## Notas Importantes

1. Todos los endpoints requieren autenticación excepto registro e inicio de sesión.
2. El token de acceso debe incluirse en el encabezado `Authorization` como `Bearer {token}`.
3. Los endpoints de gestión de pedidos solo están disponibles para usuarios con rol "vendedor" o "admin".
4. Los estados posibles de un pedido son: "pending", "created", "paid", "processing", "shipped", "delivered", "cancelled".
5. Al marcar un pedido como entregado o cancelado, este se mueve automáticamente al historial.