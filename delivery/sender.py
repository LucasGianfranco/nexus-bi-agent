import os
import resend # type: ignore
from dotenv import load_dotenv # type: ignore

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, '.env'))

resend.api_key = os.getenv('RESEND_API_KEY')
TO_EMAIL   = os.getenv('TO_EMAIL')
REPORT_URL = os.getenv('REPORT_URL')

def send_report(narrative="", kpis=None):
    print("📧 Enviando reporte por email...")

    preview = "\n".join(narrative.split("\n")[:15]) if narrative else ""

    html_body = f"""
<html><body style="font-family:Arial,sans-serif;background:#07090f;color:#dde6f0;padding:32px">
  <h2 style="color:#00e5ff">NEXUS BI AGENT — Reporte Ejecutivo</h2>
  <hr style="border-color:#1e2d3d">
  <table style="width:100%;margin:20px 0">
    <tr>
      <td style="background:#0e1117;border:1px solid #1e2d3d;border-radius:8px;padding:16px;text-align:center">
        <div style="font-size:11px;color:#556070;text-transform:uppercase">Revenue Total</div>
        <div style="font-size:22px;font-weight:800;color:#00e5ff">${kpis['total_revenue']:,.0f}</div>
      </td>
      <td style="width:12px"></td>
      <td style="background:#0e1117;border:1px solid #1e2d3d;border-radius:8px;padding:16px;text-align:center">
        <div style="font-size:11px;color:#556070;text-transform:uppercase">Órdenes</div>
        <div style="font-size:22px;font-weight:800;color:#22d3a0">{int(kpis['total_orders']):,}</div>
      </td>
      <td style="width:12px"></td>
      <td style="background:#0e1117;border:1px solid #1e2d3d;border-radius:8px;padding:16px;text-align:center">
        <div style="font-size:11px;color:#556070;text-transform:uppercase">Ticket Prom.</div>
        <div style="font-size:22px;font-weight:800;color:#fbbf24">${kpis['avg_ticket']:,.2f}</div>
      </td>
    </tr>
  </table>
  <div style="background:#0e1117;border-left:3px solid #00e5ff;padding:16px;border-radius:8px;margin:20px 0">
    <div style="font-size:11px;color:#00e5ff;text-transform:uppercase;margin-bottom:10px">Análisis IA</div>
    <div style="font-size:12px;color:#8899aa;line-height:1.7;white-space:pre-wrap">{preview}</div>
  </div>
  <div style="text-align:center;margin:28px 0">
    <a href="{REPORT_URL}" style="background:linear-gradient(135deg,#00e5ff,#8b5cf6);color:#000;font-weight:700;padding:14px 32px;border-radius:8px;text-decoration:none;display:inline-block">
      Ver Reporte Completo →
    </a>
  </div>
  <hr style="border-color:#1e2d3d">
  <p style="font-size:11px;color:#556070;text-align:center">NEXUS BI AGENT · Reporte generado automáticamente</p>
</body></html>
"""

    try:
        params = {
            "from": "NEXUS BI <onboarding@resend.dev>",
            "to": [TO_EMAIL],
            "subject": "📊 NEXUS BI — Reporte Ejecutivo E-Commerce",
            "html": html_body,
        }
        email = resend.Emails.send(params)
        print(f"✅ Email enviado. ID: {email['id']}")
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