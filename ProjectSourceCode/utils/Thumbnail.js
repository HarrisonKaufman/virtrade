class Candlestick {
  constructor(time, open, high, low, close, volume = null) {
    this.time = time;
    this.open = open;
    this.high = high;
    this.low = low;
    this.close = close;
    if (volume !== null) {
      this.volume = volume;
    }
  }

  toLightweightCharts() {
    return {
      time: this.time,
      open: this.open,
      high: this.high,
      low: this.low,
      close: this.close,
      ...(this.volume !== null && { volume: this.volume })
    };
  }
}

class StockThumbnail {
  constructor(symbol, candles = [], days = null) {
    this.symbol = symbol;
    this.candles = candles;
    this.days = days || (candles.length > 0 ? candles.length : 0);
  }

  addCandle(candlestick) {
    this.candles.push(candlestick);
  }

  getLastCandles(n) {
    return this.candles.slice(-n).reverse();
  }

  toLightweightCharts() {
    return this.candles.map(candle => candle.toLightweightCharts());
  }

  getStats() {
    if (this.candles.length === 0) {
      return { min: null, max: null, closePrice: null, change: null };
    }

    const closes = this.candles.map(c => c.close);
    const highs = this.candles.map(c => c.high);
    const lows = this.candles.map(c => c.low);

    const firstClose = this.candles[0].close;
    const lastClose = this.candles[this.candles.length - 1].close;

    return {
      min: Math.min(...lows),
      max: Math.max(...highs),
      closePrice: lastClose,
      change: lastClose - firstClose,
      changePercent: ((lastClose - firstClose) / firstClose * 100).toFixed(2)
    };
  }

  static fromAlphaVantage(symbol, avData, days = 7) {
    const thumbnail = new StockThumbnail(symbol);

    if (!avData['Time Series (Daily)']) {
      console.warn(`No time series data for ${symbol}`);
      return thumbnail;
    }

    const timeSeries = avData['Time Series (Daily)'];
    const sorted = Object.entries(timeSeries)
      .sort((a, b) => new Date(a[0]) - new Date(b[0]))
      .slice(-days);

    sorted.forEach(([date, dailyData]) => {
      const candle = new Candlestick(
        date,
        parseFloat(dailyData['1. open']),
        parseFloat(dailyData['2. high']),
        parseFloat(dailyData['3. low']),
        parseFloat(dailyData['4. close']),
        parseInt(dailyData['5. volume'])
      );
      thumbnail.addCandle(candle);
    });

    return thumbnail;
  }
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = { Candlestick, StockThumbnail };
}
