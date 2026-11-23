from elasticsearch import helpers

INDICE = "ventas"

MAPPING = {
    "properties": {
        "venta_id": {"type": "keyword"},
        "fecha": {"type": "date"},
        "producto": {"type": "text", "fields": {"raw": {"type": "keyword"}}},
        "categoria_codigo": {"type": "keyword"},
        "categoria_nombre": {"type": "keyword"},
        "cantidad": {"type": "integer"},
        "precio_unitario": {"type": "float"},
        "descuento": {"type": "float"},
        "total": {"type": "float"},
        "region": {"type": "keyword"},
    }
}


def crear_indice(es, indice=INDICE):
    """Crea el índice con su mapping solo si no existe."""
    if not es.indices.exists(index=indice):
        es.indices.create(index=indice, mappings=MAPPING)


def cargar(es, documentos, indice=INDICE):
    """Indexa los documentos usando venta_id como _id (idempotente)."""
    acciones = (
        {"_index": indice, "_id": d["venta_id"], "_source": d}
        for d in documentos
    )
    exitosos, fallidos = helpers.bulk(es, acciones, raise_on_error=False, stats_only=True)
    es.indices.refresh(index=indice)
    return exitosos, fallidos