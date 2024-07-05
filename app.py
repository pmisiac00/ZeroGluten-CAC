from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL
from config import Config
from send_email import send_email

app = Flask(__name__)
app.config.from_object(Config)
mysql = MySQL(app)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO contacts (name, email, message) VALUES (%s, %s, %s)", (name, email, message))
        mysql.connection.commit()
        cur.close()

        # Enviar correo de confirmación
        send_email(email, 'Contact Form Submission', 'Thank you for contacting us. We have received your message.')

        flash('Contact form submitted successfully!', 'success')
        return redirect(url_for('contact'))

    return render_template('contact.html')



if __name__ == '__main__':
    app.run(debug=True)

