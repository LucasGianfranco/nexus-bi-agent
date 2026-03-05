import pandas as pd # type: ignore
import os

RAW = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw')

def load_raw():
    print("📥 Cargando CSVs...")
    
    orders       = pd.read_csv(f'{RAW}/olist_orders_dataset.csv')
    order_items  = pd.read_csv(f'{RAW}/olist_order_items_dataset.csv')
    products     = pd.read_csv(f'{RAW}/olist_products_dataset.csv')
    customers    = pd.read_csv(f'{RAW}/olist_customers_dataset.csv')
    payments     = pd.read_csv(f'{RAW}/olist_order_payments_dataset.csv')
    reviews      = pd.read_csv(f'{RAW}/olist_order_reviews_dataset.csv')
    sellers      = pd.read_csv(f'{RAW}/olist_sellers_dataset.csv')
    category     = pd.read_csv(f'{RAW}/product_category_name_translation.csv')
    geolocation  = pd.read_csv(f'{RAW}/olist_geolocation_dataset.csv')

    print(f"✅ orders:      {len(orders):,} filas")
    print(f"✅ order_items: {len(order_items):,} filas")
    print(f"✅ products:    {len(products):,} filas")
    print(f"✅ customers:   {len(customers):,} filas")
    print(f"✅ payments:    {len(payments):,} filas")

    return {
        'orders': orders,
        'order_items': order_items,
        'products': products,
        'customers': customers,
        'payments': payments,
        'reviews': reviews,
        'sellers': sellers,
        'category': category,
        'geolocation': geolocation
    }

if __name__ == '__main__':
    data = load_raw()
    print("\n🎯 Todos los archivos cargados correctamente.")