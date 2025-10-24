import os
from datetime import datetime
from icalendar import Calendar, Event

# Carpeta de Dropbox sincronizada
DROPBOX_FOLDER = r"C:\Users\TuUsuario\Dropbox\Calendarios"
ICS_FILENAME = "virgen_europa.ics"
ICS_PATH = os.path.join(DROPBOX_FOLDER, ICS_FILENAME)

def crear_evento(fecha, hora, local, visitante, lugar, enlace_lugar=None):
    """Crea un evento de iCalendar"""
    event = Event()
    if fecha:
        if hora and hora != "0:00":
            dt = datetime.strptime(f"{fecha} {hora}", "%d/%m/%Y %H:%M")
            event.add('dtstart', dt)
        else:
            # Todo el día
            dt = datetime.strptime(fecha, "%d/%m/%Y").date()
            event.add('dtstart', dt)
            event.add('dtend', dt)
            event.add('X-MICROSOFT-CDO-ALLDAYEVENT', 'TRUE')
    event.add('summary', f"{local} vs {visitante}")
    if lugar:
        event.add('location', lugar)
        if enlace_lugar:
            event.add('description', f"Ubicación en Google Maps: {enlace_lugar}")
    return event

def guardar_calendario(eventos):
    """Genera y guarda el .ics en Dropbox"""
    cal = Calendar()
    cal.add('prodid', '-//Calendario Balonmano Virgen de Europa//')
    cal.add('version', '2.0')
    for e in eventos:
        cal.add_component(e)
    with open(ICS_PATH, 'wb') as f:
        f.write(cal.to_ical())
    print(f"Archivo ICS guardado en {ICS_PATH}")

# Ejemplo de uso con eventos ficticios
eventos = [
    crear_evento("05/10/2025", "12:00", "CLUB BALONMANO CHINCHON", "CB PARLA", "PM CHINCHON", "https://www.google.com/maps/?q=40.1393574,-3.4145528"),
    crear_evento("05/10/2025", "0:00", "VIRGEN DE EUROPA", "G MADRID PEDRO ZEROLO", "COL. VIRGEN DE EUROPA PABELLON", "https://www.google.com/maps/?q=40.123456,-3.654321")
]

guardar_calendario(eventos)
