import os
import sys
from flask import Flask, render_template, request, jsonify # type: ignore
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, '.env'))
API_KEY = os.environ.get('ANTHROPIC_API_KEY') or os.getenv('ANTHROPIC_API_KEY')
sys.path.append(os.path.join(BASE_DIR, 'analysis'))
sys.path.append(os.path.join(BASE_DIR, 'reports'))
sys.path.append(os.path.join(BASE_DIR, 'delivery'))

app = Flask(__name__)

def process_request(user_message):
    import requests as req
    from kpis import get_kpis

    kpis, revenue_daily, top_products, top_states = get_kpis()

    API_KEY = os.environ.get('ANTHROPIC_API_KEY')
    prompt = f"""
Sos un agente de Business Intelligence con acceso a datos reales de e-commerce brasileño.

DATOS DISPONIBLES:
- Revenue total: ${float(kpis['total_revenue']):,.2f}
- Órdenes totales: {int(kpis['total_orders']):,}
- Ticket promedio: ${float(kpis['avg_ticket']):,.2f}
- Clientes únicos: {int(kpis['total_customers']):,}
- Variación 7 días: {kpis['variation_7d']}% ({kpis['trend']})
- Top categorías: {top_products[['product_category_name_english','revenue']].head(3).to_string(index=False)}
- Top estados: {top_states[['customer_state','revenue']].head(3).to_string(index=False)}

El CFO preguntó: "{user_message}"

Respondé de forma conversacional, directa y precisa en 3-5 oraciones máximo.
Usá los datos reales. No uses markdown ni bullets. Hablá como un analista senior explicándole a un ejecutivo.
"""

    response = req.post(
        'https://api.anthropic.com/v1/messages',
        headers={
            'x-api-key': API_KEY,
            'anthropic-version': '2023-06-01',
            'content-type': 'application/json',
        },
        json={
            'model': 'claude-sonnet-4-6',
            'max_tokens': 300,
            'messages': [{'role': 'user', 'content': prompt}]
        }
    )
    print(f"STATUS: {response.status_code}")
    print(f"RESPONSE: {response.text[:200]}")
    result = response.json()
    conversational_response = result['content'][0]['text']
    return conversational_response, kpis

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    message = data.get('message', '')
    try:
        response, kpis = process_request(message)
        return jsonify({
            'status': 'ok',
            'response': response,
            'kpis': kpis,
            'dashboard_url': os.getenv('REPORT_URL')
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/send-email', methods=['POST'])
def send_email():
    try:
        from kpis import get_kpis
        from claude_agent import generate_narrative
        from sender import send_report
        kpis, revenue_daily, top_products, top_states = get_kpis()
        narrative = generate_narrative(kpis, top_products, top_states)
        send_report(narrative, kpis)
        return jsonify({'status': 'ok'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/generate-dashboard', methods=['POST'])
def generate_dash():
    try:
        from kpis import get_kpis
        from claude_agent import generate_narrative
        from generator import generate_dashboard
        kpis, revenue_daily, top_products, top_states = get_kpis()
        narrative = generate_narrative(kpis, top_products, top_states)
        generate_dashboard(narrative)
        return jsonify({'status': 'ok', 'url': os.getenv('REPORT_URL')})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)