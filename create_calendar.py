from extract import get_partidos
from store import guardar_calendario

def main():
    print("Obteniendo partidos...")
    partidos = get_partidos()
    print(f"Se han extraído {len(partidos)} partidos")
    guardar_calendario(partidos)
    print("Calendario actualizado correctamente")

if __name__ == "__main__":
    main()
