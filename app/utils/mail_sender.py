import smtplib, ssl
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

smtp_address = 'smtp.gmail.com'
smtp_port = 465

email_address = os.getenv("EMAIL_ADDRESS")
email_password = os.getenv("EMAIL_PASSWORD")

def send_order_confirmation(to_email: str, order_number: str, total_amount: float, items: list) -> bool:
    try:
        message = MIMEMultipart()
        message["From"] = email_address
        message["To"] = to_email
        message["Subject"] = f"Confirmación de Orden #{order_number}"

        # Crear el contenido HTML del correo
        items_html = ""
        for item in items:
            items_html += f"""
            <tr>
                <td>{item.product.name}</td>
                <td>{item.quantity}</td>
                <td>${item.unit_price/100:.2f}</td>
                <td>${(item.quantity * item.unit_price)/100:.2f}</td>
            </tr>
            """

        html = f"""
        <html>
            <body style="font-family: Arial, sans-serif;">
                <h2>¡Gracias por tu compra!</h2>
                <p>Tu orden #{order_number} ha sido confirmada.</p>
                
                <h3>Detalles de la orden:</h3>
                <table style="border-collapse: collapse; width: 100%;">
                    <tr style="background-color: #f2f2f2;">
                        <th style="padding: 8px; text-align: left; border: 1px solid #ddd;">Producto</th>
                        <th style="padding: 8px; text-align: left; border: 1px solid #ddd;">Cantidad</th>
                        <th style="padding: 8px; text-align: left; border: 1px solid #ddd;">Precio Unitario</th>
                        <th style="padding: 8px; text-align: left; border: 1px solid #ddd;">Subtotal</th>
                    </tr>
                    {items_html}
                </table>
                
                <h3>Total: ${total_amount/100:.2f}</h3>
                
                <p>Gracias por tu preferencia.</p>
            </body>
        </html>
        """

        message.attach(MIMEText(html, "html"))

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_address, smtp_port, context=context) as server:
            server.login(email_address, email_password)
            server.send_message(message)
            
        return True
    except Exception as e:
        print(f"Error enviando el correo: {str(e)}")
        return False

def send_payment_confirmation(to_email: str, order_id: int, invoice_number: int) -> bool:
    try:
        message = MIMEMultipart()
        message["From"] = email_address
        message["To"] = to_email
        message["Subject"] = f"Confirmación de Pago - Factura #{invoice_number}"

        html = f"""
        <html>
            <body style="font-family: Arial, sans-serif;">
                <h2>¡Pago Confirmado!</h2>
                <p>El pago de tu orden #{order_id} ha sido procesado exitosamente.</p>
                
                <h3>Detalles de la factura:</h3>
                <ul>
                    <li>Número de Factura: {invoice_number}</li>
                    <li>Número de Orden: {order_id}</li>
                </ul>
                
                <p>Puedes descargar tu factura desde tu perfil en nuestra plataforma.</p>
                
                <p>¡Gracias por tu compra!</p>
            </body>
        </html>
        """

        message.attach(MIMEText(html, "html"))

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_address, smtp_port, context=context) as server:
            server.login(email_address, email_password)
            server.send_message(message)
            
        return True
    except Exception as e:
        print(f"Error enviando confirmación de pago: {str(e)}")
        return False

def send_test_email(to_email: str) -> bool:
    try:
        message = MIMEMultipart()
        message["From"] = email_address
        message["To"] = to_email
        message["Subject"] = "Prueba de Email - E-commerce Backend"

        html = """
        <html>
            <body style="font-family: Arial, sans-serif;">
                <h2>¡Prueba de Email Exitosa!</h2>
                <p>Si estás viendo este mensaje, la configuración de email está funcionando correctamente.</p>
                
                <h3>Detalles de la prueba:</h3>
                <ul>
                    <li>Tipo: Email de prueba</li>
                    <li>Estado: Enviado</li>
                    <li>Servidor SMTP: Gmail</li>
                </ul>
                
                <p>Este es un mensaje automático de prueba.</p>
            </body>
        </html>
        """

        message.attach(MIMEText(html, "html"))

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_address, smtp_port, context=context) as server:
            server.login(email_address, email_password)
            server.send_message(message)
            
        return True
    except Exception as e:
        print(f"Error enviando email de prueba: {str(e)}")
        return False
