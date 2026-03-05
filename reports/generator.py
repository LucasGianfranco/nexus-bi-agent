import sqlite3
import os
import json
import pandas as pd # type: ignore

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed', 'nexus_bi.db')
OUTPUT  = os.path.join(os.path.dirname(__file__), '..', 'reports', 'dashboard.html')

def load_data():
    conn = sqlite3.connect(DB_PATH)
    revenue_daily = pd.read_sql('SELECT * FROM revenue_daily ORDER BY order_date', conn)
    top_products  = pd.read_sql('SELECT * FROM top_products ORDER BY revenue DESC', conn)
    revenue_state = pd.read_sql('SELECT * FROM revenue_state ORDER BY revenue DESC LIMIT 10', conn)
    kpis          = pd.read_sql('SELECT * FROM kpis', conn).iloc[0].to_dict()
    conn.close()
    return revenue_daily, top_products, revenue_state, kpis

def generate_dashboard(narrative=""):
    print("📊 Generando dashboard...")
    revenue_daily, top_products, revenue_state, kpis = load_data()

    rev_dates    = revenue_daily['order_date'].tolist()
    rev_values   = revenue_daily['revenue'].round(2).tolist()
    prod_names   = top_products['product_category_name_english'].tolist()
    prod_values  = top_products['revenue'].round(2).tolist()
    state_names  = revenue_state['customer_state'].tolist()
    state_values = revenue_state['revenue'].round(2).tolist()

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>NEXUS BI — Reporte Ejecutivo</title>
<script src="https://cdn.plot.ly/plotly-2.26.0.min.js"></script>
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
  :root {{
    --bg: #07090f; --s1: #0e1117; --s2: #151c27;
    --border: #1e2d3d; --cyan: #00e5ff; --green: #22d3a0;
    --amber: #fbbf24; --purple: #8b5cf6; --text: #dde6f0; --muted: #556070;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: 'DM Sans', sans-serif; background: var(--bg); color: var(--text); padding: 0 0 60px; }}
  body::before {{
    content: ''; position: fixed; inset: 0; z-index: 0; pointer-events: none;
    background-image: linear-gradient(rgba(0,229,255,.02) 1px, transparent 1px),
      linear-gradient(90deg, rgba(0,229,255,.02) 1px, transparent 1px);
    background-size: 40px 40px;
  }}
  .wrap {{ max-width: 1100px; margin: 0 auto; padding: 0 24px; position: relative; z-index: 1; }}

  header {{ padding: 36px 0 28px; border-bottom: 1px solid var(--border); margin-bottom: 32px; }}
  .header-top {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }}
  .brand {{ display: flex; align-items: center; gap: 10px; }}
  .brand-icon {{
    width: 36px; height: 36px; border-radius: 8px;
    background: linear-gradient(135deg, var(--cyan), var(--purple));
    display: flex; align-items: center; justify-content: center; font-size: 16px;
  }}
  .brand-name {{ font-family: 'Syne', sans-serif; font-size: 18px; font-weight: 800;
    background: linear-gradient(90deg, var(--cyan), #fff);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
  .report-date {{ font-family: 'DM Mono', monospace; font-size: 11px; color: var(--muted); }}
  h1 {{ font-family: 'Syne', sans-serif; font-size: 28px; font-weight: 800; letter-spacing: -1px; }}
  .subtitle {{ font-size: 13px; color: var(--muted); margin-top: 4px; }}

  .kpi-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; margin-bottom: 28px; }}
  .kpi-card {{
    background: var(--s1); border: 1px solid var(--border); border-radius: 12px;
    padding: 18px 20px;
  }}
  .kpi-label {{ font-family: 'DM Mono', monospace; font-size: 9px; color: var(--muted);
    text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 8px; }}
  .kpi-value {{ font-family: 'Syne', sans-serif; font-size: 24px; font-weight: 800; }}
  .kpi-value.cyan {{ color: var(--cyan); }}
  .kpi-value.green {{ color: var(--green); }}
  .kpi-value.amber {{ color: var(--amber); }}
  .kpi-value.purple {{ color: var(--purple); }}

  .charts-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 16px; }}
  .chart-card {{
    background: var(--s1); border: 1px solid var(--border); border-radius: 12px;
    padding: 20px;
  }}
  .chart-card.full {{ grid-column: span 2; }}
  .chart-title {{ font-family: 'Syne', sans-serif; font-size: 13px; font-weight: 800;
    margin-bottom: 14px; color: var(--text); }}

  .narrative-card {{
    background: var(--s1); border: 1px solid rgba(0,229,255,.2);
    border-radius: 12px; padding: 24px; margin-bottom: 16px;
  }}
  .narrative-title {{ font-family: 'Syne', sans-serif; font-size: 13px; font-weight: 800;
    color: var(--cyan); margin-bottom: 14px; }}
  .narrative-body {{ font-size: 13px; color: var(--muted); line-height: 1.8;
    white-space: pre-wrap; }}

  footer {{ text-align: center; padding-top: 32px; border-top: 1px solid var(--border);
    font-family: 'DM Mono', monospace; font-size: 10px; color: var(--muted); }}

  @media(max-width:700px) {{
    .kpi-grid {{ grid-template-columns: 1fr 1fr; }}
    .charts-grid {{ grid-template-columns: 1fr; }}
    .chart-card.full {{ grid-column: span 1; }}
  }}
</style>
</head>
<body>
<div class="wrap">
  <header>
    <div class="header-top">
      <div class="brand">
        <div class="brand-icon">⬡</div>
        <span class="brand-name">NEXUS BI AGENT</span>
      </div>
      <span class="report-date">Reporte generado automáticamente · E-Commerce Demo</span>
    </div>
    <h1>Reporte Ejecutivo de Business Intelligence</h1>
    <p class="subtitle">Dataset: Olist Brazilian E-Commerce · {len(rev_dates)} días de datos históricos</p>
  </header>

  <div class="kpi-grid">
    <div class="kpi-card">
      <div class="kpi-label">Revenue Total</div>
      <div class="kpi-value cyan">${kpis['total_revenue']:,.0f}</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">Órdenes Totales</div>
      <div class="kpi-value green">{int(kpis['total_orders']):,}</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">Ticket Promedio</div>
      <div class="kpi-value amber">${kpis['avg_ticket']:,.2f}</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">Clientes Únicos</div>
      <div class="kpi-value purple">{int(kpis['total_customers']):,}</div>
    </div>
  </div>

  <div class="charts-grid">
    <div class="chart-card full">
      <div class="chart-title">📈 Revenue Diario</div>
      <div id="chart-revenue"></div>
    </div>
    <div class="chart-card">
      <div class="chart-title">🏆 Top Categorías por Revenue</div>
      <div id="chart-products"></div>
    </div>
    <div class="chart-card">
      <div class="chart-title">🗺️ Revenue por Estado</div>
      <div id="chart-states"></div>
    </div>
  </div>

  <div class="narrative-card">
    <div class="narrative-title">🤖 Análisis Ejecutivo — Generado por IA</div>
    <div class="narrative-body">{narrative if narrative else "Ejecutá el agente para generar el análisis."}</div>
  </div>

  <footer>NEXUS BI AGENT · Reporte generado automáticamente · {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}</footer>
</div>

<script>
const layout = {{
  paper_bgcolor: 'transparent', plot_bgcolor: 'transparent',
  font: {{ family: 'DM Sans', color: '#dde6f0', size: 11 }},
  margin: {{ t: 10, b: 40, l: 50, r: 20 }},
  xaxis: {{ gridcolor: '#1e2d3d', linecolor: '#1e2d3d' }},
  yaxis: {{ gridcolor: '#1e2d3d', linecolor: '#1e2d3d' }},
  showlegend: false
}};
const cfg = {{responsive: true, displayModeBar: false}};

Plotly.newPlot('chart-revenue', [{{
  x: {json.dumps(rev_dates)},
  y: {json.dumps(rev_values)},
  type: 'scatter', mode: 'lines',
  line: {{ color: '#00e5ff', width: 2 }},
  fill: 'tozeroy', fillcolor: 'rgba(0,229,255,0.06)'
}}], {{...layout, height: 280}}, cfg);

Plotly.newPlot('chart-products', [{{
  x: {json.dumps(prod_values[::-1])},
  y: {json.dumps(prod_names[::-1])},
  type: 'bar', orientation: 'h',
  marker: {{ color: '#8b5cf6' }}
}}], {{...layout, height: 320}}, cfg);

Plotly.newPlot('chart-states', [{{
  x: {json.dumps(state_names)},
  y: {json.dumps(state_values)},
  type: 'bar',
  marker: {{ color: '#22d3a0' }}
}}], {{...layout, height: 320}}, cfg);
</script>
</body>
</html>"""

    with open(OUTPUT, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"✅ Dashboard generado: reports/dashboard.html")
    return OUTPUT

if __name__ == '__main__':
    import sys
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'analysis'))
    from kpis import get_kpis
    from claude_agent import generate_narrative
    kpis, revenue_daily, top_products, top_states = get_kpis()
    narrative = generate_narrative(kpis, top_products, top_states)
    generate_dashboard(narrative)
    print("\n🎯 Abrí reports/dashboard.html en el browser.")