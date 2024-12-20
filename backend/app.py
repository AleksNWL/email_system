from flask import Flask, request, render_template, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import smtplib
import imaplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import decode_header
from config import Config

app = Flask(__name__, static_folder='static')
app.config.from_object(Config)
db = SQLAlchemy(app)

EMAIL_SERVERS = {
    'yandex.ru': {
        'imap': 'imap.yandex.ru',
        'smtp': 'smtp.yandex.ru',
        'imap_port': 993,
        'smtp_port': 465,
        'use_starttls': False
    },
    'mail.ru': {
        'imap': 'imap.mail.ru',
        'smtp': 'smtp.mail.ru',
        'imap_port': 993,
        'smtp_port': 465,
        'use_starttls': False
    },
    'gmail.com': {
        'imap': 'imap.gmail.com',
        'smtp': 'smtp.gmail.com',
        'imap_port': 993,
        'smtp_port': 587,
        'use_starttls': True
    },
    'mail.com': {
        'imap': 'imap.mail.com',
        'smtp': 'smtp.mail.com',
        'imap_port': 993,
        'smtp_port': 587,
        'use_starttls': True
    },
    'mail.ru': {
        'imap': 'imap.mail.ru',
        'smtp': 'smtp.mail.ru',
        'imap_port': 993,
        'smtp_port': 587,
        'use_starttls': False
    },
    'outlook.com': {
        'imap': 'outlook.office365.com',
        'smtp': 'smtp.office365.com',
        'imap_port': 993,
        'smtp_port': 587,
        'use_starttls': True
    }
}

class SentEmail(db.Model):
    __tablename__ = 'sent_email'
    id = db.Column(db.Integer, primary_key=True)
    from_email = db.Column(db.String(120), nullable=False)
    to_email = db.Column(db.String(120), nullable=False)
    subject = db.Column(db.String(120), nullable=False)
    message_body = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f'<SentEmail {self.subject}>'

def get_email_server(email_address):
    domain = email_address.split('@')[-1]
    return EMAIL_SERVERS.get(domain)

def decode_mime_words(s):
    if not s:
        return ""
    decoded = decode_header(s)
    return ''.join([str(part[0], part[1] or 'utf-8') if isinstance(part[0], bytes) else part[0] for part in decoded])

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email_address = request.form['email']
        email_password = request.form['password']
        email_server = get_email_server(email_address)

        if not email_server:
            return "Сервер для данного домена не настроен"

        try:
            with imaplib.IMAP4_SSL(email_server['imap'], email_server['imap_port']) as mail:
                mail.login(email_address, email_password)
            
            session['email'] = email_address
            session['password'] = email_password
            session['email_server'] = email_server
            return redirect(url_for('home'))

        except Exception as e:
            return f"Ошибка авторизации: {e}"

    return render_template('login.html')

@app.route('/home')
def home():
    if 'email' not in session or 'password' not in session:
        return redirect(url_for('login'))
    return render_template('index.html', email=session['email'])

@app.route('/send', methods=['GET', 'POST'])
def send():
    if 'email' not in session or 'password' not in session or 'email_server' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        to_email = request.form['to_email']
        subject = request.form['subject']
        message_body = request.form['message']
        email_address = session['email']
        email_password = session['password']
        email_server = session['email_server']

        try:
            msg = MIMEMultipart()
            msg['From'] = email_address
            msg['To'] = to_email
            msg['Subject'] = subject
            msg.attach(MIMEText(message_body, 'plain'))

            if email_server['use_starttls']:
                with smtplib.SMTP(email_server['smtp'], email_server['smtp_port'], timeout=30) as server:
                    server.starttls()
                    server.login(email_address, email_password)
                    server.send_message(msg)
            else:
                with smtplib.SMTP_SSL(email_server['smtp'], email_server['smtp_port'], timeout=30) as server:
                    server.login(email_address, email_password)
                    server.send_message(msg)

            sent_email = SentEmail(from_email=email_address, to_email=to_email, subject=subject, message_body=message_body)
            db.session.add(sent_email)
            db.session.commit()

        except Exception as e:
            return f"Ошибка при отправке письма: {e}"

    return render_template('send.html')


@app.route('/sent')
def sent():
    if 'email' not in session:
        return redirect(url_for('login'))

    emails = SentEmail.query.filter_by(from_email=session['email']).all()
    return render_template('sent.html', emails=emails)

@app.route('/inbox')
def inbox():
    if 'email' not in session:
        return redirect(url_for('login'))

    email_address = session['email']
    email_password = session['password']
    email_server = session['email_server']

    try:
        with imaplib.IMAP4_SSL(email_server['imap'], email_server['imap_port']) as mail:
            mail.login(email_address, email_password)
            mail.select('inbox')

            status, messages = mail.search(None, 'ALL')
            mail_ids = messages[0].split()[-10:]
            emails = []

            for mail_id in mail_ids:
                status, msg_data = mail.fetch(mail_id, '(RFC822)')
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        emails.append({
                            'from': decode_mime_words(msg['from']), 
                            'subject': decode_mime_words(msg['subject']),
                            'date': msg['date'],
                        })

            return render_template('inbox.html', emails=emails)

    except Exception as e:
        return f"Ошибка: {e}"

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
