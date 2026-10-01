# Trabajar en el clúster

Notas prácticas para el equipo. Incluye dos problemas que ya costaron tiempo encontrar y
que conviene no volver a sufrir.

## Topología

Seis máquinas virtuales con Rocky Linux 9.8, Apache Spark 4.2.0 en modo standalone.
Capacidad agregada: **24 núcleos y 86 GB de RAM** para ejecutores.

| Nodo | IP | Rol | Núcleos | RAM |
|---|---|---|---|---|
| NBDG41 | 10.43.97.58 | maestro + trabajador | 4 | 15 GB |
| NBDG42 | 10.43.97.59 | trabajador | 4 | 15 GB |
| NBDG44 | 10.43.97.61 | trabajador | 4 | 15 GB |
| NBDG46 | 10.43.97.63 | trabajador | 4 | 15 GB |
| NBDG50 | 10.43.97.67 | trabajador | 4 | 15 GB |
| NBDG54 | 10.43.97.71 | trabajador | 4 | 15 GB |

- Maestro: `spark://10.43.97.58:7077`
- Interfaz de administración: `http://10.43.97.58:8081`
- Jupyter: `http://10.43.97.58:8888`

Requiere estar conectado a la VPN de la universidad.

## Almacenamiento: NFS, no HDFS

**No hay HDFS en funcionamiento.** Las bibliotecas de Hadoop 3.5.0 están instaladas, pero
no corren NameNode ni DataNode: `hdfs dfs -ls /` lista el sistema de archivos local.

La compartición se resuelve por NFS 4.2. El maestro exporta `/opt/cluster` y los cinco
trabajadores lo montan en la misma ruta, así que todos los nodos ven los datos igual.

```
/opt/cluster/data/grupo1/     nuestros datos (2,6 GB)
/opt/cluster/data/grupo2/     datos del otro equipo — no modificar
```

Los nombres de esas dos carpetas son simplemente los que quedaron al repartir el espacio
compartido y no se corresponden con la numeración de los equipos.

Dos consecuencias a tener en cuenta:

- **`/home/estudiante` NO es compartido.** Lo que guardes ahí solo existe en esa máquina.
  Si un cuaderno debe ser visible para todo el clúster, va en `/opt/cluster`.
- Todo el I/O pasa por el disco del maestro, que es el cuello de botella. Si en el futuro
  los tiempos de lectura molestan, convertir los CSV a Parquet es la mejora más directa.

## Python: hay que usar el 3.11, no el del sistema

Spark 4.2.0 **requiere Python 3.10 o superior**, y el intérprete del sistema es 3.9.25.
Con el Python del sistema, importar PySpark falla así:

```
pyspark/sql/types.py línea 557, in GeographyType
TypeError: unsupported operand type(s) for |: 'type' and 'type'
```

Es sintaxis `X | Y` (PEP 604), que no existe en 3.9.

Se instaló CPython 3.11.16 en el directorio compartido, de modo que los seis nodos lo ven
en la misma ruta sin configuración por máquina:

```
/opt/cluster/python311/bin/python3
```

Incluye pandas, numpy, matplotlib, seaborn, pyarrow y jupyterlab.

### En Jupyter

Selecciona el kernel **`PySpark 4.2 (Python 3.11)`**. Ya está registrado y define las
variables de entorno necesarias. Con el kernel por defecto no funciona.

### Desde la terminal

```bash
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk
export SPARK_HOME=/opt/cluster/spark
export PYSPARK_PYTHON=/opt/cluster/python311/bin/python3
export PYSPARK_DRIVER_PYTHON=/opt/cluster/python311/bin/python3

/opt/cluster/spark/bin/spark-submit --master spark://10.43.97.58:7077 mi_script.py
```

## Convivencia con el otro equipo

Los seis integrantes del equipo de clúster son dos equipos de proyecto distintos que
comparten la misma cuenta `estudiante`. Acuerdos vigentes:

- Cada equipo trabaja en su carpeta: `/opt/cluster/data/grupo1` y `.../grupo2`.
- No hay cuotas de recursos. **El primer trabajo que se lance toma los 24 núcleos.** Como
  está activa la asignación dinámica, los ejecutores se liberan cuando la sesión queda
  inactiva, así que en la práctica el clúster se usa por turnos. Un trabajo largo bloquea
  al otro equipo mientras dure: conviene avisar antes de lanzar algo pesado.
- Si alguna vez hace falta repartir en firme, basta con que cada equipo fije
  `spark.cores.max` a 12 en su sesión.

## Avisos: dos problemas que ya se resolvieron

### El cortafuegos rompía los trabajos de forma intermitente

**Síntoma:** un trabajo falla con `FetchFailedException` y, más abajo,
`java.net.NoRouteToHostException`. Lo desconcertante es que el mismo cuaderno funciona una
vez y falla la siguiente.

**Causa:** Spark asigna a cada ejecutor un puerto alto aleatorio para servir los bloques de
shuffle. Los nodos `.59` y `.71` tenían `firewalld` activo mientras los otros cuatro no, de
modo que el fallo solo aparecía cuando la asignación dinámica colocaba un ejecutor en uno
de esos dos nodos.

**Solución aplicada el 20/09/2026:** se unificó el estado de los seis nodos.

```bash
sudo systemctl stop firewalld
sudo systemctl disable firewalld
```

Este paso no figuraba en `ComandosWorker.txt`, razón por la cual dos máquinas quedaron sin
configurar. Ya quedó documentado ahí, en la sección 6.

### Los conteos de `Crashes` salían mal

`mvc_crashes.csv` contiene un registro con un salto de línea embebido dentro de un nombre
de calle. Sin `multiLine`, Spark lo parte en dos filas defectuosas y el total queda mal.

```python
spark.read.option("header", True).option("multiLine", True) \
     .option("quote", '"').option("escape", '"').csv(ruta)
```

Solo hace falta en `Crashes`. Verificado archivo por archivo: los demás no tienen saltos
embebidos, y activar `multiLine` en ellos impediría dividirlos y desperdiciaría el
paralelismo.

## Credenciales

Las credenciales de las VM **no están en este repositorio** y no deben subirse. El archivo
`credenciales.txt` está en `.gitignore`. Pídeselas a un integrante del equipo.
