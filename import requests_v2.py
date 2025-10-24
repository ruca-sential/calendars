import requests
from bs4 import BeautifulSoup
from datetime import datetime, time
from icalendar import Calendar, Event
import pytz


# =======================
# CONFIGURACIÓN GLOBAL
# =======================
#URL_BASE = "https://www.fmbalonmano.com/resultados-clasificaciones"
URL_BASE = "https://resultadosbalonmano.isquad.es/calendario.php?seleccion=0&id=1033293&id_ambito=0&id_territorial=21&id_superficie=1&iframe=0&id_categoria=2608&id_competicion=209599"
PARAMS = {
    "territorial": "21",     # FEDERACION TERRITORIAL MADRILEÑA
    "temporadas": "2526",    # Temporada 2025/2026
    "categorias": "2608",    # CAMPEONATO AUTONÓMICO DE LIGA MASCULINO
    "competiciones": "209599", # 3ª TERRITORIAL MASCULINA
    "torneos": "1033293",    # PRIMERA FASE - GRUPO B
}
EQUIPO_OBJETIVO = "VIRGEN DE EUROPA"
ZONA_HORARIA = pytz.timezone("Europe/Madrid")


# =======================
# FUNCIONES DE PARSEO
# =======================

def obtener_html():
    """Descarga la página HTML con los parámetros configurados."""
    response = requests.get(URL_BASE, params=PARAMS)
    response.raise_for_status()
    return response.text


def extraer_filas(html):
    """Obtiene las filas del calendario de la página."""
    soup = BeautifulSoup(html, "html.parser")
    return soup.select("table tbody tr")


def parsear_equipos(td_equipos):
    """Extrae los nombres de los equipos local y visitante de la primera celda."""
    equipos = td_equipos.select(".nombres-equipos a")
    if len(equipos) >= 2:
        local = equipos[0].get_text(strip=True)
        visitante = equipos[1].get_text(strip=True)
    else:
        local, visitante = None, None
    return local, visitante


def parsear_resultado(td_marcador):
    """Extrae el marcador (si existe)."""
    resultado = td_marcador.select_one(".resultado")
    return resultado.get_text(strip=True) if resultado else None


def parsear_fecha_hora(td_fecha):
    """Extrae y convierte la fecha y la hora."""
    partes = [div.get_text(strip=True) for div in td_fecha.find_all("div") if div.get_text(strip=True)]
    fecha_str = partes[0] if partes else None
    hora_str = partes[1] if len(partes) > 1 else None

    if not fecha_str:
        return None

    fecha = datetime.strptime(fecha_str, "%d/%m/%Y")
    if hora_str:
        try:
            h, m = map(int, hora_str.split(":"))
            fecha = fecha.replace(hour=h, minute=m)
        except ValueError:
            fecha = fecha.replace(hour=12)  # hora pendiente
    else:
        fecha = fecha.replace(hour=12)
    return fecha


def parsear_lugar(td_lugar):
    """Obtiene el nombre del lugar."""
    enlace = td_lugar.find("a")
    return enlace.get_text(strip=True) if enlace else td_lugar.get_text(strip=True)


def parsear_partido(row):
    """Extrae toda la información de una fila del calendario."""
    celdas = row.find_all("td")
    if len(celdas) < 4:
        return None

    local, visitante = parsear_equipos(celdas[0])
    resultado = parsear_resultado(celdas[1])
    fecha = parsear_fecha_hora(celdas[2])
    lugar = parsear_lugar(celdas[3])

    return {
        "local": local,
        "visitante": visitante,
        "resultado": resultado,
        "fecha": fecha,
        "lugar": lugar
    }


# =======================
# FUNCIONES DE CALENDARIO
# =======================

def crear_calendario(partidos):
    """Crea el objeto Calendar en formato iCalendar."""
    cal = Calendar()
    cal.add('prodid', '-//Calendario Virgen de Europa//fmbalonmano.com//')
    cal.add('version', '2.0')

    for p in partidos:
        evento = Event()
        evento.add('summary', f"{p['local']} vs {p['visitante']}")
        if p['fecha']:
            evento.add('dtstart', ZONA_HORARIA.localize(p['fecha']))
            evento.add('dtend', ZONA_HORARIA.localize(p['fecha']))
        evento.add('location', p['lugar'] or "Pendiente")
        evento.add('description', f"Marcador: {p['resultado'] or 'Pendiente'}\nLugar: {p['lugar'] or 'Pendiente'}")
        cal.add_component(evento)

    return cal


def guardar_calendario(cal, filename="virgen_de_europa.ics"):
    """Guarda el calendario en un archivo .ics."""
    with open(filename, "wb") as f:
        f.write(cal.to_ical())
    print(f"✅ Calendario guardado en: {filename}")


# =======================
# MAIN
# =======================

def main():
    html = obtener_html()
    filas = extraer_filas(html)

    partidos = []
    for row in filas:
        p = parsear_partido(row)
        if not p:
            continue
        if EQUIPO_OBJETIVO in (p["local"] or "").upper() or EQUIPO_OBJETIVO in (p["visitante"] or "").upper():
            partidos.append(p)

    if not partidos:
        print("⚠️ No se encontraron partidos del Virgen de Europa.")
        return

    cal = crear_calendario(partidos)
    guardar_calendario(cal)


if __name__ == "__main__":
    main()
