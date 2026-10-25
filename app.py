from flask import Flask, request, render_template_string, redirect, url_for, Response
import sqlite3
import csv
import io
import urllib.parse

app = Flask(__name__)

# Número de WhatsApp de la Barbería (México: +52)
NUMERO_WHATSAPP = "527716265867"

# 1. Configurar e Inicializar la Base de Datos SQLite
def inicializar_bd():
    conexion = sqlite3.connect("flow_fino.db")
    cursor = conexion.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS citas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente TEXT,
            servicio TEXT,
            horario TEXT,
            estado TEXT DEFAULT 'Pendiente'
        )
    """)
    conexion.commit()
    conexion.close()

# Se inicializa al arrancar la app en Render
inicializar_bd()

# 2. Vista Pública: Formulario de Agendado para Clientes
@app.route("/", methods=["GET", "POST"])
def cliente_agendar():
    if request.method == "POST":
        cliente = request.form.get("cliente", "").strip()
        servicio = request.form.get("servicio", "").strip()
        horario = request.form.get("horario", "").strip()

        if cliente and horario:
            # Guardar en BD como 'Pendiente'
            conexion = sqlite3.connect("flow_fino.db")
            cursor = conexion.cursor()
            cursor.execute(
                "INSERT INTO citas (cliente, servicio, horario, estado) VALUES (?, ?, ?, 'Pendiente')",
                (cliente, servicio, horario)
            )
            conexion.commit()
            conexion.close()

            # Texto preescrito para WhatsApp
            mensaje = f"¡Hola! Me gustaría agendar una cita en *Barbería Flow Fino* 💈✂️\n\n👤 *Nombre:* {cliente}\n💈 *Servicio:* {servicio}\n⏰ *Horario:* {horario}"
            mensaje_encoded = urllib.parse.quote(mensaje)
            whatsapp_url = f"https://api.whatsapp.com/send?phone={NUMERO_WHATSAPP}&text={mensaje_encoded}"

            return redirect(whatsapp_url)

    html_cliente = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Barbería Flow Fino - Agendar Cita</title>
        <style>
            body { background-color: #121212; color: #f5f5f5; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; text-align: center; padding: 20px; margin: 0; }
            .card { background: #1e1e1e; max-width: 420px; margin: 40px auto; padding: 30px; border-radius: 12px; box-shadow: 0 4px 20px rgba(243, 156, 18, 0.2); border: 1px solid #333; }
            h1 { color: #f39c12; margin-bottom: 5px; font-size: 26px; }
            p { color: #aaa; margin-bottom: 25px; font-size: 14px; }
            label { display: block; text-align: left; margin: 10px 0 5px; font-weight: bold; color: #ddd; }
            input, select { width: 100%; padding: 12px; border-radius: 6px; border: 1px solid #444; background: #2a2a2a; color: #fff; box-sizing: border-box; font-size: 15px; }
            input:focus, select:focus { border-color: #f39c12; outline: none; }
            .btn { background: #25d366; color: #fff; border: none; padding: 14px; width: 100%; font-size: 16px; font-weight: bold; border-radius: 6px; cursor: pointer; margin-top: 20px; transition: 0.3s; }
            .btn:hover { background: #1eb954; }
        </style>
    </head>
    <body>
        <div class="card">
            <h1>💈 Flow Fino 💈</h1>
            <p>Reserva tu cita al instante</p>
            <form method="POST">
                <label for="cliente">Tu Nombre:</label>
                <input type="text" id="cliente" name="cliente" placeholder="Ej. Carlos Pérez" required>

                <label for="servicio">Servicio:</label>
                <select id="servicio" name="servicio">
                    <option value="Corte de Cabello">Corte de Cabello</option>
                    <option value="Barba y Perfilado">Barba y Perfilado</option>
                    <option value="Corte + Barba (Combo Flow)">Corte + Barba (Combo Flow)</option>
                    <option value="Tinte / Diseño">Tinte / Diseño</option>
                </select>

                <label for="horario">Día y Hora deseada:</label>
                <input type="text" id="horario" name="horario" placeholder="Ej. Hoy 5:00 PM" required>

                <button type="submit" class="btn">📲 Reservar y Mandar WhatsApp</button>
            </form>
        </div>
    </body>
    </html>
    """
    return render_template_string(html_cliente)


# 3. Vista de Administración para la Tablet: `/admin`
@app.route("/admin")
def panel_tablet():
    conexion = sqlite3.connect("flow_fino.db")
    cursor = conexion.cursor()
    cursor.execute("SELECT id, cliente, servicio, horario, estado FROM citas ORDER BY id DESC")
    citas = cursor.fetchall()
    conexion.close()

    html_admin = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Flow Fino - Panel Tablet</title>
        <style>
            body { background-color: #121212; color: #e0e0e0; font-family: Arial, sans-serif; text-align: center; padding: 20px; }
            h1 { color: #f39c12; margin-bottom: 5px; }
            .header-btns { margin: 20px 0; display: flex; justify-content: center; gap: 15px; }
            table { width: 100%; max-width: 800px; margin: 0 auto; border-collapse: collapse; background: #1e1e1e; border-radius: 8px; overflow: hidden; }
            th, td { padding: 12px; border: 1px solid #333; text-align: center; }
            th { background-color: #2c2c2c; color: #f39c12; }
            .btn-action { padding: 6px 12px; border-radius: 4px; text-decoration: none; font-weight: bold; color: #fff; font-size: 13px; }
            .btn-confirm { background-color: #27ae60; }
            .btn-refresh { background-color: #f39c12; color: #000; padding: 10px 20px; border-radius: 5px; text-decoration: none; font-weight: bold; }
            .btn-excel { background-color: #217346; color: #fff; padding: 10px 20px; border-radius: 5px; text-decoration: none; font-weight: bold; }
            .badge-pendiente { color: #e67e22; font-weight: bold; }
            .badge-confirmada { color: #2ecc71; font-weight: bold; }
        </style>
    </head>
    <body>
        <h1>💈 Barbería Flow Fino - Control de Citas 💈</h1>
        <p>Panel exclusivo de la tablet</p>

        <div class="header-btns">
            <a class="btn-refresh" href="/admin">🔄 Actualizar Citas</a>
            <a class="btn-excel" href="/exportar_excel">📊 Descargar Excel (.csv)</a>
        </div>

        <table>
            <tr>
                <th>ID</th>
                <th>Cliente</th>
                <th>Servicio</th>
                <th>Horario</th>
                <th>Estado</th>
                <th>Acción</th>
            </tr>
            {% for cita in citas %}
            <tr>
                <td>{{ cita[0] }}</td>
                <td>{{ cita[1] }}</td>
                <td>{{ cita[2] }}</td>
                <td>{{ cita[3] }}</td>
                <td>
                    {% if cita[4] == 'Pendiente' %}
                        <span class="badge-pendiente">⏳ Pendiente</span>
                    {% else %}
                        <span class="badge-confirmada">✅ Confirmada</span>
                    {% endif %}
                </td>
                <td>
                    {% if cita[4] == 'Pendiente' %}
                        <a class="btn-action btn-confirm" href="/confirmar/{{ cita[0] }}">Confirmar</a>
                    {% else %}
                        -
                    {% endif %}
                </td>
            </tr>
            {% endfor %}
        </table>
    </body>
    </html>
    """
    return render_template_string(html_admin, citas=citas)


# 4. Confirmar Cita desde la Tablet
@app.route("/confirmar/<int:cita_id>")
def confirmar_cita(cita_id):
    conexion = sqlite3.connect("flow_fino.db")
    cursor = conexion.cursor()
    cursor.execute("UPDATE citas SET estado = 'Confirmada' WHERE id = ?", (cita_id,))
    conexion.commit()
    conexion.close()
    return redirect(url_for("panel_tablet"))


# 5. Exportar la Tabla a Excel (.csv)
@app.route("/exportar_excel")
def exportar_excel():
    conexion = sqlite3.connect("flow_fino.db")
    cursor = conexion.cursor()
    cursor.execute("SELECT id, cliente, servicio, horario, estado FROM citas")
    citas = cursor.fetchall()
    conexion.close()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Cliente", "Servicio", "Horario", "Estado"])

    for row in citas:
        writer.writerow(row)

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=citas_flow_fino.csv"}
    )


if __name__ == "__main__":
    app.run(port=5000, debug=True)
