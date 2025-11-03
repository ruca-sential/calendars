import os
from datetime import datetime, timedelta
from icalendar import Calendar, Event
import uuid

DROPBOX_FOLDER = r"C:\Users\gabri\Dropbox\Calendarios\Balonmano"

def crear_evento_seguro(partido):
    """Crea un evento iCal compatible con Google Calendar."""
    if not partido.get("fecha"):
        print(f"se descarta partido [{partido["local"]} vs {partido["visitante"]}] xq no tiene fecha: fecha")
        return None  # sin fecha, no se añade

    event = Event()
    fecha = partido["fecha"]
    hora = partido.get("hora")

     # --- Parseo de fecha y hora ---
    if hora and hora != "00:00":
        dtstart = datetime.strptime(f"{fecha} {hora}", "%d/%m/%Y %H:%M")
        dtend = dtstart + timedelta(hours=1)
        event.add("dtstart", dtstart)
        event.add("dtend", dtend)
    else:
        # evento de todo el día
        d = datetime.strptime(fecha, "%d/%m/%Y").date()
        event.add("dtstart", d, parameters={"VALUE": "DATE"})
        event.add("dtend", (d + timedelta(days=1)), parameters={"VALUE": "DATE"})

    # --- Título del evento ---
    summary = f"{partido['local']} vs {partido['visitante']}"
    event.add("summary", summary)

    # --- Lugar ---
    if partido.get("lugar"):
        event.add("location", partido["lugar"])

    if partido.get("enlace_lugar"):
        event.add("url", partido["enlace_lugar"])

    # --- Calcular estado del partido ---
    marcador = partido.get("marcador", "").strip()
    tiene_fecha = bool(partido.get("fecha"))
    tiene_lugar = bool(partido.get("lugar"))

    if marcador:
        estado = "Finalizado"
    elif tiene_fecha and tiene_lugar:
        estado = "Confirmado"
    else:
        estado = "Pendiente"

    # --- Descripción ---
    descripcion = [f"Estado: {estado}"]
    if marcador:
        descripcion.append(f"Resultado: {marcador}")
    if partido.get("enlace_lugar"):
        descripcion.append(f"Ubicación: {partido['enlace_lugar']}")

    # Si hay algo en la descripción, se añade
    if descripcion:
        event.add("description", "\n".join(descripcion))

    # Campos obligatorios
    event.add("uid", str(uuid.uuid4()) + "@virgen_europa")
    event.add("dtstamp", datetime.utcnow())

    return event


def guardar_calendario_seguro(partidos, file_name):
    ICS_PATH=os.path.join(DROPBOX_FOLDER, f"{file_name}.ics")

    cal = Calendar()
    cal.add("prodid", "-//Calendario Balonmano Virgen de Europa//")
    cal.add("version", "2.0")

    for p in partidos:
        ev = crear_evento_seguro(p)
        if ev:
            cal.add_component(ev)

    with open(ICS_PATH, "wb") as f:
        f.write(cal.to_ical())

    print(f"✅ Calendario ICS compatible generado: {ICS_PATH}")
