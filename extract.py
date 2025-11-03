import requests
from bs4 import BeautifulSoup

#URL = "https://www.fmbalonmano.com/resultados-clasificaciones?torneo=7663"
URL = {"2TM" : "https://resultadosbalonmano.isquad.es/calendario2.php?seleccion=0&id=1033290&id_ambito=0&id_territorial=21&id_superficie=1&iframe=0&id_categoria=2608&id_competicion=209598",
       "3TM" : "https://resultadosbalonmano.isquad.es/calendario2.php?seleccion=0&id=1033293&id_ambito=0&id_territorial=21&id_superficie=1&iframe=0&id_categoria=2608&id_competicion=209599"}

def fetch_html(filter_cat):
    """Obtiene el HTML de la página"""
    if (filter_cat not in URL):
        raise Exception("Categoría no reconocida: {fitler_cat}")

    response = requests.get(URL[filter_cat])
    response.raise_for_status()
    return response.text

def parse_fecha_hora(fecha_text, hora_text):
    """Devuelve fecha y hora, None si es todo el día"""
    fecha_text = fecha_text.strip()
    hora_text = hora_text.strip()
    if hora_text == "0:00" or hora_text == "":
        return fecha_text, None  # Evento todo el día
    return fecha_text, hora_text

def parse_row_OLD(card):
    """
    Parsea un bloque <div class='info-content partido-card'> y devuelve un diccionario
    con los datos del partido en el mismo formato que la versión anterior.
    """

    # --- Equipos ---
    equipos_div = card.select_one(".nombres-equipos") or card.select_one(".versus-nombre")
    if not equipos_div:
        raise ValueError("No se encontró el bloque de equipos")

    nombres = [a.get_text(strip=True) for a in equipos_div.find_all("a")]
    if len(nombres) < 3:
        # En algunos casos los nombres están como <div> sin <a>
        nombres = [d.get_text(strip=True) for d in equipos_div.find_all("div")]

    local = nombres[0] if nombres else "Desconocido"
    visitante = nombres[2] if len(nombres) > 1 else "Desconocido"

    # --- Marcador (si existe) ---
    marcador_span = card.select_one(".resultados")
    marcador = marcador_span.get_text(strip=True) if marcador_span else ""

    # --- Fecha y hora ---
    fecha_div = card.select_one(".fecha div:nth-of-type(1)")
    hora_div = card.select_one(".fecha div:nth-of-type(2)")
    fecha_text = fecha_div.get_text(strip=True) if fecha_div else None
    hora_text = hora_div.get_text(strip=True) if hora_div else "0:00"

    # Parseo seguro de fecha/hora
    fecha, hora = parse_fecha_hora(fecha_text, hora_text)

    # --- Lugar y enlace ---
    lugar_a = card.select_one(".lugar a")
    lugar = lugar_a.get_text(strip=True) if lugar_a else ""
    enlace_lugar = lugar_a["href"] if lugar_a and lugar_a.has_attr("href") else None

    return {
        "local": local,
        "visitante": visitante,
        "marcador": marcador,
        "fecha": fecha,
        "hora": hora,
        "lugar": lugar,
        "enlace_lugar": enlace_lugar
    }

def parse_row(card):
    """
    Parsea un bloque <div class="info-content partido-card"> de la web FMBalonmano
    y devuelve un diccionario con los datos del partido.
    """

    # --- Equipos ---
    equipos_div = card.select_one(".versus-nombre span.custom-col")
    equipos = [e.get_text(strip=True) for e in equipos_div.find_all("div") if e.get_text(strip=True)]
    
    local = equipos[0] if len(equipos) >= 1 else ""
    visitante = equipos[-1] if len(equipos) >= 2 else ""

    # --- Marcador ---
    marcador_div = card.select_one(".resultados")
    marcador = marcador_div.get_text(strip=True) if marcador_div else ""

    # --- Fecha y hora ---
    fecha_hora_div = card.select_one(".partido-data > div:nth-of-type(2)")
    fecha, hora = None, None
    if fecha_hora_div:
        texto_fecha = fecha_hora_div.get_text(strip=True).replace("h", "")
        partes = texto_fecha.split()
        if len(partes) >= 2:
            fecha = partes[0].replace("-", "/")  # cambia formato 05-10-2025 → 05/10/2025
            hora = partes[1]
        elif len(partes) == 1:
            fecha = partes[0].replace("-", "/")
            hora = "0:00"

    # --- Lugar ---
    lugar_div = card.select_one(".partido-campo div")
    lugar = lugar_div.get_text(strip=True) if lugar_div else ""
    enlace_lugar = None  # en este HTML no viene el enlace de Maps

    return {
        "local": local,
        "visitante": visitante,
        "marcador": marcador,
        "fecha": fecha,
        "hora": hora,
        "lugar": lugar,
        "enlace_lugar": enlace_lugar
    }



def extract_partidos(html, filter_team):
    """Extrae todos los partidos de la tabla"""
    soup = BeautifulSoup(html, "html.parser")
    rows = soup.select("div.info-content.partido-card")
    partidos = []
    for row in rows:
        try:
            partido = parse_row(row)
            if partido["local"] and partido["visitante"] and (filter_team.lower() in partido["local"].lower() or filter_team.lower() in partido["visitante"].lower()):
                partidos.append(partido)
        except Exception:
            continue
    return partidos

def get_partidos(filter_cat, filter_team):
    html = fetch_html(filter_cat)
    return extract_partidos(html, filter_team)
