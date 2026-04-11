from flask import Flask, jsonify, request
from api import get_finnhub_quote, get_alpha_vantage_daily, get_finnhub_candle_data, get_twelve_data_daily, get_twelve_data_intraday

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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
