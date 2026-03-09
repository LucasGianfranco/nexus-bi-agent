import os
import sendgrid # type: ignore
from sendgrid.helpers.mail import Mail # type: ignore
from dotenv import load_dotenv # type: ignore
import base64

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, '.env'))

SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')
FROM_EMAIL       = os.getenv('FROM_EMAIL')
TO_EMAIL         = os.getenv('TO_EMAIL')
REPORT_URL       = os.getenv('REPORT_URL')

def send_report(narrative="", kpis=None):
    print("📧 Enviando reporte por email...")

    # Top 3 insights del narrative
    preview = "\n".join(narrative.split("\n")[:15]) if narrative else "Reporte disponible en el link."

    html_body = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
  body {{ font-family: 'Helvetica Neue', sans-serif; background: #07090f; color: #dde6f0; margin: 0; padding: 0; }}
  .container {{ max-width: 600px; margin: 0 auto; padding: 40px 24px; }}
  .header {{ border-bottom: 1px solid #1e2d3d; padding-bottom: 24px; margin-bottom: 28px; }}
  .brand {{ font-size: 20px; font-weight: 800; color: #00e5ff; letter-spacing: -0.5px; }}
  .brand span {{ color: #dde6f0; }}
  h1 {{ font-size: 22px; font-weight: 700; margin: 16px 0 6px; }}
  .subtitle {{ font-size: 13px; color: #556070; margin-bottom: 28px; }}
  .kpi-row {{ display: flex; gap: 12px; margin-bottom: 24px; }}
  .kpi-box {{ flex: 1; background: #0e1117; border: 1px solid #1e2d3d; border-radius: 10px; padding: 14px; text-align: center; }}
  .kpi-label {{ font-size: 9px; color: #556070; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 6px; }}
  .kpi-value {{ font-size: 18px; font-weight: 800; color: #00e5ff; }}
  .narrative-box {{ background: #0e1117; border: 1px solid #1e2d3d; border-left: 3px solid #00e5ff; border-radius: 10px; padding: 20px; margin-bottom: 24px; }}
  .narrative-title {{ font-size: 11px; color: #00e5ff; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 12px; font-weight: 700; }}
  .narrative-text {{ font-size: 12px; color: #8899aa; line-height: 1.7; white-space: pre-wrap; }}
  .cta {{ text-align: center; margin: 28px 0; }}
  .cta a {{ background: linear-gradient(135deg, #00e5ff, #8b5cf6); color: #000; font-weight: 700; font-size: 14px; padding: 14px 32px; border-radius: 8px; text-decoration: none; display: inline-block; }}
  .footer {{ border-top: 1px solid #1e2d3d; padding-top: 20px; text-align: center; font-size: 11px; color: #556070; }}
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <div class="brand">NEXUS <span>BI AGENT</span></div>
  </div>

  <h1>Reporte Ejecutivo de Business Intelligence</h1>
  <p class="subtitle">Generado automáticamente · E-Commerce Demo</p>

  <div class="kpi-row">
    <div class="kpi-box">
      <div class="kpi-label">Revenue Total</div>
      <div class="kpi-value">${kpis['total_revenue']:,.0f}</div>
    </div>
    <div class="kpi-box">
      <div class="kpi-label">Órdenes</div>
      <div class="kpi-value" style="color:#22d3a0">{int(kpis['total_orders']):,}</div>
    </div>
    <div class="kpi-box">
      <div class="kpi-label">Ticket Prom.</div>
      <div class="kpi-value" style="color:#fbbf24">${kpis['avg_ticket']:,.2f}</div>
    </div>
  </div>

  <div class="narrative-box">
    <div class="narrative-title">🤖 Análisis IA — Top Insights</div>
    <div class="narrative-text">{preview}</div>
  </div>

  <div class="cta">
    <a href="{REPORT_URL}">Ver Reporte Completo →</a>
  </div>

  <div class="footer">
    NEXUS BI AGENT · Reporte generado automáticamente<br>
    Para dejar de recibir estos reportes, respondé este email.
  </div>
</div>
</body>
</html>
"""

    message = Mail(
        from_email=FROM_EMAIL,
        to_emails=TO_EMAIL,
        subject='📊 NEXUS BI — Reporte Ejecutivo E-Commerce',
        html_content=html_body
    )

    try:
        sg = sendgrid.SendGridAPIClient(api_key=SENDGRID_API_KEY)
        response = sg.send(message)
        print(f"✅ Email enviado. Status: {response.status_code}")
        print(f"   Para: {TO_EMAIL}")
        print(f"   Link: {REPORT_URL}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == '__main__':
    import sys
    sys.path.append(os.path.join(BASE_DIR, 'analysis'))
    from kpis import get_kpis
    from claude_agent import generate_narrative
    kpis, revenue_daily, top_products, top_states = get_kpis()
    narrative = generate_narrative(kpis, top_products, top_states)
    send_report(narrative, kpis)