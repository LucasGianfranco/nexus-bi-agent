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

def get_kpis_from_postgres():
    from sqlalchemy import create_engine, text
    import os
    from dotenv import load_dotenv
    
    BASE_DIR_BI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    load_dotenv(os.path.join(BASE_DIR_BI, '.env'))
    
    DATABASE_URL = os.getenv('DATABASE_URL')
    
    if not DATABASE_URL:
        print("⚠️ No hay DATABASE_URL, usando SQLite...")
        return get_kpis()
    
    print("🔗 Conectando a PostgreSQL...")
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        # KPIs principales
        kpis_raw = pd.read_sql(text("""
            SELECT 
                COUNT(*) as total_orders,
                ROUND(SUM(costo_usd)::numeric, 2) as total_revenue,
                ROUND(AVG(costo_usd)::numeric, 2) as avg_ticket,
                COUNT(DISTINCT cliente) as total_customers
            FROM ordenes_logistica
            WHERE estado = 'entregado'
        """), conn)

        # Revenue por día
        revenue_daily = pd.read_sql(text("""
            SELECT 
                fecha::text as order_date,
                ROUND(SUM(costo_usd)::numeric, 2) as revenue
            FROM ordenes_logistica
            WHERE estado = 'entregado' AND fecha IS NOT NULL
            GROUP BY fecha
            ORDER BY fecha
        """), conn)

        # Top productos (clientes en este caso)
        top_products = pd.read_sql(text("""
            SELECT 
                cliente as product_category_name_english,
                ROUND(SUM(costo_usd)::numeric, 2) as revenue,
                COUNT(*) as orders
            FROM ordenes_logistica
            WHERE estado = 'entregado'
            GROUP BY cliente
            ORDER BY revenue DESC
            LIMIT 10
        """), conn)

        # Top estados/ciudades
        top_states = pd.read_sql(text("""
            SELECT 
                ciudad_destino as customer_state,
                ROUND(SUM(costo_usd)::numeric, 2) as revenue,
                COUNT(*) as orders
            FROM ordenes_logistica
            GROUP BY ciudad_destino
            ORDER BY revenue DESC
            LIMIT 10
        """), conn)

    kpis = kpis_raw.iloc[0].to_dict()
    
    # Variación 7 días
    kpis['variation_7d'] = 0
    kpis['trend'] = 'ESTABLE'

    print(f"✅ KPIs desde Postgres:")
    print(f"   💰 Revenue total: ${kpis['total_revenue']:,.2f}")
    print(f"   📦 Órdenes: {int(kpis['total_orders']):,}")

    return kpis, revenue_daily, top_products, top_states