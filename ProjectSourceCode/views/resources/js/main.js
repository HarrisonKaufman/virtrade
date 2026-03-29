async function loadChart(symbol = "NASDAQ:AAPL") {
  window.CHART_SYMBOL = symbol;
  const res = await fetch("../../partials/chart-widget.hbs");
  const html = await res.text();
  document.getElementById("chart-container").innerHTML = html;
}