async function getFinnhubQuote(symbol, requested) {
    try {
        const response = await fetch(`http://localhost:8000/quote/${symbol}`);
        if (!response.ok) {
            console.error('Error response:', response.status);
            return null;
        }
        const data = await response.json();
        return data.data[requested];
    } catch (error) {
        console.error('Error:', error);
    }
}

//AV = alpha vantage
async function getAVData(symbol, date, requested) {
    try {
        const response = await fetch(`http://localhost:8000/daily/${symbol}`);
        if (!response.ok) {
            console.error('Error response:', response.status);
            return null;
        }
        const data = await response.json();
        const timeSeries = data.data['Time Series (Daily)'];

        if (!timeSeries || !timeSeries[date]) {
            console.error(`No data for: ${date}`);
            return null;
        }

        return timeSeries[date][requested];
    } catch (error) {
        console.error('Error:', error);
        return null;
    }
}

//getQuote for buy rooute
async function getQuote(symbol) {
    try {
        const response = await fetch(`http://localhost:8000/quote/${symbol}`);
        if (!response.ok) {
            console.error('Error response:', response.status);
            return null;
        }
        const data = await response.json();
        return data.data[requested];
    } catch (error) {
        console.error('Error:', error);
    }
    //

}

function getChange(symbol) {
    return getFinnhubData(symbol, 'd'); //d = change
}

function getChangePercent(symbol) {
    return getFinnhubData(symbol, 'dp'); //dp = change percent
}

function getHigh(symbol) {
    return getFinnhubData(symbol, 'h'); //h = high
}

function getLow(symbol) {
    return getFinnhubData(symbol, 'l'); //l = low
}

function getOpen(symbol) {
    return getFinnhubData(symbol, 'o'); //o = open
}

function getPrevClose(symbol) {
    return getFinnhubData(symbol, 'pc'); //pc = previous close
}

function getTimestamp(symbol) {
    return getFinnhubData(symbol, 't'); //t = timestamp
}

//alpha vantage wrapper functions
function getAVOpen(symbol, date) {
    return getAVData(symbol, date, '1. open');
}

function getAVHigh(symbol, date) {
    return getAVData(symbol, date, '2. high');
}

function getAVLow(symbol, date) {
    return getAVData(symbol, date, '3. low');
}

function getAVClose(symbol, date) {
    return getAVData(symbol, date, '4. close');
}

function getAVVolume(symbol, date) {
    return getAVData(symbol, date, '5. volume');
}

