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
├── figuras/                      Las 12 gráficas del documento, en PNG
├── scripts/
│   └── descargar_datos.py        Recupera los 3 datasets grandes desde NYC Open Data
├── Entrega 1 - ... .docx         Documento escrito (21 páginas)
├── CLUSTER.md                    Cómo trabajar en el clúster: Python, kernel, avisos
└── CHECKSUMS.md5                 Sumas de control de la descarga original
```

## Los datos están en el clúster, no aquí

**Si tienes acceso al clúster, no necesitas descargar nada.** Los siete conjuntos están
en el directorio compartido por NFS, que los seis nodos ven en la misma ruta:

```
/opt/cluster/data/grupo1/
```

El cuaderno lee de ahí directamente (constante `BASE`). El otro equipo que comparte el
clúster trabaja en `/opt/cluster/data/grupo2/`; no lo modifiques.

### Por qué los datasets grandes no están en el repositorio

GitHub rechaza archivos de más de 100 MB, y tres de los nuestros lo superan:

| Dataset | Tamaño | En el repo |
|---|---|---|
| `nypd_arrests_historic.csv` | 1,34 GB | no — usar el clúster o el script |
| `mvc_vehicles.csv` | 842 MB | no — usar el clúster o el script |
| `mvc_crashes.csv` | 477 MB | no — usar el clúster o el script |
| `nypd_arrests_ytd.csv` | 26 MB | sí |
| `nycgov_poverty_2018.csv` | 13,8 MB | sí |
| `collegeboard_ny_sat_2024.pdf` | 1,8 MB | sí |
| `sat_results_2012.csv` | 28 KB | sí |

Git LFS permitiría subirlos, pero su cuota gratuita es de 1 GB de almacenamiento y 1 GB
de transferencia mensual, insuficiente para 2,66 GB y además se consumiría con cada clon.

### Si necesitas los datos en tu máquina

```bash
python scripts/descargar_datos.py
```

Descarga los tres archivos grandes a `data/raw/` desde la API de NYC Open Data, con
reanudación automática si se corta la conexión. Tarda bastante: son 2,66 GB.

## Ejecutar el cuaderno

El cuaderno **debe** ejecutarse con el kernel `PySpark 4.2 (Python 3.11)`. Si lo abres con
el kernel por defecto, falla al importar PySpark. El motivo está explicado en
[CLUSTER.md](CLUSTER.md).

1. Conéctate a la VPN de la universidad.
2. Abre Jupyter en `http://10.43.97.58:8888`.
3. Selecciona el kernel `PySpark 4.2 (Python 3.11)`.
4. Ejecuta las celdas en orden.

La ejecución completa toma unos 3 minutos sobre los 6 nodos.

## Estado de la Entrega 1

| Apartado del enunciado | Estado |
|---|---|
| Entendimiento del negocio | completo |
| Selección de los datos | completo, con limitaciones declaradas |
| Colección y descripción de datos | completo, verificado por MD5 |
| Exploración (mínimo 8 elementos) | 13 elementos |
| Reporte de calidad de datos | completo, con 8 técnicas propuestas |
| Preguntas de negocio (mínimo 8) | 10 preguntas |
| Filtros y transformación inicial | avance, según pide el enunciado |
| Presentación ejecutiva (15 min) | pendiente |

## Pendientes conocidos

- **Desfase temporal entre conjuntos.** Pobreza es de 2018 y SAT de 2012, mientras que
  arrestos y siniestros llegan a 2026. Comparar años distintos es metodológicamente débil.
  Hay que buscar ediciones más recientes de ambos conjuntos y, en lo posible, alinear los
  años de referencia antes de la entrega final.
- La presentación ejecutiva de 15 minutos.

## Cifras principales (de la ejecución del 20/09/2026)

- 6.406.848 arrestos entre 2006 y junio de 2026
- 2.269.187 siniestros y 4.551.002 vehículos involucrados, 2012–2026
- El Bronx lidera en arrestos por habitante (4.523 por 100.000) aunque es tercero en
  volumen absoluto: la normalización por población cambia el orden de prioridad
- El 30,47% de los siniestros no registra distrito, pero solo el 10,61% carece de
  coordenadas, de modo que unos 450.000 admiten recuperación por geolocalización
- Los atributos del conductor en `Vehicles` no se capturaban antes de 2016: la ausencia
  pasa del 99,9% en 2015 al 34,8% en 2016, por lo que no deben imputarse
