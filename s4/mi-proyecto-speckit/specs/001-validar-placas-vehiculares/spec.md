# Feature Specification: Validador de Formato de Placa Vehicular (ANT Ecuador)

**Feature Branch**: `001-validar-placas-vehiculares`

**Created**: 2026-09-16

**Status**: Draft

**Input**: User description: "Implementa un validador de formato de placa vehícular siguiento esta spec: @spec_manual.md , puedes ver que la carpeta raiz trabaja con el ambiente uv con python, para que tengas eso en consideración"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Validación y Normalización de Placas Ecuatorianas Vigentes (Priority: P1)

Como operador o sistema de matriculación vehicular, deseo ingresar una placa vehicular en diferentes estilos de escritura comunes (con guion, con espacio, sin separador, en mayúsculas o minúsculas) y recibir la confirmación inmediata de si cumple con el formato oficial vigente de 3 letras y 4 dígitos, junto con su representación estandarizada, para garantizar la integridad y coherencia de los registros vehiculares.

**Why this priority**: Representa el núcleo operativo y funcional del negocio (MVP). Sin la capacidad de validar y estandarizar placas conformes a la normativa de 3 letras y 4 números, el proceso de matriculación no puede operar.

**Independent Test**: Puede probarse de forma independiente ingresando placas válidas en diversas variantes tipográficas (por ejemplo: `PBX-1234`, `pbx-1234`, `GYA 4567`, `ABC1234`, `PBX-0001`) y comprobando que todas son aprobadas y normalizadas al formato oficial `AAA-0000`.

**Acceptance Scenarios**:

1. **Given** un operador ingresa la placa vehicular `PBX-1234` con guion estándar, **When** solicita la validación, **Then** el sistema confirma que la placa es válida y entrega la placa normalizada `PBX-1234`.
2. **Given** un operador ingresa la placa vehicular `abc1234` en minúsculas y sin separador, **When** solicita la validación, **Then** el sistema confirma que la placa es válida y entrega la placa normalizada `ABC-1234`.
3. **Given** un operador ingresa la placa vehicular `GYB 4567` con un espacio separador y espacios en blanco al inicio y al final, **When** solicita la validación, **Then** el sistema limpia los espacios circundantes, confirma la validez y entrega `GYB-4567`.
4. **Given** un usuario ingresa una placa vehicular con ceros iniciales en el bloque numérico como `PBX-0001`, **When** solicita la validación, **Then** el sistema la reconoce como válida preservando los 4 dígitos numéricos y entrega `PBX-0001`.

---

### User Story 2 - Identificación de Jurisdicción Provincial y Tipo de Servicio (Priority: P1)

Como analista del sistema de matriculación vehicular, requiero que el validador determine automáticamente la provincia de registro oficial y la categoría de servicio del vehículo a partir del código de letras de la placa, para clasificar correctamente los trámites de matriculación conforme a las regulaciones de la Agencia Nacional de Tránsito (ANT).

**Why this priority**: Permite aplicar las reglas administrativas y tarifarias adecuadas según la provincia de emisión (1ª letra) y el tipo de servicio (2ª letra: comercial, gubernamental, institucional o particular).

**Independent Test**: Puede probarse de forma independiente ingresando placas válidas que comiencen con cada una de las 24 letras provinciales oficiales de la ANT y verificando que el resultado exponga con precisión el nombre de la provincia y la categoría de servicio correspondiente.

**Acceptance Scenarios**:

1. **Given** se ingresa la placa `PBX-1234`, **When** se ejecuta la validación, **Then** el sistema identifica la provincia como `Pichincha` y el servicio como `Particular / Privado`.
2. **Given** se ingresa una placa cuyo segundo carácter denota servicio público como `PAA-1234`, `PUA-1234` o `PZA-1234`, **When** se ejecuta la validación, **Then** el sistema identifica la provincia como `Pichincha` y el tipo de servicio como `Público / Comercial`.
3. **Given** se ingresa una placa de vehículo del estado como `PEA-1234` (gubernamental) o `PMA-1234` (Gobiernos Autónomos Descentralizados - GAD), **When** se ejecuta la validación, **Then** el sistema identifica correctamente la provincia y reporta la categoría de servicio respectiva.
4. **Given** se ingresa una placa con cualquiera de los 24 códigos provinciales oficiales (`A` Azuay, `B` Bolívar, `C` Carchi, `E` Esmeraldas, `G` Guayas, `H` Chimborazo, `I` Imbabura, `J` Santo Domingo de los Tsáchilas, `K` Sucumbíos, `L` Loja, `M` Manabí, `N` Napo, `O` El Oro, `P` Pichincha, `Q` Orellana, `R` Los Ríos, `S` Pastaza, `T` Tungurahua, `U` Cañar, `V` Morona Santiago, `W` Galápagos, `X` Cotopaxi, `Y` Santa Elena, `Z` Zamora Chinchipe), **When** se valida, **Then** el sistema asocia de forma unívoca la provincia oficial correspondiente.

---

### User Story 3 - Rechazo y Diagnóstico de Entradas Inválidas o Malformadas (Priority: P2)

Como usuario u operador del sistema de matriculación, cuando ingrese una placa con formato incorrecto, letras no provinciales o caracteres no permitidos, deseo recibir un diagnóstico comprensible que me indique claramente por qué fue rechazada y me oriente a ingresar una placa válida, para subsanar el error de digitación sin confusiones.

**Why this priority**: Asegura que el sistema evite el ingreso de datos basura o fraudulentos y guíe amigablemente al usuario en la corrección de errores.

**Independent Test**: Puede probarse ingresando cadenas con caracteres no reconocidos, exceso o deficiencia de caracteres, o letras iniciales inexistentes en la ANT (como `D` o `F`), comprobando que todas son marcadas como inválidas con su respectivo mensaje explicativo.

**Acceptance Scenarios**:

1. **Given** se ingresa una placa cuya primera letra no corresponde a ninguna provincia ecuatoriana (por ejemplo `DFG-1234` o `FAA-1234`), **When** se valida, **Then** el sistema dictamina que es inválida y notifica que la primera letra no corresponde a una provincia reconocida por la ANT.
2. **Given** se ingresa un valor con caracteres especiales o símbolos (por ejemplo `PBX-12@4` o `PBX#1234`), **When** se valida, **Then** el sistema la rechaza indicando la presencia de caracteres no permitidos y solicita ingresar una placa válida.
3. **Given** se ingresa una combinación con longitud incorrecta de letras o dígitos (por ejemplo `PBX-12345` o `PB-1234`), **When** se valida, **Then** el sistema la declara inválida indicando la discrepancia estructural con el formato requerido de 3 letras y 4 dígitos.

---

### User Story 4 - Detección Asistida de Formato Histórico de Placas (Priority: P2)

Como operador del sistema, cuando se ingrese una placa con el formato antiguo de 3 letras y 3 números (por ejemplo `PBX-123`), deseo que el sistema reconozca específicamente que se trata de una placa del formato histórico no vigente y me informe que el criterio de matriculación actual exige el formato de 4 números.

**Why this priority**: Evita la confusión entre placas totalmente corruptas y placas históricas legítimas que requieren un proceso de actualización o reasignación de placa ante la ANT.

**Independent Test**: Puede probarse enviando placas con el patrón de 3 letras y 3 números (por ejemplo `PBX-123`) y verificando que el resultado sea inválido pero con un mensaje diferenciado de formato histórico desactualizado.

**Acceptance Scenarios**:

1. **Given** un usuario ingresa una placa con formato de 3 letras y 3 dígitos como `PBX-123`, **When** se ejecuta la validación, **Then** el sistema la clasifica como no aceptada y emite un mensaje orientativo explicando que corresponde al formato antiguo y que la normativa actual exige 3 letras y 4 números.

---

### User Story 5 - Tratamiento de Entradas Nulas o Vacías (Priority: P3)

Como sistema de matriculación integrado, cuando una consulta sea enviada vacía, con puros espacios o sin contenido, deseo que el sistema responda de forma segura y clara requiriendo el ingreso de un valor válido de placa, sin causar interrupciones ni excepciones no controladas.

**Why this priority**: Garantiza la robustez y resiliencia del sistema ante omisiones de datos o peticiones incompletas en interfaces de usuario o integraciones.

**Independent Test**: Puede probarse suministrando textos vacíos, cadenas de solo espacios o valores nulos, verificando que se rechacen de forma controlada solicitando el ingreso de una placa válida.

**Acceptance Scenarios**:

1. **Given** se envía una cadena vacía `""` o compuesta exclusivamente de espacios en blanco `"    "`, **When** se valida, **Then** el sistema devuelve un estado de invalidez y un mensaje solicitando ingresar una placa válida.
2. **Given** se envía una ausencia de dato (valor nulo), **When** se procesa la validación, **Then** el sistema rechaza la operación informando la ausencia de placa y requiriendo un valor de texto válido.

---

### Edge Cases

- **Espaciado perimetral irregular**: Entradas con múltiples espacios en blanco al inicio o al final (ej. `   PBX-1234   `) deben ser limpiadas antes de evaluar la validez.
- **Variabilidad de separadores**: Cadenas con guion (`PBX-1234`), con espacio simple (`PBX 1234`) o continuas (`PBX1234`) deben ser aceptadas y unificadas en la salida normalizada (`PBX-1234`).
- **Mayúsculas y minúsculas**: La entrada puede venir en minúsculas (`pbx-1234`) o combinación mixta (`PbX-1234`), debiendo normalizarse a mayúsculas.
- **Dígitos con ceros sucesivos a la izquierda**: Placas válidas cuyos números inician con ceros (ej. `PBX-0001` a `PBX-0999`) deben ser aceptadas conservando exactamente los 4 dígitos.
- **Letras reservadas o no asignadas como cabecera provincial**: Letras como `D` o `F` que no corresponden a provincias de Ecuador deben ser rechazadas con mención explícita.
- **Placas históricas de 3 números**: Combinaciones como `PBX-123` deben ser diferenciadas de basura sintáctica y rechazadas con explicación de formato antiguo.
- **Tipos de datos no textuales**: Valores numéricos puros (ej. `1234567`) u objetos no compatibles deben ser rechazados de manera controlada sin generar fallas críticas.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema DEBE validar si una placa vehicular ingresada cumple estrictamente con la estructura reglamentaria de 3 letras seguidas de 4 números.
- **FR-002**: El sistema DEBE permitir como separador entre el bloque de letras y el bloque numérico un guion (`-`), un espacio en blanco (` `) o ningún separador.
- **FR-003**: El sistema DEBE normalizar toda placa válida al estándar de presentación oficial de la ANT compuesto por 3 letras mayúsculas, un guion separador y 4 dígitos (`AAA-0000`).
- **FR-004**: El sistema DEBE validar que la primera letra de la placa pertenezca a la tabla oficial de las 24 provincias del Ecuador reconocida por la ANT (`A, B, C, E, G, H, I, J, K, L, M, N, O, P, Q, R, S, T, U, V, W, X, Y, Z`).
- **FR-005**: El sistema DEBE rechazar cualquier placa cuya primera letra no corresponda a una provincia ecuatoriana (incluyendo de forma expresa las letras `D` y `F`), proporcionando un mensaje descriptivo.
- **FR-006**: El sistema DEBE clasificar e informar el tipo de servicio del vehículo a partir de la segunda letra de la placa, distinguiendo al menos: servicio público/comercial (`A`, `U`, `Z`), gubernamental (`E`), Gobiernos Autónomos Descentralizados (`M`), uso oficial (`X`), y servicio particular/privado para las restantes.
- **FR-007**: El sistema DEBE detectar placas que siguen el formato antiguo ecuatoriano de 3 letras y 3 números y rechazarlas con una indicación clara de que la norma vigente exige 4 números.
- **FR-008**: El sistema DEBE rechazar entradas con caracteres especiales, signos de puntuación ajenos al guion o símbolos no alfanuméricos, requiriendo el ingreso de una placa válida.
- **FR-009**: El sistema DEBE rechazar entradas con cantidad insuficiente o excedente de caracteres alfanuméricos, informando la discrepancia estructural observada.
- **FR-010**: El sistema DEBE rechazar valores vacíos, compuestos únicamente de espacios o valores nulos, indicando de forma explícita la necesidad de ingresar una placa válida.
- **FR-011**: El sistema DEBE entregar un objeto de resultado estructurado que contenga: estado de validez (booleano), placa original, placa normalizada (si es válida), provincia identificada, tipo de servicio y mensaje explicativo para el usuario o sistema consumidor.

### Key Entities

- **Placa Vehicular**: Representa la identificación física y registral asignada a un vehículo automotor. Atributos conceptuales: cadena original ingresada, bloque de letras (3 caracteres alfabéticos), bloque numérico (4 dígitos decimales), separador utilizado.
- **Resultado de Validación**: Representa el dictamen emitido por el sistema tras la evaluación de la placa. Atributos: estado de validez (válida / inválida), placa normalizada (`AAA-0000`), provincia asociada, tipo de servicio vehicular, mensaje de diagnóstico explicativo y desglose de metadatos.
- **Catálogo Provincial ANT**: Representa la correspondencia geográfica oficial entre la letra inicial de la placa y la división político-administrativa de las 24 provincias del Ecuador.
- **Catálogo de Tipos de Servicio ANT**: Representa la clasificación normativa del uso del vehículo (particular, público/comercial, gubernamental, municipal/GAD, oficial) determinada por la segunda letra de la placa.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: El 100% de las placas vehiculares ecuatorianas vigentes bajo el esquema de 3 letras y 4 números son validadas y normalizadas satisfactoriamente.
- **SC-002**: El 100% de las 24 provincias oficiales de la ANT son identificadas con exactitud a partir de la primera letra de la placa.
- **SC-003**: El 100% de las entradas inválidas (caracteres extraños, formato antiguo de 3 dígitos, letras no provinciales, vacíos o nulos) son rechazadas sin interrupciones del servicio y con mensajes explicativos orientados a la corrección.
- **SC-004**: Los operadores y sistemas integrados reciben una respuesta inmediata de validación (tiempo de respuesta imperceptible en procesamiento de registros individuales).
- **SC-005**: Cero errores de falsos positivos en placas con letras no provinciales (como `D` o `F`) o con cantidades erróneas de dígitos.

## Assumptions

- Se asume que el alcance de la validación cubre los vehículos automotores de transporte terrestre estándar (automóviles, camionetas, buses, camiones) bajo el esquema ANT de 3 letras y 4 números.
- Se asume que las motocicletas (que tradicionalmente poseen esquemas diferenciados de cantidad de letras/números) quedan fuera del alcance inmediato de esta regla de 3 letras y 4 números, salvo que adopten dicha configuración.
- Se asume que la validación es de formato y sintaxis registral (conforme a las reglas de codificación de la ANT), y no una verificación de existencia en la base de datos de vehículos matriculados en tiempo real.
- Se asume que el sistema consumidor utilizará la placa normalizada (`AAA-0000`) para almacenamiento y consultas uniformes en la base de datos de matriculación.
- Se asume que los mensajes diagnósticos serán presentados en idioma español, acorde al contexto regulatorio de Ecuador.
