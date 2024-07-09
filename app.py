from flask import Flask, request, jsonify, render_template
from flask_mail import Mail, Message
import mysql.connector
from datetime import datetime

app = Flask(__name__)

# Configuración de Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'zerogluten.adm@gmail.com'
app.config['MAIL_PASSWORD'] = 'ZeroGluten.CAC24'

mail = Mail(app)

# Configuración de la base de datos
db_config = {
    'user': 'root',
    'password': '',
    'host': 'localhost',
    'database': 'form_contacto_db'
}

@app.route('/')
def index():
    return render_template('contacto.html')

@app.route('/contacto', methods=['POST'])
def contacto():
    data = request.json
    nombre = data['nombre']
    email = data['email']
    motivo_contacto = data['motivo_contacto']
    serv_utilizado = data['serv_utilizado']
    ubicacion = data['ubicacion']
    mensaje = data['mensaje']
    newsletter = data['newsletter']
    created_at = datetime.now()

    # Conectar a la base de datos
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # Generar el número de consulta
    cursor.execute("SELECT COUNT(*) FROM contactos")
    count = cursor.fetchone()[0]
    numero_consulta = f"A{count:03d}"

    # Insertar los datos en la tabla
    query = """
    INSERT INTO contactos (numero_consulta, nombre, email, motivo_contacto, serv_utilizado, ubicacion, mensaje, newsletter, created_at)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(query, (numero_consulta, nombre, email, motivo_contacto, serv_utilizado, ubicacion, mensaje, newsletter, created_at))
    conn.commit()

    cursor.close()
    conn.close()

    # Configura y envía el correo de confirmación
    msg = Message('Confirmación de recepción', sender='zerogluten.adm@gmail.com', recipients=[email])
    msg.body = f'Gracias por contactarnos, hemos recibido tu mensaje. Tu número de consulta es {numero_consulta}.'
    mail.send(msg)

    return jsonify({'status': 'success', 'numero_consulta': numero_consulta})

# Ruta para obtener todos los registros (Read)
@app.route('/consultas', methods=['GET'])
def get_consultas():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM contactos")
    consultas = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(consultas)

# Ruta para actualizar un registro (Update)
@app.route('/consultas/<numero_consulta>', methods=['PUT'])
def update_consulta(numero_consulta):
    data = request.json
    nombre = data['nombre']
    email = data['email']
    motivo_contacto = data['motivo_contacto']
    serv_utilizado = data['serv_utilizado']
    ubicacion = data['ubicacion']
    mensaje = data['mensaje']
    newsletter = data['newsletter']

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    query = """
    UPDATE contactos
    SET nombre = %s, email = %s, motivo_contacto = %s, serv_utilizado = %s, ubicacion = %s, mensaje = %s, newsletter = %s
    WHERE numero_consulta = %s
    """
    cursor.execute(query, (nombre, email, motivo_contacto, serv_utilizado, ubicacion, mensaje, newsletter, numero_consulta))
    conn.commit()

    cursor.close()
    conn.close()

    return jsonify({'status': 'success'})

# Ruta para borrar un registro (Delete)
@app.route('/consultas/<numero_consulta>', methods=['DELETE'])
def delete_consulta(numero_consulta):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    query = "DELETE FROM contactos WHERE numero_consulta = %s"
    cursor.execute(query, (numero_consulta,))
    conn.commit()

    cursor.close()
    conn.close()

    return jsonify({'status': 'success'})

if __name__ == '__main__':
    app.run(debug=True)