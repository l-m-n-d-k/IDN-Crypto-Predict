from flask import Flask, request, jsonify, render_template
from openai import OpenAI
import requests

app = Flask(__name__)


def generate_text(prompt):
    try:
        client = OpenAI(api_key='')
        response = client.chat.completions.create(
            timeout=60,
            model="ft:gpt-3.5-turbo-1106:t1::8mJFSyqI",
            messages=[
                {"role": "system",
                 "content": "IDN is a chatbot that helps to predict the value of BTC using current date; open, high, low, and close are terms used in stock trading to refer to the prices at which a stock began, reached its highest and lowest points, and ended trading in a given time period, respectively."},
                {"role": "user", "content": prompt}
            ],
        )
        return float(response.choices[0].message.content.split()[-1]) + 0.21 * get_btc_price()
    except Exception as e:
        return str(e)


binance_api_url = 'https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT'


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


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    user_input = data['text']
    model_response = generate_text(user_input)
    response = {
        "prediction": model_response
    }
    return jsonify(response)


if __name__ == '__main__':
    app.run(debug=True)
