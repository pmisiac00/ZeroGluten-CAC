from flask import Flask, render_template, request, redirect, url_for, flash
from models_form import db, Formulario
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/form_contacto_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.urandom(24)

db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('contacto.html')

@app.route('/contacto', methods=['POST'])
def contact():
    numero_consulta = f"A{str(Formulario.query.count() + 1).zfill(3)}"
    nombre = request.form['nombre']
    email = request.form['email']
    motivo_contacto = request.form['motivo_contacto']
    serv_utilizado = request.form['serv_utilizado']
    ubicacion = request.form['ubicacion']
    mensaje = request.form['mensaje']
    newsletter = 'Sí' if 'newsletter' in request.form else 'No'
    
    nuevo_formulario = Formulario(
        numero_consulta=numero_consulta,
        nombre=nombre,
        email=email,
        motivo_contacto=motivo_contacto,
        serv_utilizado=serv_utilizado,
        ubicacion=ubicacion,
        mensaje=mensaje,
        newsletter=newsletter
    )
    db.session.add(nuevo_formulario)
    db.session.commit()
    
    enviar_correo_smtp(email)
    
    flash('Formulario enviado correctamente.')
    return redirect(url_for('index'))

def enviar_correo_smtp(destinatario):
    remitente = "zerogluten.adm@gmail.com"
    servidor_smtp = "smtp.elasticemail.com"
    puerto_smtp = 2525  
    usuario_smtp = "zerogluten.adm@gmail.com"
    password_smtp = "976D518CD6764CBE48D5ABF5C90186874129"

    mensaje = MIMEMultipart()
    mensaje['From'] = remitente
    mensaje['To'] = destinatario
    mensaje['Subject'] = "Recepción de formulario de contacto - ZeroGluten"
    cuerpo = "Hola, \n\nGracias por contactarnos. Hemos recibido tu formulario de contacto y nos pondremos en contacto contigo pronto.\n\nSaludos,\nEquipo ZeroGluten."
    mensaje.attach(MIMEText(cuerpo, 'plain'))

    try:
        with smtplib.SMTP(servidor_smtp, puerto_smtp) as server:
            server.login(usuario_smtp, password_smtp)
            server.sendmail(remitente, destinatario, mensaje.as_string())
            print("Correo enviado correctamente")
    except Exception as e:
        print(f"Error al enviar correo: {e}")

@app.route('/contacto', methods=['GET'])
def obtener_contactos():
    contactos = Formulario.query.all()
    return render_template('contactos.html', contactos=contactos)

@app.route('/contacto/<int:id>', methods=['GET'])
def obtener_contacto(id):
    contacto = Formulario.query.get_or_404(id)
    return render_template('contacto.html', contacto=contacto)

@app.route('/contacto/<int:id>/editar', methods=['GET', 'POST'])
def editar_contacto(id):
    contacto = Formulario.query.get_or_404(id)
    if request.method == 'POST':
        contacto.nombre = request.form['nombre']
        contacto.email = request.form['email']
        contacto.motivo_contacto = request.form['motivo_contacto']
        contacto.serv_utilizado = request.form['serv_utilizado']
        contacto.ubicacion = request.form['ubicacion']
        contacto.mensaje = request.form['mensaje']
        contacto.newsletter = 'Sí' if 'newsletter' in request.form else 'No'
        db.session.commit()
        flash('Contacto actualizado correctamente.')
        return redirect(url_for('obtener_contactos'))
    return render_template('editar_contacto.html', contacto=contacto)

@app.route('/contacto/<int:id>/eliminar', methods=['POST'])
def eliminar_contacto(id):
    contacto = Formulario.query.get_or_404(id)
    db.session.delete(contacto)
    db.session.commit()
    flash('Contacto eliminado correctamente.')
    return redirect(url_for('obtener_contactos'))

if __name__ == '__main__':
    app.run(debug=True)