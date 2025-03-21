
# Parser de cronologías (# en este caso mide el proceso de  las iniciativas de ley medidas en días)

Este script toma una hoja de cálculo donde cada fila representa una iniciativa legislativa e incluye una columna con la cronología de sus pasos en texto. La herramienta:

- Extrae cada paso con su número, descripción y fecha.
- Clasifica los pasos según su tipo (los nombres que le des en el proceso)
- Detecta en qué vuelta del proceso ocurre cada paso. (las vueltas son previamente definidas. En este caso una vuelta es que una iniciativa sea introducida a la camara de 
origen y despues pase a la cámara revisora; si la revisora la devuelve entonces ya es un segundo paso)
- Calcula el tiempo que tardó desde la presentación hasta cada etapa clave.
- Genera columnas para cada paso relevante y el tiempo total de vida del evento analizado (en este caso una iniciativa)

## Requisitos

- Python 3
- pandas
- openpyxl

## Uso

1. Sirve para analizar texto plano con formatos como este: :
   
1 Presentado en origen 12/08/1998
2 Pendiente en comisión(es) de origen 12/08/1998
3 Aprobado en comisión(es) origen 06/04/2000
4 Dictamen presentado en pleno de origen 25/04/2000
5 De primera lectura en origen 25/04/2000
6 Dictamen a discusión en origen 25/04/2000
7 Aprobado en origen 25/04/2000
8 Turnado a revisora 25/04/2000
9 Minuta recibida en revisora 26/04/2000
10 Pendiente en comisión(es) de revisora 26/04/2000
11 Aprobado en comisión(es) revisora 21/11/2000
12 Dictamen presentado en pleno de revisora 23/11/2000
13 De primera lectura en revisora 23/11/2000
14 Dictamen a discusión en revisora 23/11/2000
15 Aprobado con modificaciones en revisora 23/11/2000
16 Devuelto a origen 23/11/2000
17 Minuta recibida en revisora 28/11/2000
18 Minuta recibida en origen 28/11/2000
19 Pendiente en comisión(es) de Cámara de Origen 28/11/2000
20 Aprobado en comisión(es) origen 27/12/2000(Publicación en Gaceta)
21 Dictamen presentado en pleno origen 27/12/2000
22 De primera lectura en origen 27/12/2000
23 Dictamen a discusión en origen 27/12/2000
24 Modificaciones aprobadas 27/12/2000
25 Turnado al Ejecutivo 27/12/2000
26 Publicado en DOF 12/03/2001

## siempre se necesita un punto de origen (del trámite el proceso etc,eneste caso es: 1 Presentado en origen 12/08/1998)

2. Cambia el nombre del archivo en el script (`archivo = "nombre_del_archivo.xlsx"`).

3. Ejecuta el script.

4. Obtendrás un nuevo archivo llamado `salida_analizada.xlsx` con los tiempos y vueltas ya calculados.

Este código es adaptable a otros flujos con pasos similares (trámites judiciales, administrativos, etc.). Basta con ajustar los patrones de búsqueda (`regex`) y los nombres de pasos.
