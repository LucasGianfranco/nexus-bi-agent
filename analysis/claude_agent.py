import os
import requests # type: ignore
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

API_KEY = os.getenv('ANTHROPIC_API_KEY')

def generate_narrative(kpis, top_products, top_states):
    print("🤖 Generando narrativa con Claude...")

    prompt = f"""
Sos un Senior Business Intelligence Analyst analizando datos de e-commerce brasileño.
Generá un reporte ejecutivo en español basado en estos KPIs reales:

MÉTRICAS GLOBALES:
- Revenue total histórico: ${float(kpis['total_revenue']):,.2f}
- Órdenes totales entregadas: {int(kpis['total_orders']):,}
- Ticket promedio: ${float(kpis['avg_ticket']):,.2f}
- Clientes únicos: {int(kpis['total_customers']):,}
- Variación últimos 7 días: {kpis['variation_7d']}% ({kpis['trend']})

TOP 3 CATEGORÍAS POR REVENUE:
{top_products[['product_category_name_english','revenue']].head(3).to_string(index=False)}

TOP 3 ESTADOS POR REVENUE:
{top_states[['customer_state','revenue','orders']].head(3).to_string(index=False)}

Estructura tu análisis así:
1. RESUMEN EJECUTIVO (2-3 oraciones con lo más importante)
2. INSIGHTS CLAVE (3 bullets con hallazgos accionables)
3. ALERTAS (1-2 puntos de atención o riesgos detectados)
4. RECOMENDACIONES (2 acciones concretas para el negocio)

Sé directo, preciso y orientado a decisiones. Sin introducciones genéricas.
"""

    response = requests.post(
        'https://api.anthropic.com/v1/messages',
        headers={
            'x-api-key': API_KEY,
            'anthropic-version': '2023-06-01',
            'content-type': 'application/json',
        },
        json={
            'model': 'claude-sonnet-4-6',
            'max_tokens': 1000,
            'messages': [{'role': 'user', 'content': prompt}]
        }
    )

    if response.status_code == 200:
        narrative = response.json()['content'][0]['text']
        print("✅ Narrativa generada.")
        print("\n" + "─"*60)
        print(narrative)
        print("─"*60)
        return narrative
    else:
        print(f"❌ Error API: {response.status_code} — {response.text}")
        return None

if __name__ == '__main__':
    from kpis import get_kpis
    kpis, revenue_daily, top_products, top_states = get_kpis()
    generate_narrative(kpis, top_products, top_states)