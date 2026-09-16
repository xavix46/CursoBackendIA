"""Suite de pruebas unitarias para el validador de placas vehiculares (ANT Ecuador)."""

import unittest
from validador_placa import validar_placa, ResultadoValidacion


class TestValidadorPlacas(unittest.TestCase):
    """Pruebas para validar_placa según spec_manual.md y normativa ANT."""

    # --- 1. CASOS NORMALES ---

    def test_placa_valida_con_guion(self):
        """Placa estándar con guión y letras mayúsculas."""
        res = validar_placa("PBX-1234")
        self.assertTrue(res.es_valida)
        self.assertEqual(res.placa_normalizada, "PBX-1234")
        self.assertEqual(res.provincia, "Pichincha")

    def test_placa_valida_sin_separador(self):
        """Placa sin guión ni espacio."""
        res = validar_placa("ABC1234")
        self.assertTrue(res.es_valida)
        self.assertEqual(res.placa_normalizada, "ABC-1234")
        self.assertEqual(res.provincia, "Azuay")

    def test_placa_valida_con_espacio(self):
        """Placa con espacio como separador."""
        res = validar_placa("GYB 4567")
        self.assertTrue(res.es_valida)
        self.assertEqual(res.placa_normalizada, "GYB-4567")
        self.assertEqual(res.provincia, "Guayas")

    def test_placa_valida_todas_las_provincias(self):
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
            placa = f"{codigo}AA-1000"
            res = validar_placa(placa)
            self.assertTrue(res.es_valida, f"Falló provincia {codigo} ({nombre})")
            self.assertEqual(res.provincia, nombre)

    def test_deteccion_tipo_servicio_publico(self):
        """Verifica detección de servicio comercial/público (segunda letra A, U, Z)."""
        res_a = validar_placa("PAA-1234")
        self.assertIn("Público", res_a.tipo_servicio)
        res_u = validar_placa("PUA-1234")
        self.assertIn("Público", res_u.tipo_servicio)
        res_z = validar_placa("PZA-1234")
        self.assertIn("Público", res_z.tipo_servicio)

    def test_deteccion_tipo_servicio_gobierno(self):
        """Verifica detección de servicio gubernamental (segunda letra E) y GAD (M)."""
        res_e = validar_placa("PEA-1234")
        self.assertIn("Gubernamental", res_e.tipo_servicio)
        res_m = validar_placa("PMA-1234")
        self.assertIn("Gobiernos Autónomos", res_m.tipo_servicio)

    # --- 2. CASOS BORDE DE LA SPEC ---

    def test_placa_minusculas(self):
        """Entrada en minúsculas debe ser normalizada y validada."""
        res = validar_placa("pbx-1234")
        self.assertTrue(res.es_valida)
        self.assertEqual(res.placa_normalizada, "PBX-1234")

    def test_placa_con_espacios_alrededor(self):
        """Entrada con espacios en blanco al inicio o al final."""
        res = validar_placa("   PBX-1234   ")
        self.assertTrue(res.es_valida)
        self.assertEqual(res.placa_normalizada, "PBX-1234")

    def test_primera_letra_invalida_d_o_f(self):
        """La primera letra 'D' o 'F' no son provincias válidas en la ANT."""
        res_d = validar_placa("DFG-1234")
        self.assertFalse(res_d.es_valida)
        self.assertIn("no corresponde a ninguna provincia", res_d.mensaje)

        res_f = validar_placa("FAA-1234")
        self.assertFalse(res_f.es_valida)
        self.assertIn("no corresponde a ninguna provincia", res_f.mensaje)

    def test_numeros_con_ceros_a_la_izquierda(self):
        """Placas con 4 dígitos que empiezan con ceros (ej. 0001)."""
        res = validar_placa("PBX-0001")
        self.assertTrue(res.es_valida)
        self.assertEqual(res.placa_normalizada, "PBX-0001")

    # --- 3. CASOS NO CONTEMPLADOS EXPLÍCITAMENTE EN LA SPEC ---

    def test_cadena_vacia(self):
        """Entrada vacía o sólo espacios."""
        res = validar_placa("")
        self.assertFalse(res.es_valida)
        self.assertIn("vacía", res.mensaje)

        res_espacios = validar_placa("    ")
        self.assertFalse(res_espacios.es_valida)

    def test_entrada_nula(self):
        """Paso de None como parámetro."""
        res = validar_placa(None)
        self.assertFalse(res.es_valida)
        self.assertIn("None", res.mensaje)

    def test_tipo_de_dato_incorrecto(self):
        """Paso de enteros, diccionarios o listas."""
        res = validar_placa(1234567)
        self.assertFalse(res.es_valida)
        self.assertIn("Tipo de dato no soportado", res.mensaje)

    def test_placa_formato_antiguo_3_numeros(self):
        """Placa con formato histórico de 3 números (rechazada según spec de 4 números)."""
        res = validar_placa("PBX-123")
        self.assertFalse(res.es_valida)
        self.assertIn("formato antiguo", res.mensaje)

    def test_placas_con_caracteres_especiales_o_inyeccion(self):
        """Entradas con símbolos inválidos."""
        res = validar_placa("PBX-12@4")
        self.assertFalse(res.es_valida)
        self.assertIn("caracteres especiales", res.mensaje)

    def test_exceso_de_digitos(self):
        """Más dígitos de los 4 requeridos."""
        res = validar_placa("PBX-12345")
        self.assertFalse(res.es_valida)
        self.assertIn("Estructura inválida", res.mensaje)


if __name__ == "__main__":
    unittest.main()
