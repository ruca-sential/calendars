import os
from datetime import datetime, timedelta
from icalendar import Calendar, Event
import uuid

DROPBOX_FOLDER = r"C:\Users\TuUsuario\Dropbox\Calendarios"
ICS_FILENAME = "virgen_europa.ics"
ICS_PATH = os.path.join(DROPBOX_FOLDER, ICS_FILENAME)

def crear_evento(partido):
    event = Event()
    fecha = partido["fecha"]
    hora = partido["hora"]

    if fecha:
        if hora:
            dtstart = datetime.strptime(f"{fecha} {hora}", "%d/%m/%Y %H:%M")
            dtend = dtstart + timedelta(hours=1)  # duración estimada 1 h
            event.add("dtstart", dtstart)
            event.add("dtend", dtend)
        else:
            # Evento de todo el día
            dt = datetime.strptime(fecha, "%d/%m/%Y").date()
            event.add("dtstart", dt, parameters={"VALUE": "DATE"})
            event.add("dtend", (dt + timedelta(days=1)), parameters={"VALUE": "DATE"})

    summary = f"{partido['local']} vs {partido['visitante']}"
    event.add("summary", summary)

    if partido["lugar"]:
        event.add("location", partido["lugar"])
    if partido["enlace_lugar"]:
        event.add("url", partido["enlace_lugar"])

    # Campos obligatorios para Google Calendar
    event.add("uid", str(uuid.uuid4()) + "@virgen_europa")
    event.add("dtstamp", datetime.utcnow())

    return event

def guardar_calendario(partidos):
    cal = Calendar()
    cal.add("prodid", "-//Calendario Balonmano Virgen de Europa//")
    cal.add("version", "2.0")

    for partido in partidos:
        event = crear_evento(partido)
        cal.add_component(event)

    with open(ICS_PATH, "wb") as f:
        f.write(cal.to_ical())

    print(f"✅ Archivo ICS guardado correctamente en: {ICS_PATH}")

