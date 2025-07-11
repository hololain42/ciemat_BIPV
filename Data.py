#%%
from datetime import datetime
import time
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import os 
import chardet

#%%

# Función para trackear el tiempo que tarda en ejecutar el programa (basta con poner mostrar_tiempo_total() al final del último archivo .py que se ejecuta)
tiempo_inicio = time.time()

print("-" * 50)
print(f"[INFO] Iniciando a las {datetime.now().strftime('%H:%M:%S')}")

def mostrar_tiempo_total():
    
    tiempo_total = time.time() - tiempo_inicio
    
    if tiempo_total < 60:
        print(f"[INFO] Tiempo total de ejecución: {tiempo_total:.2f} segundos")
    elif tiempo_total < 3600:
        minutos = int(tiempo_total // 60)
        segundos = tiempo_total % 60
        print(f"[INFO] Tiempo total de ejecución: {minutos}m {segundos:.1f}s ({tiempo_total:.2f}s)")
    else:
        horas = int(tiempo_total // 3600)
        minutos = int((tiempo_total % 3600) // 60)
        segundos = tiempo_total % 60
        print(f"[INFO] Tiempo total de ejecución: {horas}h {minutos}m {segundos:.1f}s")


print("-" * 50)
print(f"[INFO] Creamos la estructura de directorios del proyecto:")

# CREAMOS LA ESTRUCTURA DE CARPETAS DEL PROYECTO
directorios_necesarios = [
    "Excel Resultados",
    "Excel Resultados/Datos Submuestreados",
    "Excel Resultados/NOCT",
    "figuras",
    "figuras/DatPlots",
    "figuras/RossModel_fit",
    "figuras/RossModel_fit/png",
    "figuras/Produccion_anual",
    "figuras/Produccion_anual/png",
    "figuras/Histogramas_Irradiacion/",
    "figuras/Histogramas_Irradiacion/png",
]

def crear_estructura_directorios():
    for dir in directorios_necesarios:
        try:
            if not os.path.exists(dir):
                os.makedirs(dir)
                print(f"-Directorio creado: {dir}")
            else:
                print(f"-El directorio ya existe: {dir}")
        except Exception as e:
            print(f"-->Error al crear '{dir}': {e}")


crear_estructura_directorios()


##### IMPORT DATA SECTION #####

'''
El Datalogger ha omitido la cabecera correspondiente al inversor Huawei por lo que
los datos no corresponden a sus cabeceras:


Cabeceras de ficheros (con error)                               Cabeceras corregidas

Canal 214-Canal_214_Im_terra2_[A]                       Canal 214-Canal_214_Im_terra2_[A]
Canal 215-Canal_215_Im_terra3_[A]                       Canal 215-Canal_215_Im_terra3_[A]
Canal 216-Canal_216_Im_terra4_[A]                       Canal 216-Canal_216_Im_terra4_[A]
Canal 217-Canal_217_Ientradainversor_antacita_[A]       Canal 217-Canal_217_Ientradainversor_antacita_[A]
Canal 218-Canal_218_Ientradainversor_verde_[A]          Canal 218-Canal_218_Ientradainversor_verde_[A]
Canal 219-Canal_219_Ientradainversor_terracota_[A]      Canal 219-Canal_219_Ientradainversor_terracota_[A]

Canal 301-Canal_301_PAC_inversor_antracita_[W]          Potencia Huawei

Canal 302-Canal_302_PAC_inversor_verde_[W]              Canal 301-Canal_301_PAC_inversor_antracita_[W]
Canal 303-Canal_303_PAC_inversor_terracota_[W]          Canal 302-Canal_302_PAC_inversor_verde_[W]
Canal 304-Canal_304_G1_abajo_[W/m2]                     Canal 303-Canal_303_PAC_inversor_terracota_[W]
Canal 305-Canal_305_G2_arriba_[W/m2]                    Canal 304-Canal_304_G1_abajo_[W/m2]



Esto ocurre principalmente con archivos antiguos ya que a partir de enero del presente año
las cabeceras corresponden en longitud al número de registros de datos pero esto sigue siendo 
un error ya que añade el canal 420 (suma de canales 101+102) los cuales habían sido liberados ya
hace tiempo, entonces se corregirán las cabeceras para ambos casos.

Si bien José corrigió la no existencia del canal 220, no estoy seguro si al añadir un canal ocasione
un desplazamiento en las cabeceras, es decir, aumentando en 1 el número de cabeceras por encima del número
de registros (debido a la presencia del canal 420 el cual no es relevante en lo absoluto). 

La corrección realizada en el programa solventa ambas situaciones y dejará evaluar sin problemas los
registros que no tengan problemas en adelante.
'''


#Dataloggerfiles = os.listdir("Datos Datalogger/DAQ970A")
#
#DataLoggerDataFrame = pd.DataFrame()
#
#for i in Dataloggerfiles[1:]:
#    with open("Datos Datalogger/DAQ970A/" + i, 'r', encoding='latin1') as f:
#        columns = f.readlines()
#    lt = [o.strip().split('\t') for o in columns]
#    df = pd.DataFrame(lt)
#    new_header = df.iloc[0] 
#    df = df[1:]
#    df.columns = new_header
#    if None in df.columns:
#        df = df.drop(columns=[None])
#    DataLoggerDataFrame = pd.concat([DataLoggerDataFrame, df], axis=0, ignore_index=True)

path = os.getcwd()
Dataloggerfiles = os.listdir(path+"/Datos Datalogger/DAQ970A")

# Por temas de caché, nos aseguramos de que se importen bien ordenados por fecha
Dataloggerfiles = sorted(Dataloggerfiles, 
                        key=lambda x: datetime.strptime("_".join(x.split("_")[:3]), "%Y_%m_%d"))

DataLoggerDataFrame = pd.DataFrame()

"""
IMPORTANTE: El sistema no estuvo completamente operativo (en su versión "final", con todas las medidas ajustadas
piranómetro de referencia, termómetro de temperatura ambiente...) hasta principios de diciembre.
POR TANTO, vamos a coger datos desde el solsticio de invierno (21 de diciembre de 2024), ignorando todos los datos previos
"""

num_arch = len(Dataloggerfiles)
print("-" * 50)
print(f"Total de archivos del Datalogger: {num_arch}")

fecha_solsticio = "2024_12_21"
fecha_ultimo_arch = Dataloggerfiles[-1].split("_DAQ970A_Colores")[0]

try:
    num_arch_solsticio = next(i for i, archivo in enumerate(Dataloggerfiles) 
                             if fecha_solsticio in archivo)
    print(f"Índice del archivo correspondiente al solsticio: {num_arch_solsticio}")
except StopIteration:
    print(f"Archivo del {fecha_solsticio} no encontrado en el directorio")

num_arch_analizables = num_arch - num_arch_solsticio
print(f"Archivos desde el solsticio de invierno (21/12/24): {num_arch_analizables}")
print(f"->Analizamos datos desde el " + Dataloggerfiles[num_arch_solsticio].split("_DAQ970A_Colores")[0] + " al " + Dataloggerfiles[-1].split("_DAQ970A_Colores")[0])

# Loggear la primera aparición del canal 220 (Potencia AC Inversor Huawei)
primer_canal_220 = None
# Lista para posibles archivos que fallen al procesarse
fallo_lectura_arch = []
# Contador de iteraciones
iter = 0

print("-" * 50)
print(f"[INFO] Comienza el procesado de archivos:")
for i in Dataloggerfiles[num_arch_solsticio:]:

    try:
        # print(f"Abriendo archivo {i}")

        with open("Datos Datalogger/DAQ970A/" + i, 'r', encoding='latin1') as f:
            columns = f.readlines()
        lt = [o.strip().split('\t') for o in columns]
        header = lt[0]

        # Comprobamos si el Canal 220 existe en archivo. Si no, lo insertamos después del canal 219.
        if 'Canal 220-Canal_220_Potencia AC_InversorHuawei_[W] ' in header:
            if primer_canal_220 is None:
                # print(f"[INFO] Canal 220-Canal_220_Potencia AC_InversorHuawei_[W] ya existe en el archivo {i}")
                primer_canal_220 = i

            pass

        else:
            # Insertamos el canal 220 en el header
            idx = header.index("Canal 219-Canal_219_Ientradainversor_terracota_[A] ")
            header.insert(idx+1, "Canal 220-Canal_220_Potencia AC_InversorHuawei_[W] ")
            
            if 'Canal 420-Canal_420_101+102' in header:
                # Eliminamos el canal 420 del header (suma de canales 101+102, los cuales ya no se usan)
                header = header[:-1]
        
        # Creamos nueva lista con el header corregido (adaptado para todos)
        new_lt = []; new_lt.append(header); new_lt = new_lt + lt[1:]

        # Creamos el dataframe nuevo
        df = pd.DataFrame(new_lt)
        df = df[1:] # Elimina la primera fila (para no duplicar el encabezado)
        df.columns = header # Asigna nombres a las columnas

        # Eliminamos posibles columnas vacías
        if None in df.columns:
            df = df.drop(columns=[None])
            print(" [HECHO] Columnas vacías del dataframe eliminadas")
            
        DataLoggerDataFrame = pd.concat([DataLoggerDataFrame, df], axis=0, ignore_index=True)

        iter += 1
        # Mostrar progreso cada X archivos
        if (iter) % 30 == 0:  # Cada 30 archivos
            print(f"Procesados {iter+1}/{num_arch_analizables} archivos.")
    
    except Exception as e:
        print(f"ERROR procesando el archivo {i} - {type(e).__name__}")
        #print(f"     Mensaje: {str(e)}")
        # Agregamos el archivo fallido a la lista:
        fallo_lectura_arch.append({
            'nombre': i,
            'tipo_error': type(e).__name__,
            'mensaje_error': str(e)
            })
        continue

print("-" * 50)
print(f"Procesamiento del header completado! {iter} archivos en total.")
print(f"DataFrame creado: {DataLoggerDataFrame.shape[0]} filas x {DataLoggerDataFrame.shape[1]} columnas")
# El DataFrame se forma rellenando filas en las 83 columnas que vienen del Datalogger, una detrás de otra, un día de medidas detrás de otro

# Posible fallo de lectura en archivos
if fallo_lectura_arch:
    print("-" * 50)
    print(f"[WARNING] FALLO DE LECTURA EN {len(fallo_lectura_arch)} ARCHIVO(S):")
    for archivo in fallo_lectura_arch:
        print(f"   - {archivo['nombre']}")
        print(f"     Tipo de error: {archivo['tipo_error']}")
        print(f"     Mensaje de error: {archivo['mensaje_error']}")
else:
    print(f"[INFO] Todos los archivos se procesaron correctamente")


# Información canal 220
if primer_canal_220 is not None:
    print("-" * 50)
    print(f"[INFO] Primera aparición del canal 220 (Potencia AC Inversor Huawei): " + primer_canal_220)
    print(f"   A partir de ese archivo ya se loggea la información del inversor.")

# %%
