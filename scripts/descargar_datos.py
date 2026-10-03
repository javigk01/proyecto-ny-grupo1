# -*- coding: utf-8 -*-
"""Descarga los datasets grandes que no caben en el repositorio.

Solo hace falta si se quiere trabajar fuera del clúster. Si tienes acceso al
clúster, los siete conjuntos ya están en /opt/cluster/data/grupo1.

Uso:
    python scripts/descargar_datos.py
    python scripts/descargar_datos.py --verificar   (solo comprueba lo descargado)
"""
import argparse
import hashlib
import os
import sys
import time
import urllib.request
import zipfile

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DESTINO = os.path.join(RAIZ, "data", "raw")
PLANTILLA = "https://data.cityofnewyork.us/api/views/%s/rows.csv?accessType=DOWNLOAD"

# Microdatos del censo: se publican comprimidos y requieren extraccion
PUMS_URL = ("https://www2.census.gov/programs-surveys/acs/data/pums/"
            "2023/1-Year/csv_pny.zip")
PUMS_ZIP = "acs_pums_ny_2023.zip"
PUMS_CSV = "acs_pums_ny_2023_persona.csv"
PUMS_INTERNO = "psam_p36.csv"
PUMS_MD5_ZIP = "ca6335af22b48f84d87d103a1acd5e51"
PUMS_MD5_CSV = "102dbee93a327ec5e1ff6c5a0bcd17b5"

# Sumas de control y conteos de la descarga original del 20/09/2026.
# Los conjuntos de arrestos y siniestros se actualizan periodicamente, de modo
# que una descarga posterior tendra un MD5 distinto. Eso no indica corrupcion.
GRANDES = [
    {"archivo": "nypd_arrests_historic.csv", "id": "8h9b-rp9u",
     "md5": "dda349aa0a309b79ff1b8560b1e4983d",
     "bytes": 1341449946, "registros": 6264978,
     "nombre": "NYPD Arrests Data (Historic)"},
    {"archivo": "mvc_vehicles.csv", "id": "bm4k-52h4",
     "md5": "a42d89580d36a63ee3c3ec6fc8dfd15b",
     "bytes": 842678494, "registros": 4551002,
     "nombre": "Motor Vehicle Collisions - Vehicles"},
    {"archivo": "mvc_crashes.csv", "id": "h9gi-nx95",
     "md5": "3910e93784f255c1872c6414fbf20ba8",
     "bytes": 476616139, "registros": 2269187,
     "nombre": "Motor Vehicle Collisions - Crashes"},
]


def md5_de(ruta, bloque=4 * 1024 * 1024):
    h = hashlib.md5()
    with open(ruta, "rb") as f:
        for trozo in iter(lambda: f.read(bloque), b""):
            h.update(trozo)
    return h.hexdigest()


def humano(n):
    for unidad in ("B", "KB", "MB", "GB"):
        if abs(n) < 1024:
            return "%.1f %s" % (n, unidad)
        n /= 1024.0
    return "%.1f TB" % n


def descargar(url, ruta, esperado):
    """Descarga con reanudacion: si el archivo esta incompleto, continua."""
    hecho = os.path.getsize(ruta) if os.path.exists(ruta) else 0
    if hecho and hecho >= esperado:
        print("      ya esta completo")
        return
    for intento in range(1, 7):
        try:
            peticion = urllib.request.Request(url)
            if hecho:
                peticion.add_header("Range", "bytes=%d-" % hecho)
                print("      reanudando desde %s" % humano(hecho))
            modo = "ab" if hecho else "wb"
            t0 = time.time()
            with urllib.request.urlopen(peticion, timeout=120) as r, open(ruta, modo) as f:
                while True:
                    trozo = r.read(1024 * 1024)
                    if not trozo:
                        break
                    f.write(trozo)
                    hecho += len(trozo)
                    transcurrido = max(time.time() - t0, 0.001)
                    sys.stdout.write("\r      %s  (%.1f MB/s)   " %
                                     (humano(hecho), hecho / 1e6 / transcurrido))
                    sys.stdout.flush()
            print()
            return
        except Exception as ex:
            hecho = os.path.getsize(ruta) if os.path.exists(ruta) else 0
            print("\n      corte (%s), reintento %d de 6" % (type(ex).__name__, intento))
            time.sleep(4)
    raise RuntimeError("no se pudo completar la descarga de %s" % ruta)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verificar", action="store_true",
                    help="no descarga; solo comprueba los archivos presentes")
    args = ap.parse_args()

    os.makedirs(DESTINO, exist_ok=True)
    print("destino: %s\n" % DESTINO)

    problemas = 0
    for d in GRANDES:
        ruta = os.path.join(DESTINO, d["archivo"])
        print("%s" % d["nombre"])
        print("   %s  (%s esperados)" % (d["archivo"], humano(d["bytes"])))

        if not args.verificar:
            descargar(PLANTILLA % d["id"], ruta, d["bytes"])

        if not os.path.exists(ruta):
            print("   FALTA\n")
            problemas += 1
            continue

        real = os.path.getsize(ruta)
        print("   tamano : %s" % humano(real))
        print("   md5    : calculando...", end="\r")
        suma = md5_de(ruta)
        if suma == d["md5"]:
            print("   md5    : coincide con la descarga original          ")
        else:
            print("   md5    : %s" % suma)
            print("            distinto del original (%s)." % d["md5"])
            print("            Es lo esperado si el portal actualizo el conjunto;")
            print("            en ese caso los conteos del cuaderno cambiaran.")
        print()

    # ---------------------------------------------------- ACS PUMS 2023
    print("ACS PUMS 2023, estado de Nueva York")
    ruta_zip = os.path.join(DESTINO, PUMS_ZIP)
    ruta_csv = os.path.join(DESTINO, PUMS_CSV)
    print("   %s  (36,6 MB comprimidos)" % PUMS_ZIP)

    if not args.verificar and not os.path.exists(ruta_csv):
        descargar(PUMS_URL, ruta_zip, 36608199)

    if os.path.exists(ruta_zip):
        suma = md5_de(ruta_zip)
        print("   md5 zip: %s" % ("coincide" if suma == PUMS_MD5_ZIP else suma))

    if not os.path.exists(ruta_csv) and os.path.exists(ruta_zip):
        print("   extrayendo %s -> %s" % (PUMS_INTERNO, PUMS_CSV))
        with zipfile.ZipFile(ruta_zip) as z, open(ruta_csv, "wb") as destino:
            with z.open(PUMS_INTERNO) as origen:
                while True:
                    trozo = origen.read(8 * 1024 * 1024)
                    if not trozo:
                        break
                    destino.write(trozo)

    if os.path.exists(ruta_csv):
        print("   %s  (%s)" % (PUMS_CSV, humano(os.path.getsize(ruta_csv))))
        suma = md5_de(ruta_csv)
        print("   md5 csv: %s" % ("coincide" if suma == PUMS_MD5_CSV else suma))
    else:
        print("   FALTA")
        problemas += 1
    print()

    print("-" * 62)
    if problemas:
        print("faltan %d archivos" % problemas)
        sys.exit(1)
    print("listo. Los conjuntos pequenos ya vienen en el repositorio.")


if __name__ == "__main__":
    main()
