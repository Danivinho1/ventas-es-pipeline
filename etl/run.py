import csv
from pathlib import Path

from elasticsearch import Elasticsearch

from etl.extract import leer_csv
from etl.load import cargar, crear_indice
from etl.transform import cargar_categorias, transformar

DATA = Path(__file__).resolve().parent.parent / "data"


def escribir_rechazados(rechazados, ruta):
    if not rechazados:
        print("Sin filas rechazadas.")
        return
    campos = ["linea", "motivo"] + list(rechazados[0]["datos"].keys())
    with open(ruta, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=campos)
        writer.writeheader()
        for r in rechazados:
            writer.writerow({"linea": r["linea"], "motivo": r["motivo"], **r["datos"]})


def main():
    es = Elasticsearch("http://localhost:9200")

    categorias = cargar_categorias(leer_csv(DATA / "categorias.csv"))  # E
    filas = leer_csv(DATA / "ventas.csv")                               # E
    validos, rechazados = transformar(filas, categorias)                # T

    crear_indice(es)
    indexados, fallidos = cargar(es, validos)                           # L
    escribir_rechazados(rechazados, DATA / "rechazados.csv")

    print(
        f"Leídas: {len(filas)} | Indexadas: {indexados} | "
        f"Rechazadas: {len(rechazados)} | Fallidas en ES: {fallidos}"
    )


if __name__ == "__main__":
    main()