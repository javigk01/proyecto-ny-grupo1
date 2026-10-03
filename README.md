# Proyecto Procesamiento de Datos — Aldana · Ávila · Pardo

Plan de acción basado en datos para la reducción de arrestos y siniestros viales en la
ciudad de Nueva York.

Pontificia Universidad Javeriana · Procesamiento de Datos a Gran Escala · Semestre 8

---

## Qué hay en este repositorio

```
.
├── notebooks/
│   └── entrega1.ipynb            Anexo de código, ejecutado sobre el clúster
├── data/raw/                     Datasets pequeños (los grandes NO, ver más abajo)
├── figuras/                      Las 13 gráficas del documento, en PNG
├── scripts/
│   └── descargar_datos.py        Recupera los datasets grandes desde su fuente
├── Entrega 1 - ... .docx         Documento escrito (26 páginas)
├── CLUSTER.md                    Cómo trabajar en el clúster: Python, kernel, avisos
└── CHECKSUMS.md5                 Sumas de control de todas las descargas
```

## Los datos están en el clúster, no aquí

**Si tienes acceso al clúster, no necesitas descargar nada.** Los conjuntos están en el
directorio compartido por NFS, que los seis nodos ven en la misma ruta:

```
/opt/cluster/data/grupo1/          2,8 GB
```

El cuaderno lee de ahí directamente (constante `BASE`). El otro equipo que comparte el
clúster trabaja en `/opt/cluster/data/grupo2/`; no lo modifiques.

### Los diez conjuntos

| Conjunto | Registros | Año | Origen | En el repo |
|---|---|---|---|---|
| `nypd_arrests_historic.csv` | 6.264.978 | 2006–2025 | equipo | no, usar script |
| `mvc_vehicles.csv` | 4.551.002 | 2012–2026 | enunciado | no, usar script |
| `mvc_crashes.csv` | 2.269.187 | 2012–2026 | equipo | no, usar script |
| `acs_pums_ny_2023_persona.csv` | 206.408 | 2023 | equipo | no, usar script |
| `nyc_graduacion_2012_2019.csv` | 321.002 | 2016–2023 | equipo | sí |
| `nyc_regents_2015_2019.csv` | 82.964 | 2015–2019 | equipo | sí |
| `nypd_arrests_ytd.csv` | 141.870 | 2026 | enunciado | sí |
| `nycgov_poverty_2018.csv` | 68.273 | 2018 | enunciado | sí |
| `sat_results_2012.csv` | 478 | 2012 | enunciado | sí |
| `puma2020_a_distrito.csv` | 55 | — | derivado | sí |

Los cuatro primeros superan el límite de 100 MB por archivo de GitHub. Git LFS lo
permitiría, pero su cuota gratuita es de 1 GB de almacenamiento y 1 GB de transferencia
mensual, insuficiente y se consumiría con cada clon.

### Si necesitas los datos en tu máquina

```bash
python scripts/descargar_datos.py              # descarga y verifica
python scripts/descargar_datos.py --verificar  # solo comprueba lo presente
```

Descarga con reanudación automática si se corta la conexión, extrae el ACS PUMS y
verifica las sumas MD5. Son unos 2,6 GB.

## Alineación temporal: por qué todo el corte transversal es de 2023

El enunciado suministró pobreza de 2018 y resultados SAT de 2012, mientras que arrestos y
siniestros llegan a junio de 2026. **Cruzar indicadores de años distintos no es
admisible**: cualquier coincidencia territorial podría deberse al desfase.

Actualizar esas fuentes era imposible: el portal publica catorce ediciones de la medida de
pobreza, de 2005 a 2018, y ninguna posterior; de SAT solo existen 2010 y 2012. Son las más
recientes que hay.

La solución fue incorporar dos fuentes equivalentes que sí alcanzan 2023:

- **ACS PUMS 2023** — los microdatos del censo sobre los que el propio NYCgov construye su
  medida de pobreza. El distrito se deriva del cruce oficial tracto-PUMA del Censo; se
  verificó que cada uno de los 55 PUMAs de la ciudad pertenece a un solo distrito.
- **Graduación por cohorte** — la cohorte 2019 es la clase de 2023.

Validación: la tasa de pobreza obtenida para la ciudad, **18,00%**, coincide con el 18,2%
publicado para 2023.

Las series temporales conservan la cobertura completa: una variable observada a lo largo
del tiempo no se alinea. Los conjuntos de 2018 y 2012 se conservan como contraste
histórico para evaluar la persistencia del ordenamiento territorial.

## Ejecutar el cuaderno

El cuaderno **debe** ejecutarse con el kernel `PySpark 4.2 (Python 3.11)`. Con el kernel
por defecto falla al importar PySpark; el motivo está en [CLUSTER.md](CLUSTER.md).

1. Conéctate a la VPN de la universidad.
2. Abre Jupyter en `http://10.43.97.58:8888`.
3. Selecciona el kernel `PySpark 4.2 (Python 3.11)`.
4. Ejecuta las celdas en orden.

La ejecución completa toma unos 3 minutos sobre los 6 nodos.

## Estado de la Entrega 1

| Apartado del enunciado | Estado |
|---|---|
| Entendimiento del negocio | completo |
| Selección de los datos | completo, con alineación y limitaciones declaradas |
| Colección y descripción de datos | completo, verificado por MD5 |
| Exploración (mínimo 8 elementos) | 14 elementos |
| Reporte de calidad de datos | completo, con 8 técnicas propuestas |
| Preguntas de negocio (mínimo 8) | 10 preguntas |
| Filtros y transformación inicial | avance, según pide el enunciado |
| Presentación ejecutiva (15 min) | pendiente |

## Hallazgos principales

Todas las cifras provienen de la ejecución del cuaderno sobre el clúster.

**El orden de prioridad cambia al normalizar.** Brooklyn tiene más arrestos en términos
absolutos, pero el Bronx registra 3.925 por cada 100.000 habitantes frente a 2.437 de
Brooklyn: un 61% más. Priorizar por cifras absolutas llevaría al territorio equivocado.

**El Bronx concentra tres de los cuatro problemas.** Es primero en arrestos por habitante
(3.925), en pobreza (27,67%) y en rezago educativo (77,1% de graduación). Staten Island es
quinto en los cuatro indicadores.

**La siniestralidad sigue un patrón propio.** Brooklyn encabeza con 894 siniestros por
100.000 habitantes y el Bronx es tercero. Los dos indicadores del encargo no identifican el
mismo territorio prioritario.

**Los arrestos son estables en el tiempo; los siniestros no.** El Bronx es primero en
arrestos en 2018, 2021, 2023 y 2025. En siniestros, Manhattan cayó del primer al cuarto
puesto, pasando de 2.662 a 740 por 100.000 habitantes entre 2015 y 2023. Consecuencia: la
priorización en seguridad ciudadana puede apoyarse en un diagnóstico estable, la de
seguridad vial debe recalcularse periódicamente.

**El ordenamiento educativo persiste once años.** El SAT de 2012 y la graduación de 2023
producen el mismo orden entre distritos, pese a ser mediciones distintas.

**Los atributos del conductor no se capturaban antes de 2016.** La ausencia pasa del 99,9%
en 2015 al 34,8% en 2016. No deben imputarse: hay que acotar la ventana temporal.

**El marcador «s» oculta faltantes en todos los datasets educativos.** Afecta al 39,91% de
Regents, al 25,45% de graduación y al 11,92% de SAT. Un conteo de nulos no lo detecta
porque técnicamente es un valor.

## Pendientes

- La presentación ejecutiva de 15 minutos.
- Implementar la imputación geoespacial del distrito en los siniestros: el 30,47% no tiene
  distrito pero solo el 10,61% carece de coordenadas, así que unos 450.000 registros son
  recuperables.
