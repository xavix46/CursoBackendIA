# Resultados de Pruebas — Bloque 3.A (Spec a Mano)

**Proyecto:** Validador de formato de placa vehicular (ANT Ecuador)  
**Entorno de ejecución:** Python con `uv`  
**Archivo probado:** `validador_placa.py`  

---

## Casos de Prueba Evaluados

| Tipo de caso | Entrada probada | Comportamiento esperado | Resultado obtenido | Estado |
|---|---|---|---|---|
| **Caso normal** | `"PBX-1234"` | Formato válido estándar con guión; identificar provincia Pichincha y servicio. | **VÁLIDA**<br>• Normalizada: `PBX-1234`<br>• Provincia: Pichincha<br>• Servicio: Particular / Privado | ✅ Aprobado |
| **Caso borde de la spec** | `"pbx 1234"` | Acepta minúsculas y espacios en blanco como separador, normalizando a mayúsculas con guión. | **VÁLIDA**<br>• Normalizada: `PBX-1234`<br>• Provincia: Pichincha<br>• Limpieza y estandarización exitosa | ✅ Aprobado |
| **Caso no contemplado** | `"PBX-123"` | Placa con formato antiguo de 3 números (no especificado qué hacer en `spec_manual.md`). | **INVÁLIDA**<br>• Detectó formato antiguo de 3 números.<br>• Mensaje informativo indicando que la especificación actual requiere 4 números.<br>• No arrojó excepciones no controladas. | ✅ Aprobado |

---

## Otros Casos de Control Ejecutados en la Suite

- **Primera letra no válida como provincia (ej. `"DFG-1234"`):** Rechazada correctamente; la ANT no asigna la letra `D` a provincias.
- **Detección de servicio público/comercial (ej. `"PAA-1234"`):** Detectado como Público / Comercial (transporte, buses, taxis).
- **Tipos no válidos o vacíos (`None`, `""`, `1234567`):** Manejo defensivo con mensajes de error descriptivos.
- **Suite de pruebas:** 16 pruebas unitarias ejecutadas con éxito en `test_validador_placa.py`.
