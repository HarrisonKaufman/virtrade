async function loadFullChart(symbol = "NASDAQ:AAPL") {
  window.CHART_SYMBOL = symbol;
  const res = await fetch("../../partials/full-chart.hbs");
  const html = await res.text();
  document.getElementById("chart-container").innerHTML = html;
}