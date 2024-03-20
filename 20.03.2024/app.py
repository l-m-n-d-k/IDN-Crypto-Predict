from flask import Flask, request, jsonify, render_template, url_for
from openai import OpenAI
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer
import sqlite3
import requests
import csv

app = Flask(__name__)

def generate_text(prompt):
    try:
        client = OpenAI(api_key='')
        response = client.chat.completions.create(
            timeout=60,
            model="ft:gpt-3.5-turbo-1106:t1::8mJFSyqI",
            messages=[
                {
                    "role": "system",
                    "content": "IDN является чат-ботом, который помогает предсказывать значение BTC с использованием текущей даты; open, high, low и close - это термины, используемые в торговле акциями для обозначения цен, с которых акция начала торговаться, достигла своих максимальных и минимальных точек и закончила торговаться в заданный период времени, соответственно."
                },
                {"role": "user", "content": prompt}
            ],
        )
        db = get_db_connection()
        db.execute('INSERT INTO interactions (user_input, model_response) VALUES (?, ?)', (prompt, response.choices[0].message.content))
        db.commit()
    
        update_csv(prompt, response.choices[0].message.content)
        
        try:
            return float(response.choices[0].message.content.split()[-1])
        except ValueError:
            return response.choices[0].message.content
    except Exception as e:
        return str(e)

    '''try:
        client = OpenAI(api_key='')
        response2 = client.chat.completions.create(
            timeout=60,
            model="pass", #пока так, сделаем вторую модель 
            messages=[
                {
                    "role": "system",
                    "content": "pass" # system content второй нейросети для bids
                },
                {"role": "user", "content": response}
            ],
        )
        
        try:
            return float(response['choices'][0]['message']['content'])
        except ValueError:
            return response2['choices'][0]['message']['content']
    except Exception as e:
        return str(e)'''

def update_csv(input_data, output_data, file_path='C:\\Users\\andre\\Programming_projects\\Sait_future\\model_interactions.csv'):
    try:
        with open(file_path, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            if file.tell() == 0:
                writer.writerow(['Input', 'Output'])
            writer.writerow([input_data, output_data])
    except Exception as e:
        print(f"Ошибка при попытке записи в файл: {e}")

# URL API Binance для получения текущей цены BTC
binance_api_url = 'https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT'

def get_btc_price():
    try:
        # Запрос к API Binance для получения текущей цены BTC
        response = requests.get(binance_api_url)
        if response.status_code == 200:
            data = response.json()
            # Возврат текущей цены BTC
            return float(data['price'])
        else:
            # Возврат None, если статус ответа не 200
            return None
    except Exception as e:
        # Возврат ошибки, если что-то пошло не так
        return str(e)
    
@app.route('/')
def index():
    # Отображение начальной страницы
    return render_template('indexf.html')


@app.route('/predict', methods=['POST'])
def predict():
    # Получение данных от пользователя через POST запрос
    data = request.get_json()
    user_input = data['text']
    # Генерация ответа модели
    model_response = generate_text(user_input)
    response = {
        "prediction": model_response
    }
    # Возврат ответа в формате JSON
    return jsonify(response)

database = 'user_data.db'

def get_db_connection():
    conn = sqlite3.connect(database)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with app.app_context():
        db = get_db_connection()
        db.execute('''CREATE TABLE IF NOT EXISTS users (
                      id INTEGER PRIMARY KEY AUTOINCREMENT,
                      username TEXT NOT NULL UNIQUE,
                      password TEXT NOT NULL,
                      email TEXT NOT NULL UNIQUE,
                      email_confirmed BOOLEAN NOT NULL DEFAULT FALSE)''')
        
        db.execute('''CREATE TABLE IF NOT EXISTS interactions (
                      id INTEGER PRIMARY KEY AUTOINCREMENT,
                      user_input TEXT NOT NULL,
                      model_response TEXT NOT NULL,
                      timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
        
        db.commit()



@app.before_first_request
def initialize():
    init_db()

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data['username']
    password = data['password']
    email = data['email']

    db = get_db_connection()
    user_by_username = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    user_by_email = db.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()

    if user_by_username:
        return jsonify({"message": "This username is already taken."}), 400

    if user_by_email:
        return jsonify({"message": "This email is already registered."}), 400

    password_hash = generate_password_hash(password)

    db.execute('INSERT INTO users (username, password, email) VALUES (?, ?, ?)', (username, password_hash, email))
    db.commit()

    send_confirmation_email(email)

    return jsonify({"message": "User registered successfully!"}), 201


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']
    
    db = get_db_connection()
    user = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    
    if user and check_password_hash(user['password'], password):
        if not user['email_confirmed']:
            return jsonify({"success": False, "message": "Email not confirmed."}), 401
        return jsonify({"success": True}), 200
    else:
        return jsonify({"success": False, "message": "Invalid credentials."}), 401


app.config['MAIL_SERVER'] = 'smtp.googlemail.com'  
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'idntechnicalgroup@gmail.com'  
app.config['MAIL_PASSWORD'] = '080607Fv'  
mail = Mail(app)

app.config['SECRET_KEY'] = '465132'
app.config['SECURITY_PASSWORD_SALT'] = '132465'

def generate_confirmation_token(email):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    return serializer.dumps(email, salt=app.config['SECURITY_PASSWORD_SALT'])

def send_confirmation_email(user_email):
    token = generate_confirmation_token(user_email)
    confirm_url = url_for('confirm_email', token=token, _external=True)
    msg = Message("Пожалуйста, подтвердите ваш email", sender='idntechnicalgroup@gmail.com', recipients=[user_email])
    msg.body = f'Для подтверждения вашего email, пожалуйста, перейдите по следующей ссылке: {confirm_url}'
    mail.send(msg)

@app.route('/interactions')
def interactions():
    db = get_db_connection()
    interactions = db.execute('SELECT * FROM interactions ORDER BY timestamp DESC').fetchall()
    return render_template('interactions.html', interactions=interactions)

@app.route('/confirm/<token>')
def confirm_email(token):
    try:
        serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
        email = serializer.loads(token, salt=app.config['SECURITY_PASSWORD_SALT'], max_age=3600)
        db = get_db_connection()
        db.execute('UPDATE users SET email_confirmed = TRUE WHERE email = ?', (email,))
        db.commit()
        return 'Ваш email был успешно подтвержден!'
    except:
        return 'Ссылка для подтверждения недействительна или истек срок ее действия.'

if __name__ == '__main__':
    # Запуск сервера Flask в режиме отладки
    app.run(debug=True)