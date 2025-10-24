import os
from datetime import datetime, date
from icalendar import Calendar, Event

DROPBOX_FOLDER = r"C:\Users\gabri\Dropbox\Calendarios\Balonmano"
ICS_FILENAME = "virgen_europa.ics"
ICS_PATH = os.path.join(DROPBOX_FOLDER, ICS_FILENAME)

def crear_evento(partido):
    """Crea un evento de iCalendar a partir de un dict de partido"""
    event = Event()
    fecha = partido["fecha"]
    hora = partido["hora"]
    if fecha:
        if hora:
            dt = datetime.strptime(f"{fecha} {hora}", "%d/%m/%Y %H:%M")
            event.add("dtstart", dt)
        else:
            dt = datetime.strptime(fecha, "%d/%m/%Y").date()
            event.add("dtstart", dt)
            event.add("dtend", dt)
            event.add('X-MICROSOFT-CDO-ALLDAYEVENT', 'TRUE')
    summary = f"{partido['local']} vs {partido['visitante']}"
    event.add("summary", summary)
    if partido["lugar"]:
        event.add("location", partido["lugar"])
        if partido["enlace_lugar"]:
            event.add("description", f"Ubicación en Google Maps: {partido['enlace_lugar']}")
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
    print(f"Archivo ICS guardado en: {ICS_PATH}")
