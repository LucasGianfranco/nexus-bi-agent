import os
import sys

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(BASE_DIR, 'etl'))
sys.path.append(os.path.join(BASE_DIR, 'analysis'))
sys.path.append(os.path.join(BASE_DIR, 'reports'))
sys.path.append(os.path.join(BASE_DIR, 'delivery'))

print("🚀 NEXUS BI AGENT — Iniciando pipeline completo...")
print("="*55)

# PASO 1 — ETL
print("\n📥 PASO 1/5 — ETL: Extracción y transformación...")
from extract import load_raw
from transform import transform
from load import load_to_db
data   = load_raw()
result = transform(data)
load_to_db(result)

# PASO 2 — KPIs
print("\n📊 PASO 2/5 — Calculando KPIs...")
from kpis import get_kpis
kpis, revenue_daily, top_products, top_states = get_kpis()

# PASO 3 — Claude API
print("\n🤖 PASO 3/5 — Generando narrativa con Claude...")
from claude_agent import generate_narrative
narrative = generate_narrative(kpis, top_products, top_states)

# PASO 4 — Dashboard
print("\n📈 PASO 4/5 — Generando dashboard HTML...")
from generator import generate_dashboard
generate_dashboard(narrative)

# PASO 5 — Email
print("\n📧 PASO 5/5 — Enviando reporte por email...")
from sender import send_report
send_report(narrative, kpis)

print("\n" + "="*55)
print("✅ NEXUS BI AGENT — Pipeline completado exitosamente.")
print(f"   Dashboard: https://lucasgianfranco.github.io/nexus-bi-agent/reports/dashboard.html")
print("="*55)