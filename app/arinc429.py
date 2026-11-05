from dataclasses import dataclass


@dataclass(frozen=True)
class PalabraArinc429:
    valor: int

    @property
    def hexadecimal(self) -> str:
        return f"{self.valor:08X}"

    @property
    def bytes_serial(self) -> bytes:
        # Convención de este proyecto: palabra de 32 bits transmitida little-endian.
        # El adaptador externo debe convertirla a la señalización física ARINC 429.
        return self.valor.to_bytes(4, byteorder="little", signed=False)


def _reverse_8_bits(value: int) -> int:
    return int(f"{value:08b}"[::-1], 2)


def generar_palabra_bnr(
    *, etiqueta_octal: str, valor: float, escala_lsb: float, sdi: int = 0, ssm: int = 0
) -> PalabraArinc429:
    """Codifica un dato BNR de ejemplo con signo-magnitud y paridad impar.

    La etiqueta se recibe en octal y se invierten sus bits para el orden ARINC.
    Bits: etiqueta 1-8, SDI 9-10, datos BNR 11-29, SSM 30-31, paridad impar 32.
    La escala/unidades y el formato BNR deben confirmarse contra la definición
    específica del equipo antes de conectar hardware real.
    """
    if not etiqueta_octal or any(digit not in "01234567" for digit in etiqueta_octal):
        raise ValueError("La etiqueta ARINC debe ser un número octal")
    etiqueta = int(etiqueta_octal, 8)
    if etiqueta > 0xFF:
        raise ValueError("La etiqueta ARINC debe caber en 8 bits")
    if escala_lsb <= 0:
        raise ValueError("escala_lsb debe ser mayor que cero")
    if not 0 <= sdi <= 3 or not 0 <= ssm <= 3:
        raise ValueError("SDI y SSM deben estar entre 0 y 3")

    magnitud = round(abs(valor) / escala_lsb)
    if magnitud > 0x3FFFF:
        raise ValueError("El valor excede los 18 bits de magnitud BNR")

    datos = magnitud | ((1 if valor < 0 else 0) << 18)
    palabra = _reverse_8_bits(etiqueta) | (sdi << 8) | (datos << 10) | (ssm << 29)
    # El número total de bits de la palabra, incluyendo el bit de paridad, debe ser impar.
    if palabra.bit_count() % 2 == 0:
        palabra |= 1 << 31
    return PalabraArinc429(palabra)
