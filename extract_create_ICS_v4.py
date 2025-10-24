import requests
from bs4 import BeautifulSoup
from datetime import datetime
from icalendar import Calendar, Event
from pytz import timezone
import msal

# -------------------------------
# CONFIGURACIÓN
# -------------------------------
#URL_CALENDARIO = "https://www.fmbalonmano.com/resultados-clasificaciones?torneo=7663"
URL_CALENDARIO = "https://resultadosbalonmano.isquad.es/calendario.php?seleccion=0&id=1033293&id_ambito=0&id_territorial=21&id_superficie=1&iframe=0&id_categoria=2608&id_competicion=209599"

HEADERS = {"User-Agent": "Mozilla/5.0"}

ZONA_HORARIA = timezone("Europe/Madrid")
FILENAME = "virgen_europa.ics"
ONEDRIVE_PATH = "/Calendarios/balonmano" + FILENAME  # Carpeta en OneDrive

# Microsoft Graph API
CLIENT_ID = "tu_client_id"
TENANT_ID = "tu_tenant_id"
CLIENT_SECRET = "tu_client_secret"

# -------------------------------
# FUNCIONES DE PARSING
# -------------------------------
def parsear_fecha_hora(td_fecha):
    """Extrae fecha y hora desde td. Si hora es '0:00' o no está, devuelve evento all-day"""
    partes = [div.get_text(strip=True) for div in td_fecha.find_all("div") if div.get_text(strip=True)]
    if not partes:
        return None

    fecha_str = partes[0]
    hora_str = partes[1] if len(partes) > 1 else None

    try:
        fecha = datetime.strptime(fecha_str, "%d/%m/%Y").date()
    except ValueError:
        return None

    if not hora_str or hora_str.strip() in ["0:00", "00:00", "-", "Pendiente"]:
        return fecha  # all-day
    try:
        h, m = map(int, hora_str.split(":"))
        fecha_y_hora = datetime.combine(fecha, datetime.min.time()).replace(hour=h, minute=m)
        return fecha_y_hora
    except ValueError:
        return fecha  # all-day si formato incorrecto

def parsear_row(tr):
    """Extrae datos de un row <tr> del calendario"""
    tds = tr.find_all("td")
    if len(tds) < 4:
        return None

    # Equipos
    equipos_col = tds[0]
    nombres = [a.get_text(strip=True) for a in equipos_col.find_all("a")][:2]
    local, visitante = nombres if len(nombres) == 2 else ("Pendiente", "Pendiente")

    # Marcador
    marcador_span = tds[1].find("span", class_="resultado")
    resultado = marcador_span.get_text(strip=True) if marcador_span else None

    # Fecha y hora
    fecha = parsear_fecha_hora(tds[2])

    # Lugar y enlace
    lugar_a = tds[3].find("a")
    lugar = lugar_a.get_text(strip=True) if lugar_a else "Pendiente"
    url_lugar = lugar_a["href"] if lugar_a and "href" in lugar_a.attrs else None

    return {
        "local": local,
        "visitante": visitante,
        "resultado": resultado,
        "fecha": fecha,
        "lugar": lugar,
        "url_lugar": url_lugar
    }

# -------------------------------
# SCRAPING
# -------------------------------
def obtener_partidos():
    r = requests.get(URL_CALENDARIO, headers=HEADERS)
    soup = BeautifulSoup(r.text, "html.parser")
    rows = soup.find_all("tr")
    partidos = []
    for tr in rows:
        partido = parsear_row(tr)
        if partido:
            partidos.append(partido)
    return partidos

# -------------------------------
# GENERAR ICS
# -------------------------------
def crear_calendario(partidos):
    cal = Calendar()
    cal.add('prodid', '-//Calendario Virgen de Europa//fmbalonmano.com//')
    cal.add('version', '2.0')

    for p in partidos:
        evento = Event()
        evento.add('summary', f"{p['local']} vs {p['visitante']}")

        descripcion = f"Marcador: {p['resultado'] or 'Pendiente'}\nLugar: {p['lugar'] or 'Pendiente'}"
        if p.get("url_lugar"):
            descripcion += f"\n📍 Enlace ubicación: {p['url_lugar']}"

        if p['fecha']:
            if isinstance(p['fecha'], datetime):
                evento.add('dtstart', ZONA_HORARIA.localize(p['fecha']))
                evento.add('dtend', ZONA_HORARIA.localize(p['fecha']))
            else:
                evento.add('dtstart', p['fecha'])
                evento.add('dtend', p['fecha'])
                descripcion += "\n⏰ Hora pendiente de confirmación"

        evento.add('location', p['lugar'] or "Pendiente")
        if p.get("url_lugar"):
            evento.add('url', p["url_lugar"])
        evento.add('description', descripcion)

        cal.add_component(evento)
    return cal

def guardar_ics(cal):
    with open(FILENAME, "wb") as f:
        f.write(cal.to_ical())
    print(f"✅ Archivo {FILENAME} generado")

# -------------------------------
# SUBIR A ONEDRIVE
# -------------------------------
def upload_to_onedrive():
    authority = f"https://login.microsoftonline.com/{TENANT_ID}"
    app = msal.ConfidentialClientApplication(
        CLIENT_ID, authority=authority, client_credential=CLIENT_SECRET
    )
    result = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
    access_token = result["access_token"]

    with open(FILENAME, "rb") as f:
        data = f.read()

    upload_url = f"https://graph.microsoft.com/v1.0/me/drive/root:{ONEDRIVE_PATH}:/content"
    headers = {"Authorization": f"Bearer {access_token}"}
    r = requests.put(upload_url, headers=headers, data=data)
    r.raise_for_status()
    print("✅ Archivo actualizado en OneDrive")

# -------------------------------
# MAIN
# -------------------------------
if __name__ == "__main__":
    partidos = obtener_partidos()
    cal = crear_calendario(partidos)
    guardar_ics(cal)
    upload_to_onedrive()
