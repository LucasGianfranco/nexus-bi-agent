import pandas as pd # type: ignore

def transform(data):
    print("⚙️  Transformando datos...")

    orders      = data['orders'].copy()
    order_items = data['order_items'].copy()
    products    = data['products'].copy()
    customers   = data['customers'].copy()
    payments    = data['payments'].copy()
    category    = data['category'].copy()

    # ── 1. FECHAS ──────────────────────────────────────
    orders['order_purchase_timestamp'] = pd.to_datetime(orders['order_purchase_timestamp'])
    orders['order_year']  = orders['order_purchase_timestamp'].dt.year
    orders['order_month'] = orders['order_purchase_timestamp'].dt.month
    orders['order_week']  = orders['order_purchase_timestamp'].dt.isocalendar().week.astype(int)
    orders['order_date']  = orders['order_purchase_timestamp'].dt.date

    # ── 2. SOLO ORDENES ENTREGADAS ─────────────────────
    orders_delivered = orders[orders['order_status'] == 'delivered'].copy()
    print(f"   ✅ Órdenes entregadas: {len(orders_delivered):,} de {len(orders):,}")

    # ── 3. MERGE PRINCIPAL ─────────────────────────────
    df = orders_delivered.merge(order_items, on='order_id', how='left')
    df = df.merge(payments[['order_id','payment_value']].groupby('order_id').sum().reset_index(), on='order_id', how='left')
    df = df.merge(customers[['customer_id','customer_state','customer_city']], on='customer_id', how='left')
    df = df.merge(products[['product_id','product_category_name']], on='product_id', how='left')
    df = df.merge(category, on='product_category_name', how='left')

    # ── 4. REVENUE DIARIO ──────────────────────────────
    revenue_daily = (
        df.groupby('order_date')
        .agg(orders=('order_id', 'nunique'), revenue=('payment_value', 'sum'))
        .reset_index()
        .sort_values('order_date')
    )

    # ── 5. TOP PRODUCTOS ───────────────────────────────
    top_products = (
        df.groupby('product_category_name_english')
        .agg(orders=('order_id', 'nunique'), revenue=('payment_value', 'sum'))
        .reset_index()
        .sort_values('revenue', ascending=False)
        .head(10)
    )

    # ── 6. REVENUE POR ESTADO ──────────────────────────
    revenue_by_state = (
        df.groupby('customer_state')
        .agg(orders=('order_id', 'nunique'), revenue=('payment_value', 'sum'))
        .reset_index()
        .sort_values('revenue', ascending=False)
    )

    # ── 7. KPIs GLOBALES ───────────────────────────────
    kpis = {
        'total_revenue':    round(df['payment_value'].sum(), 2),
        'total_orders':     df['order_id'].nunique(),
        'avg_ticket':       round(df['payment_value'].sum() / df['order_id'].nunique(), 2),
        'total_customers':  df['customer_id'].nunique(),
        'top_state':        revenue_by_state.iloc[0]['customer_state'],
        'top_category':     top_products.iloc[0]['product_category_name_english'],
    }

    print(f"   💰 Revenue total:    $ {kpis['total_revenue']:,.2f}")
    print(f"   📦 Órdenes totales:  {kpis['total_orders']:,}")
    print(f"   🎟️  Ticket promedio:  $ {kpis['avg_ticket']:,.2f}")
    print(f"   👥 Clientes únicos:  {kpis['total_customers']:,}")
    print(f"   🏆 Top estado:       {kpis['top_state']}")
    print(f"   🏆 Top categoría:    {kpis['top_category']}")

    return {
        'df':               df,
        'revenue_daily':    revenue_daily,
        'top_products':     top_products,
        'revenue_by_state': revenue_by_state,
        'kpis':             kpis,
    }

if __name__ == '__main__':
    from extract import load_raw
    data = load_raw()
    result = transform(data)
    print("\n🎯 Transformación completada.")