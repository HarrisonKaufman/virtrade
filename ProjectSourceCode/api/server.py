from flask import Flask, jsonify, request
from api import get_finnhub_quote, get_alpha_vantage_daily, get_finnhub_news, get_finnhub_candle_data, get_twelve_data_daily, get_twelve_data_intraday
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
    try:
        data = get_finnhub_news(symbol)

        if 'error' in data:
            return jsonify({'error': data.get('error')}), 400

        return jsonify({
            'symbol': symbol,
            'articles': data.get('articles', [])
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/health', methods=['GET'])
def health():
    #health check
    return jsonify({'status': 'healthy'}), 200


@app.route('/candle/<symbol>', methods=['GET'])
def candle(symbol):
    try:
        data = get_finnhub_candle_data(symbol)
        return jsonify({'symbol': symbol, 'data': data}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/twelvedata/<symbol>', methods=['GET'])
def twelvedata(symbol):
    try:
        data = get_twelve_data_daily(symbol)
        return jsonify({'symbol': symbol, 'data': data}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/intraday/<symbol>', methods=['GET'])
def intraday(symbol):
    try:
        data = get_twelve_data_intraday(symbol)
        return jsonify({'symbol': symbol, 'data': data}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/holdings/<int:user_id>', methods=['GET'])
def holdings(user_id):
    user = User.load_from_db(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    # Get live prices for all held tickers
    holdings_list = []
    for ticker, quantity in user.holdings.items():
        try:
            quote = get_finnhub_quote(ticker)
            price = quote.get('c', 0)
        except:
            price = 0

        market_value = round(quantity * price, 2)
        holdings_list.append({
            'ticker': ticker,
            'quantity': float(quantity),
            'price': price,
            'market_value': market_value
        })

    return jsonify({'holdings': holdings_list}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)