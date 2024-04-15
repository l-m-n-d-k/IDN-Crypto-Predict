from flask import Flask, request, jsonify, render_template, url_for
from openai import OpenAI
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer
import sqlite3
import requests
import csv

# Создание экземпляра приложения Flask
app = Flask(__name__)

# Функция для генерации ответа от модели OpenAI
def generate_text(prompt):
    try:
        # Инициализация клиента API OpenAI
        client = OpenAI(api_key='')
        # Получение ответа от модели
        response = client.chat.completions.create(
            timeout=180,
            model="ft:gpt-3.5-turbo-1106:t1::9DIkapIh",
            messages=[
                {
                    "role": "system",
                    "content": "Your task, as an AI, involves predicting Bitcoin's price for a specified future date, taking into account the current price, date, and the high, open, close values of the current Japanese candlesticks, analyzing these data points to identify trends and the impact of current economic, political events, and global market shifts."
                },
                {"role": "user", "content": prompt}
            ],
        )
        # Запись в базу данных
        db = get_db_connection()
        db.execute('INSERT INTO interactions (user_input, model_response) VALUES (?, ?)', (prompt, response.choices[0].message.content))
        db.commit()
    
        # Обновление CSV файла
        update_csv(prompt, response.choices[0].message.content)
        
        try:
            return float(response.choices[0].message.content)
        except ValueError:
            return response.choices[0].message.content
    except Exception as e:
        return str(e)

# Функция для добавления данных в CSV файл
def update_csv(input_data, output_data, file_path='11.04.2024/model_interactions.csv'):
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

# Функция для получения текущей цены Bitcoin
def get_btc_price():
    try:
        response = requests.get(binance_api_url)
        if response.status_code == 200:
            data = response.json()
            return float(data['price'])
        else:
            return None
    except Exception as e:
        return str(e)

# Функция для получения данных о Bitcoin через API
def get_bitcoin_data_from_api():
    try:
        url = 'https://api.coingecko.com/api/v3/coins/bitcoin'
        response = requests.get(url)
        if response.status_code == 200:
            bitcoin_data = response.json()
            return bitcoin_data
        else:
            print(f"Ошибка при запросе данных о биткойне: {response.status_code}")
            return None
    except Exception as e:
        print(f"Произошла ошибка при получении данных о биткойне: {str(e)}")
        return None

# Маршрут для получения данных о Bitcoin
@app.route('/bitcoin-data', methods=['GET'])
def get_bitcoin_data():
    try:
        url = 'https://api.coingecko.com/api/v3/coins/bitcoin'
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            processed_data = {
                'open': data['market_data']['current_price']['usd'],
                'high': data['market_data']['high_24h']['usd'],
                'low': data['market_data']['low_24h']['usd'],
                'close': data['market_data']['current_price']['usd'],
                'price_change_percentage': data['market_data']['price_change_percentage_24h_in_currency']['usd'],
                'volume': data['market_data']['total_volume']['usd'],
                'tradecount': "Не доступно"
            }
            return jsonify(processed_data)
        else:
            return jsonify({'error': 'Не удалось получить данные от API.'}), 500
    except Exception as e:
        return jsonify({'error': f'Внутренняя ошибка сервера: {str(e)}'}), 500

# Обработка данных о Bitcoin
def process_bitcoin_data(data):
    processed_data = {
        'open': data['market_data']['current_price']['usd'],
        'high': data['market_data']['high_24h']['usd'],
        'low': data['market_data']['low_24h']['usd'],
        'close': data['market_data']['current_price']['usd'], 
        'price_change_percentage': data['market_data']['price_change_percentage_24h'],
        'volume': data['market_data']['total_volume']['usd'],
        'tradecount': data['trade_count']
    }
    return processed_data

# Маршрут для начальной страницы
@app.route('/')
def index():
    return render_template('indexf.html')

# Маршрут для предсказания модели
@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    user_input = data['text']
    model_response = generate_text(user_input)
    response = {
        "prediction": model_response
    }
    return jsonify(response)

# Путь к файлу базы данных
database = 'user_data.db'

# Функция для подключения к базе данных
def get_db_connection():
    conn = sqlite3.connect(database)
    conn.row_factory = sqlite3.Row
    return conn

# Инициализация базы данных
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

# Инициализация базы данных при первом запросе
@app.before_first_request
def initialize():
    init_db()

# Маршрут для регистрации пользователя
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

# Маршрут для входа в систему
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

# Конфигурация почтового сервера
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'  
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'idntechnicalgroup@gmail.com'  
app.config['MAIL_PASSWORD'] = '080607Fv'  
mail = Mail(app)

# Ключи конфигурации для токена подтверждения
app.config['SECRET_KEY'] = '465132'
app.config['SECURITY_PASSWORD_SALT'] = '132465'

# Генерация токена подтверждения почты
def generate_confirmation_token(email):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    return serializer.dumps(email, salt=app.config['SECURITY_PASSWORD_SALT'])

# Отправка почты для подтверждения
def send_confirmation_email(user_email):
    token = generate_confirmation_token(user_email)
    confirm_url = url_for('confirm_email', token=token, _external=True)
    msg = Message("Пожалуйста, подтвердите ваш email", sender='idntechnicalgroup@gmail.com', recipients=[user_email])
    msg.body = f'Для подтверждения вашего email, пожалуйста, перейдите по следующей ссылке: {confirm_url}'
    mail.send(msg)

# Маршрут для страницы взаимодействий
@app.route('/interactions')
def interactions():
    db = get_db_connection()
    interactions = db.execute('SELECT * FROM interactions ORDER BY timestamp DESC').fetchall()
    return render_template('interactions.html', interactions=interactions)

# Маршрут для подтверждения email
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

# Запуск сервера Flask в режиме отладки
if __name__ == '__main__':
    app.run(debug=True)
