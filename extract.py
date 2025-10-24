import requests
from bs4 import BeautifulSoup

#URL = "https://www.fmbalonmano.com/resultados-clasificaciones?torneo=7663"
URL = "https://resultadosbalonmano.isquad.es/calendario.php?seleccion=0&id=1033293&id_ambito=0&id_territorial=21&id_superficie=1&iframe=0&id_categoria=2608&id_competicion=209599"

def fetch_html():
    """Obtiene el HTML de la página"""
    response = requests.get(URL)
    response.raise_for_status()
    return response.text

def parse_fecha_hora(fecha_text, hora_text):
    """Devuelve fecha y hora, None si es todo el día"""
    fecha_text = fecha_text.strip()
    hora_text = hora_text.strip()
    if hora_text == "0:00" or hora_text == "":
        return fecha_text, None  # Evento todo el día
    return fecha_text, hora_text

def parse_row(row):
    """Parses un row <tr> y devuelve un diccionario con los datos del partido"""
    tds = row.find_all("td")
    # Equipos
    equipos_div = tds[0].find("div", class_="nombres-equipos")
    local = equipos_div.find_all("a")[0].text.strip()
    visitante = equipos_div.find_all("a")[1].text.strip()
    # Marcador (opcional)
    marcador_span = tds[1].find("span", class_="resultado")
    marcador = marcador_span.text.strip() if marcador_span else ""
    # Fecha y hora
    fecha_divs = tds[2].find_all("div")
    fecha_text = fecha_divs[0].text.strip()
    hora_text = fecha_divs[1].text.strip() if len(fecha_divs) > 1 else "0:00"
    fecha, hora = parse_fecha_hora(fecha_text, hora_text)
    # Lugar y enlace
    lugar_a = tds[3].find("a")
    lugar = lugar_a.text.strip() if lugar_a else ""
    enlace_lugar = lugar_a.get("href") if lugar_a else None
    return {
        "local": local,
        "visitante": visitante,
        "marcador": marcador,
        "fecha": fecha,
        "hora": hora,
        "lugar": lugar,
        "enlace_lugar": enlace_lugar
    }

def extract_partidos(html):
    """Extrae todos los partidos de la tabla"""
    soup = BeautifulSoup(html, "html.parser")
    rows = soup.find_all("tr")
    partidos = []
    for row in rows:
        try:
            partido = parse_row(row)
            if partido["local"] and partido["visitante"]:
                partidos.append(partido)
        except Exception:
            continue
    return partidos

def get_partidos():
    html = fetch_html()
    return extract_partidos(html)
