"""Validador de formato de placa vehicular para el sistema de matriculación.

Basado en la normativa de la Agencia Nacional de Tránsito (ANT) del Ecuador
y la especificación definida en spec_manual.md:
- 3 letras y 4 números.
- Primera letra: Identifica la provincia de matriculación.
- Segunda letra: Identifica el tipo de servicio (particular, público/comercial, gubernamental, GAD, oficial).
- Tercera letra: Correlativo alfanumérico.
- 4 dígitos numéricos finales.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any


# Mapeo oficial de la primera letra a la provincia según la ANT (Ecuador)
PROVINCIAS_ECUADOR: dict[str, str] = {
    "A": "Azuay",
    "B": "Bolívar",
    "C": "Carchi",
    "E": "Esmeraldas",
    "G": "Guayas",
    "H": "Chimborazo",
    "I": "Imbabura",
    "J": "Santo Domingo de los Tsáchilas",
    "K": "Sucumbíos",
    "L": "Loja",
    "M": "Manabí",
    "N": "Napo",
    "O": "El Oro",
    "P": "Pichincha",
    "Q": "Orellana",
    "R": "Los Ríos",
    "S": "Pastaza",
    "T": "Tungurahua",
    "U": "Cañar",
    "V": "Morona Santiago",
    "W": "Galápagos",
    "X": "Cotopaxi",
    "Y": "Santa Elena",
    "Z": "Zamora Chinchipe",
}

# Clasificación de la segunda letra según el tipo de servicio/uso (ANT)
SERVICIOS_SEGUNDA_LETRA: dict[str, str] = {
    "A": "Público / Comercial (transporte, buses, taxis)",
    "U": "Público / Comercial (transporte, buses, taxis)",
    "Z": "Público / Comercial (transporte, buses, taxis)",
    "E": "Gubernamental (Gobierno Central)",
    "M": "Gobiernos Autónomos Descentralizados (GAD provincial o municipal)",
    "X": "Uso Oficial del Estado",
}


@dataclass
class ResultadoValidacion:
    """Representa el resultado de validar una placa vehicular."""

    es_valida: bool
    placa_original: str
    placa_normalizada: str | None = None
    provincia: str | None = None
    tipo_servicio: str | None = None
    mensaje: str = ""
    detalles: dict[str, Any] | None = None

    def __str__(self) -> str:
        estado = "VÁLIDA" if self.es_valida else "INVÁLIDA"
        lineas = [f"[{estado}] {self.mensaje}"]
        if self.es_valida:
            lineas.append(f"  - Placa normalizada: {self.placa_normalizada}")
            lineas.append(f"  - Provincia: {self.provincia}")
            lineas.append(f"  - Tipo de servicio: {self.tipo_servicio}")
        return "\n".join(lineas)


# Expresión regular para estructura: 3 letras, separador opcional (- o espacio), 4 números
PATRON_PLACA_3L_4N = re.compile(r"^([A-Za-z]{3})[\s\-]?(\d{4})$")

# Expresión regular para detectar placas del formato antiguo (3 letras y 3 números)
PATRON_PLACA_3L_3N = re.compile(r"^([A-Za-z]{3})[\s\-]?(\d{3})$")


def validar_placa(placa: Any) -> ResultadoValidacion:
    """Valida si una placa vehicular cumple con el formato ANT Ecuador de 3 letras y 4 números.

    Args:
        placa: Cadena con la placa vehicular (ej. 'PBX-1234', 'PBX 1234', 'PBX1234').

    Returns:
        ResultadoValidacion con el estado, normalización, provincia y mensaje explicativo.
    """
    if placa is None:
        return ResultadoValidacion(
            es_valida=False,
            placa_original="",
            mensaje="Error: La placa ingresada es nula (None). Se requiere un valor de texto.",
        )

    if not isinstance(placa, str):
        return ResultadoValidacion(
            es_valida=False,
            placa_original=str(placa),
            mensaje=f"Error: Tipo de dato no soportado ({type(placa).__name__}). Debe ser una cadena de texto.",
        )

    placa_limpia = placa.strip()
    if not placa_limpia:
        return ResultadoValidacion(
            es_valida=False,
            placa_original=placa,
            mensaje="Error: La placa ingresada está vacía.",
        )

    # Convertir a mayúsculas para normalizar
    placa_upper = placa_limpia.upper()

    # Detección de formato antiguo (3 letras y 3 números)
    match_antiguo = PATRON_PLACA_3L_3N.match(placa_upper)
    if match_antiguo:
        return ResultadoValidacion(
            es_valida=False,
            placa_original=placa,
            placa_normalizada=f"{match_antiguo.group(1)}-{match_antiguo.group(2)}",
            mensaje=(
                "Formato no aceptado: La placa tiene 3 números (formato antiguo). "
                "El criterio de aceptación exige 3 letras y 4 números (ejemplo: ABC-1234)."
            ),
        )

    # Comprobación de patrón general (3 letras y 4 números)
    match = PATRON_PLACA_3L_4N.match(placa_upper)
    if not match:
        # Analizar causas específicas de error para dar mensajes claros
        return _diagnosticar_error_formato(placa, placa_upper)

    letras, numeros = match.groups()
    primera_letra = letras[0]
    segunda_letra = letras[1]
    tercera_letra = letras[2]

    # Validar que la primera letra pertenezca a una provincia de Ecuador
    if primera_letra not in PROVINCIAS_ECUADOR:
        return ResultadoValidacion(
            es_valida=False,
            placa_original=placa,
            placa_normalizada=f"{letras}-{numeros}",
            mensaje=(
                f"Formato no válido: La primera letra '{primera_letra}' no corresponde "
                "a ninguna provincia del Ecuador reconocida por la Agencia Nacional de Tránsito (ANT)."
            ),
        )

    # Determinar provincia y tipo de servicio
    provincia = PROVINCIAS_ECUADOR[primera_letra]
    tipo_servicio = SERVICIOS_SEGUNDA_LETRA.get(segunda_letra, "Particular / Privado")

    placa_estandarizada = f"{letras}-{numeros}"

    return ResultadoValidacion(
        es_valida=True,
        placa_original=placa,
        placa_normalizada=placa_estandarizada,
        provincia=provincia,
        tipo_servicio=tipo_servicio,
        mensaje=f"Placa válida para la provincia de {provincia} ({tipo_servicio}).",
        detalles={
            "provincia": provincia,
            "codigo_provincia": primera_letra,
            "segunda_letra": segunda_letra,
            "tercera_letra": tercera_letra,
            "correlativo_numerico": numeros,
            "servicio": tipo_servicio,
        },
    )


def _diagnosticar_error_formato(placa_original: str, placa_upper: str) -> ResultadoValidacion:
    """Genera un mensaje de diagnóstico detallado cuando no coincide con 3 letras y 4 dígitos."""
    # Eliminar posibles guiones o espacios
    caracteres_solo = re.sub(r"[\s\-]", "", placa_upper)

    if not caracteres_solo.isalnum():
        return ResultadoValidacion(
            es_valida=False,
            placa_original=placa_original,
            mensaje="Formato no válido: La placa contiene caracteres especiales o símbolos no permitidos.",
        )

    # Contar letras iniciales y dígitos
    match_letras = re.match(r"^([A-Za-z]+)", caracteres_solo)
    cant_letras = len(match_letras.group(1)) if match_letras else 0

    match_digitos = re.search(r"(\d+)$", caracteres_solo)
    cant_digitos = len(match_digitos.group(1)) if match_digitos else 0

    if cant_letras != 3 or cant_digitos != 4 or len(caracteres_solo) != 7:
        return ResultadoValidacion(
            es_valida=False,
            placa_original=placa_original,
            mensaje=(
                f"Estructura inválida: Se detectaron {cant_letras} letra(s) y {cant_digitos} dígito(s). "
                "El formato exigido por la ANT es de 3 letras seguidas de 4 números (ejemplo: ABC-1234)."
            ),
        )

    return ResultadoValidacion(
        es_valida=False,
        placa_original=placa_original,
        mensaje="Formato no válido: No cumple con la estructura requerida (3 letras y 4 números).",
    )


def main() -> None:
    """Función de entrada para pruebas rápidas desde terminal."""
    import sys

    placas_ejemplo = sys.argv[1:] if len(sys.argv) > 1 else [
        "PBX-1234",     # Válida (Pichincha, particular)
        "pba-4567",     # Válida minúsculas (Pichincha, comercial/público)
        "GYA 9876",     # Válida con espacio (Guayas, comercial/público)
        "ABC1234",      # Válida sin guión (Azuay)
        "DFG-1234",     # Inválida (letra D no es provincia)
        "PBX-123",      # Inválida (3 números, formato antiguo)
        "PBX-12345",    # Inválida (5 números)
        "",             # Inválida (vacía)
    ]

    print("=" * 65)
    print("  VALIDADOR DE PLACAS VEHICULARES (ANT - ECUADOR)  ")
    print("=" * 65)

    for p in placas_ejemplo:
        res = validar_placa(p)
        print(f"\nEntrada: '{p}'")
        print(res)
        print("-" * 65)


if __name__ == "__main__":
    main()
