import sqlite3
import os
import pandas as pd # type: ignore
from extract import load_raw
from transform import transform

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed', 'nexus_bi.db')

def load_to_db(result):
    print("💾 Cargando en SQLite...")

    conn = sqlite3.connect(DB_PATH)

    result['revenue_daily'].to_sql('revenue_daily',    conn, if_exists='replace', index=False)
    result['top_products'].to_sql('top_products',      conn, if_exists='replace', index=False)
    result['revenue_by_state'].to_sql('revenue_state', conn, if_exists='replace', index=False)

    # KPIs como tabla de una fila
    pd.DataFrame([result['kpis']]).to_sql('kpis', conn, if_exists='replace', index=False)

    # Tabla principal (limitada a columnas clave para no pesar demasiado)
    cols = ['order_id','customer_id','order_date','order_year','order_month',
            'payment_value','customer_state','product_category_name_english']
    result['df'][cols].to_sql('orders_fact', conn, if_exists='replace', index=False)

    conn.close()

    size = os.path.getsize(DB_PATH) / 1024 / 1024
    print(f"   ✅ revenue_daily:  {len(result['revenue_daily']):,} filas")
    print(f"   ✅ top_products:   {len(result['top_products']):,} filas")
    print(f"   ✅ revenue_state:  {len(result['revenue_by_state']):,} filas")
    print(f"   ✅ orders_fact:    {len(result['df']):,} filas")
    print(f"   📦 Tamaño DB:      {size:.1f} MB")

if __name__ == '__main__':
    data   = load_raw()
    result = transform(data)
    load_to_db(result)
    print("\n🎯 ETL completo. Base de datos lista en data/processed/nexus_bi.db")