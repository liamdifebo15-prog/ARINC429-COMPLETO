import pytest

from app.arinc429 import generar_palabra_bnr


def test_palabra_es_de_32_bits_y_paridad_impar():
    palabra = generar_palabra_bnr(etiqueta_octal="203", valor=125.0, escala_lsb=1.0)
    assert 0 <= palabra.valor < 2**32
    assert palabra.valor.bit_count() % 2 == 1
    assert len(palabra.bytes_serial) == 4
    assert len(palabra.hexadecimal) == 8


def test_escala_y_signo_cambian_la_palabra():
    positiva = generar_palabra_bnr(etiqueta_octal="203", valor=25.0, escala_lsb=0.5)
    negativa = generar_palabra_bnr(etiqueta_octal="203", valor=-25.0, escala_lsb=0.5)
    assert positiva.valor != negativa.valor
    assert positiva.valor.bit_count() % 2 == negativa.valor.bit_count() % 2 == 1


@pytest.mark.parametrize("etiqueta", ["", "999", "20x"])
def test_etiqueta_octal_invalida(etiqueta: str):
    with pytest.raises(ValueError):
        generar_palabra_bnr(etiqueta_octal=etiqueta, valor=1, escala_lsb=1)


def test_rechaza_escala_no_positiva():
    with pytest.raises(ValueError):
        generar_palabra_bnr(etiqueta_octal="203", valor=1, escala_lsb=0)
