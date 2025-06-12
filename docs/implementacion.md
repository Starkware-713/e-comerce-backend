# Guía de Implementación con Angular para la API E-commerce

## Índice
- [Configuración Inicial](#configuración-inicial)
- [Servicios](#servicios)
- [Guards](#guards)
- [Interceptores](#interceptores)
- [Interfaces](#interfaces)
- [Componentes](#componentes)
- [Módulos](#módulos)

## Configuración Inicial

### 1. Instalar las dependencias requeridas

```bash
npm install  @auth0/angular-jwt

Primero, define las interfaces principales que utilizaremos:

```typescript
// src/app/core/interfaces/index.ts

export interface User {
  id: number;
  email: string;
  name: string;
  lastname: string;
  is_active: boolean;
  rol: 'comprador' | 'vendedor' | 'admin';
}

export interface Product {
  id: number;
  name: string;
  description: string;
  price: number;
  is_active: boolean;
  stock: number;
  category: string;
  seller_id: number;
}

export interface CartItem {
  id: number;
  cart_id: number;
  product: Product;
  quantity: number;
  subtotal: number;
}

export interface Cart {
  id: number;
  user: User;
  items: CartItem[];
  total: number;
  status: 'active' | 'checked_out';
}

export interface OrderItem {
  id: number;
  product: Product;
  quantity: number;
  unit_price: number;
  subtotal: number;
}

export interface Order {
  id: number;
  order_number: string;
  user: User;
  items: OrderItem[];
  status: OrderStatus;
  total_amount: number;
  created_at: string;
  payment_date?: string;
}

export type OrderStatus = 'pending' | 'paid' | 'processing' | 'shipped' | 'delivered' | 'cancelled';

export interface Payment {
  id: number;
  order_id: number;
  amount: number;
  payment_method: PaymentMethod;
  status: PaymentStatus;
  transaction_id: string;
  payment_date: string;
  invoice_number?: number;
}

export type PaymentMethod = 'credit_card' | 'debit_card' | 'transfer' | 'mercado_pago';
export type PaymentStatus = 'pending' | 'paid' | 'failed';

export interface Sale {
  id: number;
  order_id: number;
  invoice_number: number;
  total_amount: number;
  tax_amount: number;
  payment_id: number;
  status: PaymentStatus;
  created_at: string;
}
```

## Servicios

### AuthService
```typescript
// src/app/core/services/auth.service.ts
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable } from 'rxjs';
import { tap } from 'rxjs/operators';
import { JwtHelperService } from '@auth0/angular-jwt';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private apiUrl = 'http://localhost:8000/auth';
  private userSubject = new BehaviorSubject<User | null>(null);
  public user$ = this.userSubject.asObservable();

  constructor(
    private http: HttpClient,
    private jwtHelper: JwtHelperService
  ) {
    this.checkToken();
  }

  register(data: RegisterRequest): Observable<TokenResponse> {
    return this.http.post<TokenResponse>(`${this.apiUrl}/register`, data)
      .pipe(tap(response => this.handleAuthentication(response)));
  }

  login(data: LoginRequest): Observable<TokenResponse> {
    return this.http.post<TokenResponse>(`${this.apiUrl}/login`, data)
      .pipe(tap(response => this.handleAuthentication(response)));
  }

  refreshToken(): Observable<TokenResponse> {
    const refreshToken = localStorage.getItem('refresh_token');
    return this.http.post<TokenResponse>(`${this.apiUrl}/refresh`, { refresh_token: refreshToken })
      .pipe(tap(response => this.handleAuthentication(response)));
  }

  logout(): void {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    this.userSubject.next(null);
  }

  private handleAuthentication(response: TokenResponse): void {
    localStorage.setItem('access_token', response.access_token);
    localStorage.setItem('refresh_token', response.refresh_token);
    const decodedToken = this.jwtHelper.decodeToken(response.access_token);
    this.userSubject.next(decodedToken);
  }

  private checkToken(): void {
    const token = localStorage.getItem('access_token');
    if (token && !this.jwtHelper.isTokenExpired(token)) {
      const decodedToken = this.jwtHelper.decodeToken(token);
      this.userSubject.next(decodedToken);
    }
  }

  isAuthenticated(): boolean {
    const token = localStorage.getItem('access_token');
    return token ? !this.jwtHelper.isTokenExpired(token) : false;
  }

  getRole(): string | null {
    return this.userSubject.value?.rol || null;
  }
}
```

### ProductService
```typescript
// src/app/core/services/product.service.ts
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Product } from '../interfaces';

@Injectable({
  providedIn: 'root'
})
export class ProductService {
  private apiUrl = 'http://localhost:8000/products';

  constructor(private http: HttpClient) {}

  getProducts(skip: number = 0, limit: number = 10): Observable<Product[]> {
    return this.http.get<Product[]>(`${this.apiUrl}?skip=${skip}&limit=${limit}`);
  }

  getProduct(id: number): Observable<Product> {
    return this.http.get<Product>(`${this.apiUrl}/${id}`);
  }

  createProduct(product: Partial<Product>): Observable<Product> {
    return this.http.post<Product>(this.apiUrl, product);
  }

  updateProduct(id: number, product: Partial<Product>): Observable<Product> {
    return this.http.put<Product>(`${this.apiUrl}/${id}`, product);
  }

  deleteProduct(id: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/${id}`);
  }
}

### CartService
```typescript
// src/app/core/services/cart.service.ts
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable } from 'rxjs';
import { tap } from 'rxjs/operators';
import { Cart, CartItem } from '../interfaces';

@Injectable({
  providedIn: 'root'
})
export class CartService {
  private apiUrl = 'http://localhost:8000/carts';
  private cartSubject = new BehaviorSubject<Cart | null>(null);
  public cart$ = this.cartSubject.asObservable();

  constructor(private http: HttpClient) {
    this.loadCart();
  }

  private loadCart(): void {
    this.http.get<Cart>(this.apiUrl)
      .subscribe(cart => this.cartSubject.next(cart));
  }

  addToCart(productId: number, quantity: number): Observable<Cart> {
    return this.http.post<Cart>(`${this.apiUrl}/items`, { product_id: productId, quantity })
      .pipe(tap(cart => this.cartSubject.next(cart)));
  }

  updateQuantity(itemId: number, quantity: number): Observable<Cart> {
    return this.http.put<Cart>(`${this.apiUrl}/items/${itemId}`, { quantity })
      .pipe(tap(cart => this.cartSubject.next(cart)));
  }

  removeFromCart(itemId: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/items/${itemId}`)
      .pipe(tap(() => this.loadCart()));
  }

  checkout(): Observable<Cart> {
    return this.http.post<Cart>(`${this.apiUrl}/checkout`, {})
      .pipe(tap(() => this.cartSubject.next(null)));
  }

  getCartTotal(): number {
    return this.cartSubject.value?.total || 0;
  }

  getItemCount(): number {
    return this.cartSubject.value?.items.length || 0;
  }
}
```

### OrderService
```typescript
// src/app/core/services/order.service.ts
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Order, OrderStatus } from '../interfaces';

@Injectable({
  providedIn: 'root'
})
export class OrderService {
  private apiUrl = 'http://localhost:8000/orders';

  constructor(private http: HttpClient) {}

  createOrder(cartId: number): Observable<Order> {
    return this.http.post<Order>(`${this.apiUrl}/create`, { cart_id: cartId });
  }

  getMyOrders(status?: OrderStatus): Observable<Order[]> {
    const params = status ? `?status=${status}` : '';
    return this.http.get<Order[]>(`${this.apiUrl}/my-orders${params}`);
  }

  getOrder(id: number): Observable<Order> {
    return this.http.get<Order>(`${this.apiUrl}/${id}`);
  }

  // Métodos para vendedores
  getPendingOrders(): Observable<Order[]> {
    return this.http.get<Order[]>(`${this.apiUrl}/management/pending`);
  }

  markAsDelivered(orderId: number): Observable<Order> {
    return this.http.post<Order>(`${this.apiUrl}/management/${orderId}/deliver`, {});
  }

  cancelOrder(orderId: number): Observable<Order> {
    return this.http.post<Order>(`${this.apiUrl}/management/${orderId}/cancel`, {});
  }
}

### PaymentService
```typescript
// src/app/core/services/payment.service.ts
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Payment, PaymentMethod } from '../interfaces';

@Injectable({
  providedIn: 'root'
})
export class PaymentService {
  private apiUrl = 'http://localhost:8000/payment';

  constructor(private http: HttpClient) {}

  processPayment(orderId: number, paymentMethod: PaymentMethod): Observable<Payment> {
    return this.http.post<Payment>(`${this.apiUrl}/process`, {
      order_id: orderId,
      payment_method: paymentMethod
    });
  }

  getPaymentDetails(paymentId: number): Observable<Payment> {
    return this.http.get<Payment>(`${this.apiUrl}/${paymentId}`);
  }
}

## Interceptores

### TokenInterceptor
```typescript
// src/app/core/interceptors/token.interceptor.ts
import { Injectable } from '@angular/core';
import { HttpInterceptor, HttpRequest, HttpHandler, HttpEvent, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError, BehaviorSubject } from 'rxjs';
import { catchError, filter, take, switchMap } from 'rxjs/operators';
import { AuthService } from '../services/auth.service';

@Injectable()
export class TokenInterceptor implements HttpInterceptor {
  private isRefreshing = false;
  private refreshTokenSubject: BehaviorSubject<any> = new BehaviorSubject<any>(null);

  constructor(private authService: AuthService) {}

  intercept(request: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    const token = localStorage.getItem('access_token');
    
    if (token) {
      request = this.addToken(request, token);
    }

    return next.handle(request).pipe(
      catchError(error => {
        if (error instanceof HttpErrorResponse && error.status === 401) {
          return this.handle401Error(request, next);
        }
        return throwError(error);
      })
    );
  }

  private addToken(request: HttpRequest<any>, token: string): HttpRequest<any> {
    return request.clone({
      setHeaders: {
        Authorization: `Bearer ${token}`
      }
    });
  }

  private handle401Error(request: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    if (!this.isRefreshing) {
      this.isRefreshing = true;
      this.refreshTokenSubject.next(null);

      return this.authService.refreshToken().pipe(
        switchMap((token) => {
          this.isRefreshing = false;
          this.refreshTokenSubject.next(token.access_token);
          return next.handle(this.addToken(request, token.access_token));
        }),
        catchError((error) => {
          this.isRefreshing = false;
          this.authService.logout();
          return throwError(error);
        })
      );
    }

    return this.refreshTokenSubject.pipe(
      filter(token => token != null),
      take(1),
      switchMap(token => next.handle(this.addToken(request, token)))
    );
  }
}
```

## Guards

### AuthGuard
```typescript
// src/app/core/guards/auth.guard.ts
import { Injectable } from '@angular/core';
import { Router, CanActivate } from '@angular/router';
import { AuthService } from '../services/auth.service';

@Injectable({
  providedIn: 'root'
})
export class AuthGuard implements CanActivate {
  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  canActivate(): boolean {
    if (this.authService.isAuthenticated()) {
      return true;
    }
    
    this.router.navigate(['/auth/login']);
    return false;
  }
}

### RoleGuard
```typescript
// src/app/core/guards/role.guard.ts
import { Injectable } from '@angular/core';
import { Router, CanActivate, ActivatedRouteSnapshot } from '@angular/router';
import { AuthService } from '../services/auth.service';

@Injectable({
  providedIn: 'root'
})
export class RoleGuard implements CanActivate {
  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  canActivate(route: ActivatedRouteSnapshot): boolean {
    const expectedRole = route.data['role'];
    const userRole = this.authService.getRole();

    if (!this.authService.isAuthenticated() || userRole !== expectedRole) {
      this.router.navigate(['/auth/login']);
      return false;
    }
    
    return true;
  }
}

## Componentes Principales

### LoginComponent
```typescript
// src/app/features/auth/components/login/login.component.ts
import { Component } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '@core/services/auth.service';

@Component({
  selector: 'app-login',
  template: `
    <mat-card>
      <mat-card-header>
        <mat-card-title>Iniciar Sesión</mat-card-title>
      </mat-card-header>
      
      <mat-card-content>
        <form [formGroup]="loginForm" (ngSubmit)="onSubmit()">
          <mat-form-field>
            <input matInput placeholder="Email" formControlName="email" type="email">
            <mat-error *ngIf="loginForm.get('email')?.hasError('required')">
              El email es requerido
            </mat-error>
          </mat-form-field>

          <mat-form-field>
            <input matInput placeholder="Contraseña" formControlName="password" type="password">
            <mat-error *ngIf="loginForm.get('password')?.hasError('required')">
              La contraseña es requerida
            </mat-error>
          </mat-form-field>

          <button mat-raised-button color="primary" type="submit" [disabled]="loginForm.invalid">
            Iniciar Sesión
          </button>
        </form>
      </mat-card-content>
    </mat-card>
  `
})
export class LoginComponent {
  loginForm: FormGroup;

  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private router: Router
  ) {
    this.loginForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required]]
    });
  }

  onSubmit(): void {
    if (this.loginForm.valid) {
      this.authService.login(this.loginForm.value).subscribe(
        () => this.router.navigate(['/dashboard']),
        error => console.error('Error al iniciar sesión:', error)
      );
    }
  }
}
```

### ProductListComponent
```typescript
// src/app/features/products/components/product-list/product-list.component.ts
import { Component, OnInit } from '@angular/core';
import { ProductService } from '@core/services/product.service';
import { CartService } from '@core/services/cart.service';
import { Product } from '@core/interfaces';

@Component({
  selector: 'app-product-list',
  template: `
    <div class="products-grid">
      <mat-card *ngFor="let product of products">
        <mat-card-header>
          <mat-card-title>{{ product.name }}</mat-card-title>
        </mat-card-header>
        
        <mat-card-content>
          <p>{{ product.description }}</p>
          <p class="price">{{ product.price | currency }}</p>
        </mat-card-content>
        
        <mat-card-actions>
          <button mat-button (click)="addToCart(product)">
            <mat-icon>add_shopping_cart</mat-icon>
            Agregar al Carrito
          </button>
        </mat-card-actions>
      </mat-card>
    </div>
  `,
  styles: [`
    .products-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
      gap: 1rem;
      padding: 1rem;
    }
    .price {
      font-size: 1.2em;
      color: #1976d2;
      font-weight: bold;
    }
  `]
})
export class ProductListComponent implements OnInit {
  products: Product[] = [];

  constructor(
    private productService: ProductService,
    private cartService: CartService
  ) {}

  ngOnInit(): void {
    this.loadProducts();
  }

  loadProducts(skip: number = 0): void {
    this.productService.getProducts(skip)
      .subscribe(
        products => this.products = products,
        error => console.error('Error al cargar productos:', error)
      );
  }

  addToCart(product: Product): void {
    this.cartService.addToCart(product.id, 1)
      .subscribe(
        () => console.log('Producto agregado al carrito'),
        error => console.error('Error al agregar al carrito:', error)
      );
  }
}

### CartComponent
```typescript
// src/app/features/cart/components/cart/cart.component.ts
import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { CartService } from '@core/services/cart.service';
import { Cart, CartItem } from '@core/interfaces';

@Component({
  selector: 'app-cart',
  template: `
    <mat-card *ngIf="cart">
      <mat-card-header>
        <mat-card-title>Mi Carrito</mat-card-title>
      </mat-card-header>
      
      <mat-card-content>
        <mat-list>
          <mat-list-item *ngFor="let item of cart.items">
            <h3 matLine>{{ item.product.name }}</h3>
            <p matLine>
              {{ item.product.price | currency }} x {{ item.quantity }}
              = {{ item.subtotal | currency }}
            </p>
            <div class="item-actions">
              <button mat-icon-button (click)="updateQuantity(item, item.quantity - 1)">
                <mat-icon>remove</mat-icon>
              </button>
              <span>{{ item.quantity }}</span>
              <button mat-icon-button (click)="updateQuantity(item, item.quantity + 1)">
                <mat-icon>add</mat-icon>
              </button>
              <button mat-icon-button color="warn" (click)="removeItem(item)">
                <mat-icon>delete</mat-icon>
              </button>
            </div>
          </mat-list-item>
        </mat-list>
        
        <div class="cart-total">
          <h2>Total: {{ cart.total | currency }}</h2>
        </div>
      </mat-card-content>
      
      <mat-card-actions>
        <button mat-raised-button color="primary" (click)="checkout()" 
                [disabled]="!cart.items.length">
          Proceder al Pago
        </button>
      </mat-card-actions>
    </mat-card>
  `,
  styles: [`
    .item-actions {
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }
    .cart-total {
      margin-top: 1rem;
      text-align: right;
    }
  `]
})
export class CartComponent implements OnInit {
  cart: Cart | null = null;

  constructor(
    private cartService: CartService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.cartService.cart$.subscribe(
      cart => this.cart = cart
    );
  }

  updateQuantity(item: CartItem, quantity: number): void {
    if (quantity > 0) {
      this.cartService.updateQuantity(item.id, quantity)
        .subscribe(
          null,
          error => console.error('Error al actualizar cantidad:', error)
        );
    }
  }

  removeItem(item: CartItem): void {
    this.cartService.removeFromCart(item.id)
      .subscribe(
        null,
        error => console.error('Error al eliminar item:', error)
      );
  }

  checkout(): void {
    this.cartService.checkout()
      .subscribe(
        () => this.router.navigate(['/checkout']),
        error => console.error('Error al procesar el carrito:', error)
      );
  }
}
```

### CheckoutComponent
```typescript
// src/app/features/checkout/components/checkout/checkout.component.ts
import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { PaymentService } from '@core/services/payment.service';
import { OrderService } from '@core/services/order.service';
import { PaymentMethod, Order } from '@core/interfaces';

@Component({
  selector: 'app-checkout',
  template: `
    <mat-stepper linear #stepper>
      <!-- Paso 1: Método de Pago -->
      <mat-step [stepControl]="paymentForm">
        <form [formGroup]="paymentForm">
          <ng-template matStepLabel>Método de Pago</ng-template>
          
          <mat-radio-group formControlName="paymentMethod">
            <mat-radio-button value="credit_card">Tarjeta de Crédito</mat-radio-button>
            <mat-radio-button value="debit_card">Tarjeta de Débito</mat-radio-button>
            <mat-radio-button value="mercado_pago">Mercado Pago</mat-radio-button>
            <mat-radio-button value="transfer">Transferencia Bancaria</mat-radio-button>
          </mat-radio-group>
          
          <div>
            <button mat-button matStepperNext>Siguiente</button>
          </div>
        </form>
      </mat-step>

      <!-- Paso 2: Confirmación -->
      <mat-step>
        <ng-template matStepLabel>Confirmar Pago</ng-template>
        
        <div *ngIf="order">
          <h3>Resumen del Pedido</h3>
          <p>Total a Pagar: {{ order.total_amount | currency }}</p>
          <p>Método de Pago: {{ getPaymentMethodLabel() }}</p>
          
          <button mat-raised-button color="primary" 
                  (click)="processPayment()" 
                  [disabled]="processing">
            {{ processing ? 'Procesando...' : 'Confirmar Pago' }}
          </button>
          <button mat-button (click)="stepper.previous()">Atrás</button>
        </div>
      </mat-step>
    </mat-stepper>
  `
})
export class CheckoutComponent implements OnInit {
  paymentForm: FormGroup;
  order: Order | null = null;
  processing = false;

  constructor(
    private fb: FormBuilder,
    private paymentService: PaymentService,
    private orderService: OrderService,
    private router: Router
  ) {
    this.paymentForm = this.fb.group({
      paymentMethod: ['', Validators.required]
    });
  }

  ngOnInit(): void {
    // Obtener la orden actual
    this.orderService.getOrder(/* orderId */).subscribe(
      order => this.order = order
    );
  }

  getPaymentMethodLabel(): string {
    const methods = {
      credit_card: 'Tarjeta de Crédito',
      debit_card: 'Tarjeta de Débito',
      mercado_pago: 'Mercado Pago',
      transfer: 'Transferencia Bancaria'
    };
    return methods[this.paymentForm.get('paymentMethod')?.value] || '';
  }

  processPayment(): void {
    if (this.paymentForm.valid && this.order) {
      this.processing = true;
      this.paymentService.processPayment(
        this.order.id,
        this.paymentForm.get('paymentMethod')?.value
      ).subscribe(
        payment => {
          this.router.navigate(['/payment-success'], {
            queryParams: { invoice: payment.invoice_number }
          });
        },
        error => {
          console.error('Error en el pago:', error);
          this.processing = false;
        }
      );
    }
  }
}

## Módulos

### AppModule
```typescript
// src/app/app.module.ts
import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { HttpClientModule, HTTP_INTERCEPTORS } from '@angular/common/http';
import { JwtModule } from '@auth0/angular-jwt';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { TokenInterceptor } from '@core/interceptors/token.interceptor';

@NgModule({
  declarations: [AppComponent],
  imports: [
    BrowserModule,
    BrowserAnimationsModule,
    HttpClientModule,
    AppRoutingModule,
    JwtModule.forRoot({
      config: {
        tokenGetter: () => localStorage.getItem('access_token'),
        allowedDomains: ['localhost:8000']
      }
    })
  ],
  providers: [
    {
      provide: HTTP_INTERCEPTORS,
      useClass: TokenInterceptor,
      multi: true
    }
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }
```

### AppRoutingModule
```typescript
// src/app/app-routing.module.ts
import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { AuthGuard } from '@core/guards/auth.guard';
import { RoleGuard } from '@core/guards/role.guard';

const routes: Routes = [
  {
    path: '',
    redirectTo: 'products',
    pathMatch: 'full'
  },
  {
    path: 'auth',
    loadChildren: () => import('./features/auth/auth.module').then(m => m.AuthModule)
  },
  {
    path: 'products',
    loadChildren: () => import('./features/products/products.module').then(m => m.ProductsModule)
  },
  {
    path: 'cart',
    loadChildren: () => import('./features/cart/cart.module').then(m => m.CartModule),
    canActivate: [AuthGuard]
  },
  {
    path: 'checkout',
    loadChildren: () => import('./features/checkout/checkout.module').then(m => m.CheckoutModule),
    canActivate: [AuthGuard]
  },
  {
    path: 'orders',
    loadChildren: () => import('./features/orders/orders.module').then(m => m.OrdersModule),
    canActivate: [AuthGuard]
  },
  {
    path: 'seller',
    loadChildren: () => import('./features/seller/seller.module').then(m => m.SellerModule),
    canActivate: [RoleGuard],
    data: { role: 'vendedor' }
  }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }

### Feature Modules

#### AuthModule
```typescript
// src/app/features/auth/auth.module.ts
import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { MaterialModule } from '@shared/material.module';
import { LoginComponent } from './components/login/login.component';
import { RegisterComponent } from './components/register/register.component';

const routes = [
  { path: 'login', component: LoginComponent },
  { path: 'register', component: RegisterComponent }
];

@NgModule({
  declarations: [LoginComponent, RegisterComponent],
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MaterialModule,
    RouterModule.forChild(routes)
  ]
})
export class AuthModule { }

### MaterialModule
```typescript
// src/app/shared/material.module.ts
import { NgModule } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatListModule } from '@angular/material/list';
import { MatRadioModule } from '@angular/material/radio';
import { MatStepperModule } from '@angular/material/stepper';
import { MatToolbarModule } from '@angular/material/toolbar';

@NgModule({
  exports: [
    MatButtonModule,
    MatCardModule,
    MatIconModule,
    MatInputModule,
    MatListModule,
    MatRadioModule,
    MatStepperModule,
    MatToolbarModule
  ]
})
export class MaterialModule { }

## Instrucciones de Implementación

1. Configuración del Proyecto:
```bash
# Crear nuevo proyecto Angular
ng new e-commerce-frontend --routing --style=scss

# Instalar dependencias
cd e-commerce-frontend
npm install @angular/material @auth0/angular-jwt
```

2. Estructura de Carpetas Recomendada:
```
src/
├── app/
│   ├── core/           # Servicios, guardias, interceptores
│   ├── features/       # Módulos de características
│   ├── shared/         # Componentes y módulos compartidos
│   └── app.module.ts
├── assets/
└── environments/
```

3. Variables de Entorno:
```typescript
// src/environments/environment.ts
export const environment = {
  production: false,
  apiUrl: 'http://localhost:8000'
};
```

4. Configuración de Material:
```typescript
// src/styles.scss
@import '@angular/material/prebuilt-themes/indigo-pink.css';

// En angular.json, agregar:
"styles": [
  "src/styles.scss"
]
```

5. Iniciar el Desarrollo:
```bash
ng serve
```

## Buenas Prácticas

1. **Manejo de Estado**
   - Usar BehaviorSubject para estado local
   - Considerar implementar NgRx para aplicaciones más grandes

2. **Seguridad**
   - Implementar interceptor para tokens
   - Usar guardias para proteger rutas
   - Validar roles y permisos

3. **Rendimiento**
   - Lazy loading de módulos
   - Implementar virtual scrolling para listas largas
   - Usar OnPush change detection strategy

4. **Estructura**
   - Módulos por característica
   - Servicios en el módulo core
   - Componentes compartidos en shared module
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