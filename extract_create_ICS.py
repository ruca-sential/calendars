import requests
from bs4 import BeautifulSoup
from datetime import datetime
from icalendar import Calendar, Event
import pytz

# === CONFIGURACIÓN ===
#URL_BASE = "https://www.fmbalonmano.com/resultados-clasificaciones"
#URL_BASE = "https://resultadosbalonmano.isquad.es/competicion.php?id_superficie=1&seleccion=0&id_categoria=2608&id_competicion=209599&id=1033293&id_temp=2526&id_territorial=21&id_ambito=0"
URL_BASE = "https://resultadosbalonmano.isquad.es/calendario.php?seleccion=0&id=1033293&id_ambito=0&id_territorial=21&id_superficie=1&iframe=0&id_categoria=2608&id_competicion=209599"
PARAMS = {
    "territorial": "21",     # FEDERACION TERRITORIAL MADRILEÑA
    "temporadas": "2526",    # Temporada 2025/2026
    "categorias": "2608",    # CAMPEONATO AUTONÓMICO DE LIGA MASCULINO
    "competiciones": "209599", # 3ª TERRITORIAL MASCULINA
    "torneos": "1033293",    # PRIMERA FASE - GRUPO B
}

# === DESCARGA Y PARSEO DE LA PÁGINA ===
response = requests.get(URL_BASE, params=PARAMS)
response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")

# Buscar las filas de partidos
rows = soup.select("table tbody tr")
if not rows:
    raise RuntimeError("No se encontraron filas de calendario. Revisa los selectores o el HTML de la web.")

# === CREAR CALENDARIO ===
cal = Calendar()
cal.add('prodid', '-//Calendario Virgen de Europa//fmbalonmano.com//')
cal.add('version', '2.0')

# === PROCESAR PARTIDOS ===
for row in rows:
    cols = [c.get_text(strip=True) for c in row.find_all('td')]
    if len(cols) < 5:
        continue

    jornada, local, marcador, visitante, fecha, hora, lugar = cols[0], cols[1], cols[2], cols[3], cols[4], cols[5], cols[6] if len(cols) > 6 else ("", "")

    # Solo partidos donde juega Virgen de Europa
    if "VIRGEN DE EUROPA" not in (local + visitante).upper():
        continue

    # Fecha y hora
    try:
        fecha_evento = datetime.strptime(fecha, "%d/%m/%Y")
        if hora and hora != "0:00":
            hora_evento = datetime.strptime(hora, "%H:%M").time()
            fecha_evento = datetime.combine(fecha_evento, hora_evento)
        else:
            fecha_evento = fecha_evento.replace(hour=12)  # Hora por defecto si está pendiente
    except Exception:
        continue

    # Crear evento
    evento = Event()
    evento.add('summary', f"{local} vs {visitante}")
    evento.add('dtstart', pytz.timezone("Europe/Madrid").localize(fecha_evento))
    evento.add('dtend', pytz.timezone("Europe/Madrid").localize(fecha_evento))
    evento.add('location', lugar if lugar else "Pendiente de confirmar")
    evento.add('description', f"Jornada: {jornada}\nLugar: {lugar or 'Pendiente'}\nHora: {hora or 'Pendiente'}")
    cal.add_component(evento)

# === GUARDAR ARCHIVO ===
with open("virgen_de_europa_auto.ics", "wb") as f:
    f.write(cal.to_ical())

print("✅ Calendario generado: virgen_de_europa_auto.ics")
