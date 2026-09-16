"""Suite de pruebas unitarias para el validador de placas vehiculares (ANT Ecuador)."""

import unittest
from src.validador_placa import (
    ResultadoValidacion,
    PROVINCIAS_ECUADOR,
    SERVICIOS_SEGUNDA_LETRA,
    validar_placa,
)


class TestValidadorPlacas(unittest.TestCase):
    """Pruebas para validador_placa según especificación y normativa ANT."""

    def test_fundacional_catalogos_y_dataclass(self):
        """Verifica que los catálogos y dataclass base estén correctamente inicializados."""
        self.assertEqual(len(PROVINCIAS_ECUADOR), 24)
        self.assertNotIn("D", PROVINCIAS_ECUADOR)
        self.assertNotIn("F", PROVINCIAS_ECUADOR)
        self.assertEqual(PROVINCIAS_ECUADOR["P"], "Pichincha")
        self.assertEqual(PROVINCIAS_ECUADOR["G"], "Guayas")

        res = ResultadoValidacion(es_valida=True, placa_original="PBX-1234", placa_normalizada="PBX-1234")
        self.assertTrue(res.es_valida)
        self.assertEqual(res.placa_normalizada, "PBX-1234")

    # --- FASE 3: USER STORY 1 (MVP) ---

    def test_placa_valida_con_guion(self):
        """Placa estándar con guión y letras mayúsculas."""
        res = validar_placa("PBX-1234")
        self.assertTrue(res.es_valida)
        self.assertEqual(res.placa_normalizada, "PBX-1234")

    def test_placa_valida_sin_separador(self):
        """Placa sin guión ni espacio."""
        res = validar_placa("ABC1234")
        self.assertTrue(res.es_valida)
        self.assertEqual(res.placa_normalizada, "ABC-1234")

    def test_placa_valida_con_espacio(self):
        """Placa con espacio como separador."""
        res = validar_placa("GYB 4567")
        self.assertTrue(res.es_valida)
        self.assertEqual(res.placa_normalizada, "GYB-4567")

    def test_placa_valida_minusculas(self):
        """Placa en minúsculas se normaliza a mayúsculas."""
        res = validar_placa("pbx-1234")
        self.assertTrue(res.es_valida)
        self.assertEqual(res.placa_normalizada, "PBX-1234")

    def test_placa_valida_con_espacios_alrededor(self):
        """Placa con espacios en blanco al inicio o al final."""
        res = validar_placa("   PBX-1234   ")
        self.assertTrue(res.es_valida)
        self.assertEqual(res.placa_normalizada, "PBX-1234")

    def test_placa_valida_ceros_a_la_izquierda(self):
        """Placa con 4 dígitos que empiezan con ceros."""
        res = validar_placa("PBX-0001")
        self.assertTrue(res.es_valida)
        self.assertEqual(res.placa_normalizada, "PBX-0001")

    # --- FASE 4: USER STORY 2 (Provincias y Servicios) ---

    def test_deteccion_todas_las_24_provincias(self):
        """Verifica que las 24 provincias reconocidas por la ANT sean aceptadas."""
        provincias_prueba = [
            ("A", "Azuay"), ("B", "Bolívar"), ("C", "Carchi"), ("E", "Esmeraldas"),
            ("G", "Guayas"), ("H", "Chimborazo"), ("I", "Imbabura"), ("J", "Santo Domingo de los Tsáchilas"),
            ("K", "Sucumbíos"), ("L", "Loja"), ("M", "Manabí"), ("N", "Napo"),
            ("O", "El Oro"), ("P", "Pichincha"), ("Q", "Orellana"), ("R", "Los Ríos"),
            ("S", "Pastaza"), ("T", "Tungurahua"), ("U", "Cañar"), ("V", "Morona Santiago"),
            ("W", "Galápagos"), ("X", "Cotopaxi"), ("Y", "Santa Elena"), ("Z", "Zamora Chinchipe"),
        ]
        for codigo, nombre in provincias_prueba:
            placa = f"{codigo}BX-1000"
            res = validar_placa(placa)
            self.assertTrue(res.es_valida, f"Falló provincia {codigo} ({nombre})")
            self.assertEqual(res.provincia, nombre)
            self.assertIsNotNone(res.detalles)
            self.assertEqual(res.detalles.get("codigo_provincia"), codigo)

    def test_deteccion_tipo_servicio_publico(self):
        """Verifica detección de servicio comercial/público (segunda letra A, U, Z)."""
        for letra in ("A", "U", "Z"):
            res = validar_placa(f"P{letra}X-1234")
            self.assertTrue(res.es_valida)
            self.assertIn("Público", res.tipo_servicio)

    def test_deteccion_tipo_servicio_gobierno_y_gad(self):
        """Verifica detección de servicio gubernamental (E) y GAD (M)."""
        res_e = validar_placa("PEX-1234")
        self.assertTrue(res_e.es_valida)
        self.assertIn("Gubernamental", res_e.tipo_servicio)

        res_m = validar_placa("PMX-1234")
        self.assertTrue(res_m.es_valida)
        self.assertIn("Gobiernos Autónomos", res_m.tipo_servicio)

    def test_deteccion_tipo_servicio_particular(self):
        """Segunda letra distinta de servicios especiales corresponde a Particular / Privado."""
        res = validar_placa("PBX-1234")
        self.assertTrue(res.es_valida)
        self.assertEqual(res.tipo_servicio, "Particular / Privado")

    # --- FASE 5: USER STORY 3 (Diagnóstico de Entradas Inválidas) ---

    def test_primera_letra_invalida_d_o_f(self):
        """La primera letra 'D' o 'F' no son provincias válidas en la ANT."""
        res_d = validar_placa("DFG-1234")
        self.assertFalse(res_d.es_valida)
        self.assertIn("no corresponde a ninguna provincia", res_d.mensaje)

        res_f = validar_placa("FAA-1234")
        self.assertFalse(res_f.es_valida)
        self.assertIn("no corresponde a ninguna provincia", res_f.mensaje)

    def test_placas_con_caracteres_especiales(self):
        """Entradas con símbolos inválidos son rechazadas con mensaje específico."""
        res = validar_placa("PBX-12@4")
        self.assertFalse(res.es_valida)
        self.assertIn("caracteres especiales", res.mensaje)

    def test_exceso_o_defecto_de_caracteres(self):
        """Estructura con conteo de letras o dígitos incorrecto."""
        res_largo = validar_placa("PBX-12345")
        self.assertFalse(res_largo.es_valida)
        self.assertIn("Estructura inválida", res_largo.mensaje)

        res_corto = validar_placa("PB-1234")
        self.assertFalse(res_corto.es_valida)
        self.assertIn("Estructura inválida", res_corto.mensaje)

    def test_tipo_de_dato_incorrecto(self):
        """Paso de enteros, flotantes, listas o diccionarios."""
        res = validar_placa(1234567)
        self.assertFalse(res.es_valida)
        self.assertIn("Tipo de dato no soportado", res.mensaje)

    # --- FASE 6: USER STORY 4 (Formato Histórico 3 Números) ---

    def test_placa_formato_antiguo_3_numeros(self):
        """Placa con formato histórico de 3 números (rechazada con mensaje específico orientativo)."""
        res = validar_placa("PBX-123")
        self.assertFalse(res.es_valida)
        self.assertIn("formato antiguo", res.mensaje)
        self.assertEqual(res.placa_normalizada, "PBX-123")

    # --- FASE 7: USER STORY 5 (Entradas Vacías o Nulas) ---

    def test_cadena_vacia_o_solo_espacios(self):
        """Entrada vacía o compuesta únicamente por espacios en blanco."""
        res_vacia = validar_placa("")
        self.assertFalse(res_vacia.es_valida)
        self.assertIn("vacía", res_vacia.mensaje)

        res_espacios = validar_placa("    ")
        self.assertFalse(res_espacios.es_valida)
        self.assertIn("vacía", res_espacios.mensaje)

    def test_entrada_nula_none(self):
        """Paso de valor nulo (None)."""
        res = validar_placa(None)
        self.assertFalse(res.es_valida)
        self.assertIn("None", res.mensaje)


if __name__ == "__main__":
    unittest.main()
