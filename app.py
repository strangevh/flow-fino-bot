from flask import Flask, request, render_template_string
from twilio.twiml.messaging_response import MessagingResponse
import sqlite3

app = Flask(__name__)

# 1. Configurar la Base de Datos SQLite
def inicializar_bd():
    conexion = sqlite3.connect("flow_fino.db")
    cursor = conexion.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS citas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente TEXT,
            horario TEXT
        )
    """)
    conexion.commit()
    conexion.close()

# 2. Ruta para el Bot de WhatsApp
@app.route("/whatsapp", methods=["POST"])
def whatsapp_bot():
    incoming_msg = request.form.get('Body', '').strip().lower()
    
    resp = MessagingResponse()
    msg = resp.message()

    if "hola" in incoming_msg or "menu" in incoming_msg:
        msg.body("¡Qué tal, bro! Bienvenido a 💈 *Barbería Flow Fino*.\n\nEscribe **AGENDAR** para apartar tu lugar.")
    
    elif "agendar" in incoming_msg:
        msg.body("¡Perfecto! Escribe tu **Nombre** y la **Hora** separados por un guion (Ejemplo: *Carlos - 5:00 PM*) para registrar tu cita.")
    
    elif "-" in incoming_msg:
        datos = incoming_msg.split("-")
        nombre = datos[0].strip()
        horario = datos[1].strip()
        
        # Guardar en la base de datos
        conexion = sqlite3.connect("flow_fino.db")
        cursor = conexion.cursor()
        cursor.execute("INSERT INTO citas (cliente, horario) VALUES (?, ?)", (nombre, horario))
        conexion.commit()
        conexion.close()
        
        msg.body(f"✅ ¡Listo, {nombre}! Tu cita quedó apartada para las {horario}. Te esperamos en Flow Fino ✂️🔥")
    
    else:
        msg.body("No te entendí bien, bro. Escribe **HOLA** para ver las opciones.")

    return str(resp)

# 3. Ruta para el Panel de los Barberos (La que se verá en la Tablet)
@app.route("/")
def panel_tablet():
    conexion = sqlite3.connect("flow_fino.db")
    cursor = conexion.cursor()
    cursor.execute("SELECT cliente, horario FROM citas")
    citas = cursor.fetchall()
    conexion.close()

    # Diseño HTML sencillo y oscuro estilo Y2K/Pro para la tablet
    html_code = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Flow Fino - Panel de Citas</title>
        <style>
            body { background-color: #121212; color: #e0e0e0; font-family: Arial, sans-serif; text-align: center; padding: 20px; }
            h1 { color: #f39c12; }
            table { width: 100%; max-width: 600px; margin: 20px auto; border-collapse: collapse; background: #1e1e1e; }
            th, td { padding: 12px; border: 1px solid #333; }
            th { background-color: #2c2c2c; color: #fff; }
            .btn { background: #f39c12; color: #000; padding: 10px 20px; text-decoration: none; font-weight: bold; border-radius: 5px; display: inline-block; margin-top: 20px;}
        </style>
    </head>
    <body>
        <h1>💈 Barbería Flow Fino - Citas del Día 💈</h1>
        <p>Panel de control para la tablet</p>
        <table>
            <tr>
                <th>Cliente</th>
                <th>Horario</th>
            </tr>
            {% for cita in citas %}
            <tr>
                <td>{{ cita[0] }}</td>
                <td>{{ cita[1] }}</td>
            </tr>
            {% endfor %}
        </table>
        <br>
        <a class="btn" href="/">Actualizar Citas</a>
    </body>
    </html>
    """
    return render_template_string(html_code, citas=citas)

if __name__ == "__main__":
    inicializar_bd()
    app.run(port=5000, debug=True)
