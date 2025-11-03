import argparse


from extract import get_partidos
from store import guardar_calendario_seguro


def arg_read():
    parser = argparse.ArgumentParser(description='Parser de la web de la FMBM para obtener el calendario.')
    parser.add_argument('--team', type=str, default='VIRGEN DE EUROPA', help='Nombre del equipo a filtrar')
    parser.add_argument('--cat', type=str, default='3TM', help='Categoria en la que buscar ("2TM or 3TM)')
    return parser.parse_args()

def main():
    args = arg_read()
    print(f"Obteniendo partidos usando el filtro: {args.team} in {args.cat}")
    partidos = get_partidos(args.cat, args.team.lower())
    print(f"Se han extraído {len(partidos)} partidos")
    guardar_calendario_seguro(partidos, f"{args.cat}-{args.team.lower()}")
    print("Calendario actualizado correctamente")

if __name__ == "__main__":
    main()
