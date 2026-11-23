from etl.transform import transformar, validar_fila

CATS = {"COM": "Computo", "ACC": "Accesorios"}

BASE = {
    "venta_id": "V1",
    "fecha": "2026-01-05",
    "producto": "Laptop",
    "categoria_codigo": "com",
    "cantidad": "2",
    "precio_unitario": "100",
    "descuento": "10",
    "region": "Norte",
}


def test_fila_valida_calcula_total_y_enriquece():
    doc, motivo = validar_fila(BASE, CATS)
    assert motivo is None
    assert doc["total"] == 180.0
    assert doc["categoria_codigo"] == "COM"
    assert doc["categoria_nombre"] == "Computo"
    assert doc["region"] == "norte"


def test_descuento_fuera_de_rango_se_rechaza():
    doc, motivo = validar_fila({**BASE, "descuento": "150"}, CATS)
    assert doc is None
    assert "descuento" in motivo


def test_cantidad_negativa_se_rechaza():
    doc, motivo = validar_fila({**BASE, "cantidad": "-1"}, CATS)
    assert doc is None
    assert "cantidad" in motivo


def test_fecha_inexistente_se_rechaza():
    doc, motivo = validar_fila({**BASE, "fecha": "2026-02-30"}, CATS)
    assert doc is None
    assert "fecha" in motivo


def test_categoria_desconocida_se_rechaza():
    doc, motivo = validar_fila({**BASE, "categoria_codigo": "XYZ"}, CATS)
    assert doc is None
    assert "desconocida" in motivo


def test_campo_obligatorio_vacio_se_rechaza():
    doc, motivo = validar_fila({**BASE, "producto": "  "}, CATS)
    assert doc is None
    assert "producto" in motivo


def test_venta_duplicada_se_rechaza():
    validos, rechazados = transformar([BASE, BASE], CATS)
    assert len(validos) == 1
    assert len(rechazados) == 1
    assert rechazados[0]["motivo"] == "venta_id duplicado"