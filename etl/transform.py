from datetime import datetime

CAMPOS_OBLIGATORIOS = [
    "venta_id", "fecha", "producto", "categoria_codigo",
    "cantidad", "precio_unitario", "region",
]


def cargar_categorias(filas):
    """Convierte las filas de categorías en un diccionario {codigo: nombre}."""
    return {f["codigo"].strip().upper(): f["nombre"].strip() for f in filas}


def validar_fila(fila, categorias):
    """Valida y transforma una fila. Devuelve (documento, None) o (None, motivo)."""
    for campo in CAMPOS_OBLIGATORIOS:
        if not (fila.get(campo) or "").strip():
            return None, f"campo obligatorio vacío: {campo}"

    try:
        fecha = datetime.strptime(fila["fecha"].strip(), "%Y-%m-%d").date().isoformat()
    except ValueError:
        return None, "fecha inválida (use AAAA-MM-DD)"

    try:
        cantidad = int(fila["cantidad"])
        precio = float(fila["precio_unitario"])
        descuento = float(fila.get("descuento") or 0)
    except ValueError:
        return None, "cantidad, precio o descuento no numérico"

    if cantidad <= 0:
        return None, "cantidad debe ser mayor a 0"
    if precio < 0:
        return None, "precio no puede ser negativo"
    if not 0 <= descuento <= 100:
        return None, "descuento fuera de rango 0-100"

    codigo = fila["categoria_codigo"].strip().upper()
    if codigo not in categorias:
        return None, f"categoría desconocida: {codigo}"

    total = round(cantidad * precio * (1 - descuento / 100), 2)

    doc = {
        "venta_id": fila["venta_id"].strip(),
        "fecha": fecha,
        "producto": fila["producto"].strip(),
        "categoria_codigo": codigo,
        "categoria_nombre": categorias[codigo],  # enriquecimiento
        "cantidad": cantidad,
        "precio_unitario": precio,
        "descuento": descuento,
        "total": total,
        "region": fila["region"].strip().lower(),
    }
    return doc, None


def transformar(filas, categorias):
    """Devuelve (validos, rechazados). Rechaza filas inválidas y venta_id duplicados."""
    validos, rechazados, ids_vistos = [], [], set()
    for numero_linea, fila in enumerate(filas, start=2):  # la línea 1 es el encabezado
        doc, motivo = validar_fila(fila, categorias)
        if doc is None:
            rechazados.append({"linea": numero_linea, "motivo": motivo, "datos": fila})
            continue
        if doc["venta_id"] in ids_vistos:
            rechazados.append({"linea": numero_linea, "motivo": "venta_id duplicado", "datos": fila})
            continue
        ids_vistos.add(doc["venta_id"])
        validos.append(doc)
    return validos, rechazados