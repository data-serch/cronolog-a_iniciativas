
import pandas as pd
import re
from datetime import datetime

# Cargamos el archivo con las iniciativas (en este caso trabajé con excel)
# Este archivo debe tener al menos dos columnas clave:
#
# 1) Una columna llamada "CRONOLOGÍA" donde cada celda contiene texto con los pasos
#    que siguió una iniciativa. Cada paso viene en el siguiente formato:
#    "1 Nombre del paso DD/MM/AAAA", por ejemplo:
#    "3 Aprobado en comisión(es) origen 06/04/2000"
#    Es decir:
#       - Un número secuencial
#       - Una descripción del evento
#       - Y la fecha en formato día/mes/año
#
# 2) Una columna llamada "fecha presentacion (mm,dd,aaaa)" que contiene la fecha
#    en la que se presentó formalmente la iniciativa. 

# archivo = "nombre_del_archivo.xlsx" # o csv
df = pd.read_excel(archivo)
columnas_originales = df.columns.tolist()

pasos_clave = [
    "Atendido en comisión(es) origen",
    "Atendido en pleno de origen",
    "Turnado a revisora",
    "Atendido en comisión(es) revisora",
    "Atendido en pleno revisora",
    "Turnado al Ejecutivo",
    "Publicación en DOF"
]

mapeo_texto = [
    (r"(pendiente|aprobado|rechazado|desechado|dictamen|primera lectura|discusión).*comisi(o|ó)n\(es\).*(origen|cámara de origen)", "Atendido en comisión(es) origen"),
    (r"(dictamen|primera lectura|aprobado|rechazado|discusión|modificaciones).*pleno.*origen", "Atendido en pleno de origen"),
    (r"(aprobado|rechazado|modificaciones).*en origen", "Atendido en pleno de origen"),
    (r"turnado a revisora|minuta recibida en revisora|devuelto a revisora", "Turnado a revisora"),
    (r"(pendiente|aprobado|rechazado|desechado|dictamen|primera lectura|discusión).*comisi(o|ó)n\(es\).*revisora", "Atendido en comisión(es) revisora"),
    (r"(dictamen|primera lectura|aprobado|rechazado|discusión|modificaciones).*pleno.*revisora", "Atendido en pleno revisora"),
    (r"turnado al ejecutivo", "Turnado al Ejecutivo"),
    (r"(publica.*dof|publicado en dof)", "Publicación en DOF"),
]

def extraer_pasos(texto):
    if not isinstance(texto, str):
        return []
    encontrados = re.findall(r'(\d+)\s+([^\d\n]+)\s+(\d{2}/\d{2}/\d{4})', texto)
    pasos = []
    for num, descripcion, fecha in encontrados:
        if fecha == "00/00/0000":
            continue
        try:
            fecha_dt = datetime.strptime(fecha, "%d/%m/%Y")
            pasos.append((int(num), descripcion, fecha_dt))
        except:
            continue
    return pasos

df["PASOS_EXTRAIDOS"] = df["CRONOLOGÍA"].apply(extraer_pasos)
df["CANTIDAD_DE_PASOS"] = df["PASOS_EXTRAIDOS"].apply(lambda pasos: max([p[0] for p in pasos]) if pasos else 0)

def procesar_cronologia(pasos):
    if not pasos:
        return []
    pasos = sorted(pasos, key=lambda x: x[0])
    estado = "origen"
    vuelta = 1
    max_vueltas = 3
    resultados = []

    ultima_transicion = None
    fecha_transicion = None

    for num, descripcion, fecha in pasos:
        desc = descripcion.lower()

        if re.search(r"turnado a revisora|minuta recibida en revisora|devuelto a revisora", desc):
            if estado == "origen":
                estado = "revisora"
                ultima_transicion = "O->R"
                fecha_transicion = fecha

        elif re.search(r"devuelto a origen|minuta recibida en origen", desc):
            if estado == "revisora":
                if not (ultima_transicion == "O->R" and fecha_transicion == fecha):
                    vuelta += 1
                    vuelta = min(vuelta, max_vueltas)
                estado = "origen"
                ultima_transicion = "R->O"
                fecha_transicion = fecha

        for patron, paso_estandar in mapeo_texto:
            if re.search(patron, desc):
                resultados.append((vuelta, paso_estandar, fecha))
                break

    return resultados

df["CRONOLOGÍA_PROCESADA"] = df["PASOS_EXTRAIDOS"].apply(procesar_cronologia)
df["VUELTAS"] = df["CRONOLOGÍA_PROCESADA"].apply(lambda l: max([x[0] for x in l]) if l else 0)

for vuelta in range(1, df["VUELTAS"].max() + 1):
    for paso in pasos_clave:
        df[f"Tiempo {vuelta}ª vuelta → {paso}"] = None

def calcular_tiempos(row):
    pasos = row["CRONOLOGÍA_PROCESADA"]
    fecha_inicio = pd.to_datetime(row["fecha presentacion (mm,dd,aaaa)"], errors='coerce')
    if not pasos or pd.isna(fecha_inicio):
        return row

    fechas_por_paso = {}
    for vuelta, paso, fecha in pasos:
        if vuelta > 3 or paso not in pasos_clave:
            continue
        clave = (vuelta, paso)
        if clave not in fechas_por_paso or fecha > fechas_por_paso[clave]:
            fechas_por_paso[clave] = fecha

    for (vuelta, paso), fecha_final in fechas_por_paso.items():
        col = f"Tiempo {vuelta}ª vuelta → {paso}"
        row[col] = (fecha_final - fecha_inicio).days

    return row

df = df.apply(calcular_tiempos, axis=1)

def calcular_ultimo_tiempo(row):
    pasos = row["CRONOLOGÍA_PROCESADA"]
    fecha_inicio = pd.to_datetime(row["fecha presentacion (mm,dd,aaaa)"], errors='coerce')
    if not pasos or pd.isna(fecha_inicio):
        return None
    ultima_fecha = max([x[2] for x in pasos])
    return (ultima_fecha - fecha_inicio).days

df["Tiempo Presentación → Último paso"] = df.apply(calcular_ultimo_tiempo, axis=1)

columnas_nuevas = [c for c in df.columns if c not in columnas_originales]
df = df[columnas_originales + columnas_nuevas]

df.to_excel("salida_analizada.xlsx", index=False)
