from flask import Flask, jsonify, request
from api import get_finnhub_quote, get_alpha_vantage_daily, get_news_for_symbol
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'User'))
from user import User, Stock

app = Flask(__name__)


@app.route('/quote/<symbol>', methods=['GET'])
def quote(symbol):
    # get live quote from finnhub
    try:
        data = get_finnhub_quote(symbol)
        return jsonify({'symbol': symbol, 'data': data}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/daily/<symbol>', methods=['GET'])
def daily(symbol):
    #get historical OHLCV from AV
    try:
        data = get_alpha_vantage_daily(symbol)
        return jsonify({'symbol': symbol, 'data': data}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/buy', methods=['POST'])
def buy():
    data = request.get_json()
    user_id  = data.get('user_id')
    symbol   = data.get('symbol')
    quantity = float(data.get('quantity', 0))

    # Load user from DB using the User class from user.py
    user = User.load_from_db(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    # Get live price from Finnhub
    try:
        quote_data = get_finnhub_quote(symbol)
        price = quote_data.get('c')  # 'c' = current price
        if not price:
            return jsonify({'error': 'Could not fetch stock price'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    stock = Stock(symbol, price)
    result = user.buy(quantity, stock)

    if result == 'Insufficient Balance':
        return jsonify({'error': 'Insufficient Balance'}), 400
    return jsonify({'success': True, 'new_balance': result}), 200


@app.route('/sell', methods=['POST'])
def sell():
    data = request.get_json()
    user_id  = data.get('user_id')
    symbol   = data.get('symbol')
    quantity = float(data.get('quantity', 0))

    # Load user from DB using the User class from user.py
    user = User.load_from_db(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    # Get live price from Finnhub
    try:
        quote_data = get_finnhub_quote(symbol)
        price = quote_data.get('c')
        if not price:
            return jsonify({'error': 'Could not fetch stock price'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    stock = Stock(symbol, price)
    result = user.sell(quantity, stock)

    if result == 'Insufficient Holdings':
        return jsonify({'error': 'Insufficient Holdings'}), 400
    return jsonify({'success': True, 'new_balance': result}), 200


@app.route('/news/<symbol>', methods=['GET'])
def news(symbol):
    #get 3 most recent news stories for a stock symbol
    try:
        data = get_news_for_symbol(symbol)
        if 'error' in data:
            return jsonify({'error': data.get('error')}), 400
        articles = data.get('articles', [])
        return jsonify({'symbol': symbol, 'articles': articles}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/health', methods=['GET'])
def health():
    #health check
    return jsonify({'status': 'healthy'}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)


app = Flask(__name__)


@app.route('/quote/<symbol>', methods=['GET'])
def quote(symbol):
    # get live quote from finnhub
    try:
        data = get_finnhub_quote(symbol)
        return jsonify({'symbol': symbol, 'data': data}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/daily/<symbol>', methods=['GET'])
def daily(symbol):
    #get historical OHLCV from AV
    try:
        data = get_alpha_vantage_daily(symbol)
        return jsonify({'symbol': symbol, 'data': data}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/buy', methods=['POST'])
def buy():
    data = request.get_json()
    user_id  = data.get('user_id')
    symbol   = data.get('symbol')
    quantity = float(data.get('quantity', 0))

    user = User.load_from_db(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    try:
        quote_data = get_finnhub_quote(symbol)
        price = quote_data.get('c')
        if not price:
            return jsonify({'error': 'Could not fetch stock price'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    stock = Stock(symbol, price)
    result = user.buy(quantity, stock)

    if result == 'Insufficient Balance':
        return jsonify({'error': 'Insufficient Balance'}), 400
    return jsonify({'success': True, 'new_balance': result}), 200


@app.route('/sell', methods=['POST'])
def sell():
    data = request.get_json()
    user_id  = data.get('user_id')
    symbol   = data.get('symbol')
    quantity = float(data.get('quantity', 0))

    user = User.load_from_db(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    try:
        quote_data = get_finnhub_quote(symbol)
        price = quote_data.get('c')
        if not price:
            return jsonify({'error': 'Could not fetch stock price'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    stock = Stock(symbol, price)
    result = user.sell(quantity, stock)

    if result == 'Insufficient Holdings':
        return jsonify({'error': 'Insufficient Holdings'}), 400
    return jsonify({'success': True, 'new_balance': result}), 200


@app.route('/news/<symbol>', methods=['GET'])
def news(symbol):
    #get 3 most recent news stories for a stock symbol
    try:
        data = get_news_for_symbol(symbol)
        if 'error' in data:
            return jsonify({'error': data.get('error')}), 400
        articles = data.get('articles', [])
        return jsonify({'symbol': symbol, 'articles': articles}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/health', methods=['GET'])
def health():
    #health check
    return jsonify({'status': 'healthy'}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
