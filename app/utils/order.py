from datetime import datetime
import uuid

#genera un número de orden único basado en la fecha y un UUID ( Universally Unique Identifier)
def generate_order_number() -> str:
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    unique_id = str(uuid.uuid4().hex)[:8]
    return f"ORDEN-{timestamp}-{unique_id}"

#calcula el total de una orden sumando el precio de cada producto multiplicado por su cantidad
def calculate_order_total(items) -> int:
    total = 0
    for item in items:
        total += item.quantity * item.product.price
    return total

