import csv


def leer_csv(ruta):
    """Lee un CSV y devuelve una lista de diccionarios, uno por fila."""
    with open(ruta, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))