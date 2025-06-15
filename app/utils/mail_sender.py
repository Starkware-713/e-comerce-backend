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

def send_payment_confirmation(email: str, order_id: int, amount: float, invoice_number: int) -> bool:
    try:
        message = MIMEMultipart()
        message["From"] = email_address
        message["To"] = email
        message["Subject"] = f"Confirmación de Pago - Factura #{invoice_number}"

        # Crear el contenido HTML del correo
        html = f"""
        <html>
        <body>
            <h2>¡Gracias por tu compra!</h2>
            <p>Tu pago ha sido procesado exitosamente.</p>
            
            <h3>Detalles del pago:</h3>
            <ul>
                <li><strong>Número de orden:</strong> {order_id}</li>
                <li><strong>Número de factura:</strong> {invoice_number}</li>
                <li><strong>Monto pagado:</strong> ${amount:.2f}</li>
            </ul>
            
            <p>Puedes ver los detalles de tu compra en tu perfil de usuario.</p>
            
            <p>Si tienes alguna pregunta, no dudes en contactarnos.</p>
            
            <p>Saludos cordiales,<br>
            El equipo de E-commerce</p>
        </body>
        </html>
        """

        message.attach(MIMEText(html, "html"))

        # Crear conexión segura y enviar el correo
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_address, smtp_port, context=context) as server:
            server.login(email_address, email_password)
            server.sendmail(email_address, email, message.as_string())
        
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

def send_welcome_email(to_email: str, username: str) -> bool:
    try:
        message = MIMEMultipart()
        message["From"] = email_address
        message["To"] = to_email
        message["Subject"] = "¡Bienvenido a nuestra plataforma!"

        html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; margin: 0; padding: 0; background-color: #f5f8fa;">
                <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 40px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <div style="text-align: center; background-color: #1a73e8; padding: 20px; border-radius: 8px; margin-bottom: 30px;">
                        <h1 style="color: white; margin: 0;">¡Bienvenido {username}!</h1>
                    </div>
                    
                    <div style="color: #333; line-height: 1.6;">
                        <p style="font-size: 16px;">Nos alegra mucho tenerte con nosotros. Tu cuenta ha sido creada exitosamente y ahora puedes disfrutar de todos nuestros servicios.</p>
                        
                        <div style="background-color: #e8f0fe; padding: 20px; border-radius: 8px; margin: 20px 0;">
                            <h3 style="color: #1a73e8; margin-top: 0;">¿Qué puedes hacer ahora?</h3>
                            <ul style="list-style-type: none; padding: 0;">
                                <li style="margin-bottom: 10px; padding-left: 24px; position: relative;">
                                    <span style="color: #1a73e8; position: absolute; left: 0;">✓</span>
                                    Explorar nuestro catálogo de productos
                                </li>
                                <li style="margin-bottom: 10px; padding-left: 24px; position: relative;">
                                    <span style="color: #1a73e8; position: absolute; left: 0;">✓</span>
                                    Crear tu primera orden
                                </li>
                                <li style="margin-bottom: 10px; padding-left: 24px; position: relative;">
                                    <span style="color: #1a73e8; position: absolute; left: 0;">✓</span>
                                    Gestionar tu perfil
                                </li>
                            </ul>
                        </div>

                        <p style="font-size: 16px;">Si tienes alguna pregunta o necesitas ayuda, no dudes en contactarnos.</p>
                        
                        <div style="text-align: center; margin-top: 30px;">
                            <p style="color: #666; font-size: 14px;">¡Gracias por elegirnos!</p>
                        </div>
                    </div>
                </div>
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
        print(f"Error enviando email de bienvenida: {str(e)}")
        return False
