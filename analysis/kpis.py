import sqlite3
import os
import pandas as pd # type: ignore

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed', 'nexus_bi.db')

def get_kpis():
    conn = sqlite3.connect(DB_PATH)

    # KPIs globales
    kpis = pd.read_sql('SELECT * FROM kpis', conn).iloc[0].to_dict()

    # Revenue últimos 30 días
    revenue_daily = pd.read_sql('SELECT * FROM revenue_daily ORDER BY order_date DESC LIMIT 30', conn)

    # Revenue últimos 7 días vs 7 días anteriores
    last7  = pd.read_sql("SELECT SUM(revenue) as rev FROM revenue_daily ORDER BY order_date DESC LIMIT 7", conn).iloc[0]['rev']
    prev7  = pd.read_sql("SELECT SUM(revenue) as rev FROM (SELECT revenue FROM revenue_daily ORDER BY order_date DESC LIMIT 14) sub LIMIT 7", conn).iloc[0]['rev']
    var7   = round(((last7 - prev7) / prev7) * 100, 1) if prev7 else 0

    # Top productos
    top_products = pd.read_sql('SELECT * FROM top_products ORDER BY revenue DESC', conn)

    # Top estados
    top_states = pd.read_sql('SELECT * FROM revenue_state ORDER BY revenue DESC LIMIT 5', conn)

    conn.close()

    kpis['last7_revenue']  = round(last7, 2)
    kpis['prev7_revenue']  = round(prev7, 2)
    kpis['variation_7d']   = var7
    kpis['trend']          = '📈 SUBIENDO' if var7 > 0 else '📉 BAJANDO'

    print("📊 KPIs calculados:")
    print(f"   💰 Revenue total:     ${kpis['total_revenue']:,.2f}")
    print(f"   📦 Órdenes totales:   {int(kpis['total_orders']):,}")
    print(f"   🎟️  Ticket promedio:   ${kpis['avg_ticket']:,.2f}")
    print(f"   📅 Últimos 7 días:    ${kpis['last7_revenue']:,.2f}")
    print(f"   📅 7 días anteriores: ${kpis['prev7_revenue']:,.2f}")
    print(f"   📊 Variación 7d:      {kpis['variation_7d']}% {kpis['trend']}")

    return kpis, revenue_daily, top_products, top_states

if __name__ == '__main__':
    get_kpis()