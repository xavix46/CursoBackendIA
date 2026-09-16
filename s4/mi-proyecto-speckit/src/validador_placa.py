"""Validador de formato de placa vehicular para el sistema de matriculación.

Basado en la normativa de la Agencia Nacional de Tránsito (ANT) del Ecuador
y la especificación definida en spec_manual.md:
- 3 letras y 4 números.
- Primera letra: Identifica la provincia de matriculación (24 provincias oficiales).
- Segunda letra: Identifica el tipo de servicio (particular, público/comercial, gubernamental, GAD, oficial).
- Tercera letra: Correlativo alfanumérico.
- 4 dígitos numéricos finales.
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import asdict, dataclass
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

    def to_dict(self) -> dict[str, Any]:
        """Convierte el resultado a diccionario serializable."""
        return asdict(self)


# Expresión regular para estructura reglamentaria: 3 letras, separador opcional (- o espacio), 4 números
PATRON_PLACA_3L_4N = re.compile(r"^([A-Za-z]{3})[\s\-]?(\d{4})$")

# Expresión regular para detectar placas del formato antiguo (3 letras y 3 números)
PATRON_PLACA_3L_3N = re.compile(r"^([A-Za-z]{3})[\s\-]?(\d{3})$")


def _diagnosticar_error_formato(placa_original: str, placa_upper: str) -> ResultadoValidacion:
    """Genera un mensaje de diagnóstico detallado cuando no coincide con 3 letras y 4 dígitos."""
    caracteres_solo = re.sub(r"[\s\-]", "", placa_upper)

    if not caracteres_solo.isalnum():
        return ResultadoValidacion(
            es_valida=False,
            placa_original=placa_original,
            mensaje="Formato no válido: La placa contiene caracteres especiales o símbolos no permitidos.",
        )

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


def validar_placa(placa: Any) -> ResultadoValidacion:
    """Valida si una placa vehicular cumple con el formato ANT Ecuador de 3 letras y 4 números."""
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

    match = PATRON_PLACA_3L_4N.match(placa_upper)

    if not match:
        return _diagnosticar_error_formato(placa, placa_upper)

    letras, numeros = match.groups()
    primera_letra = letras[0]
    segunda_letra = letras[1]
    tercera_letra = letras[2]

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

    provincia = PROVINCIAS_ECUADOR[primera_letra]
    tipo_servicio = SERVICIOS_SEGUNDA_LETRA.get(segunda_letra, "Particular / Privado")
    placa_normalizada = f"{letras}-{numeros}"

    return ResultadoValidacion(
        es_valida=True,
        placa_original=placa,
        placa_normalizada=placa_normalizada,
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


def main() -> None:
    """Punto de entrada para ejecución desde línea de comandos (CLI)."""
    raw_args = sys.argv[1:]
    json_mode = "--json" in raw_args
    args = [a for a in raw_args if a != "--json"]

    placas_a_evaluar = args if args else [
        "PBX-1234",     # Válida (Pichincha, particular)
        "pba-4567",     # Válida minúsculas (Pichincha, comercial/público)
        "GYA 9876",     # Válida con espacio (Guayas, comercial/público)
        "ABC1234",      # Válida sin guión (Azuay)
        "DFG-1234",     # Inválida (letra D no es provincia)
        "PBX-123",      # Inválida (3 números, formato antiguo)
        "PBX-12345",    # Inválida (5 números)
        "",             # Inválida (vacía)
    ]

    resultados = [validar_placa(p) for p in placas_a_evaluar]

    if json_mode:
        print(json.dumps([r.to_dict() for r in resultados], indent=2, ensure_ascii=False))
        return

    print("=" * 65)
    print("  VALIDADOR DE PLACAS VEHICULARES (ANT - ECUADOR)  ")
    print("=" * 65)

    for r in resultados:
        print(f"\nEntrada: '{r.placa_original}'")
        print(r)
        print("-" * 65)


if __name__ == "__main__":
    main()
