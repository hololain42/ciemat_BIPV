#%%
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import os 
import chardet
#%%

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
hace tiempoo, entonces se corregirán las cabeceras para ambos casos.

Si bien José corrigió la no existencia del canal 220, no estoy seguro si al añadir un canal ocasione
un desplazamiento en las cabeceras, es decir, aumentando en 1 el número de cabeceras por encima del número
de registros (debido a la presencia del canal 420 el cual no es relevante en lo absoluto). 

La corrección realizanda en el programa solventa ambas situaciones y dejará evaluar sin problemas los
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
print(path)
Dataloggerfiles = os.listdir(path+"/Datos Datalogger/DAQ970A")

DataLoggerDataFrame = pd.DataFrame()

for i in Dataloggerfiles[30:]:
    with open("Datos Datalogger/DAQ970A/" + i, 'r', encoding='latin1') as f:
        columns = f.readlines()
    lt = [o.strip().split('\t') for o in columns]
    header = lt[0]

    if 'Canal 220-Canal_220_Potencia AC_InversorHuawei_[W] ' in header:
        pass
    else:
        idx = header.index("Canal 219-Canal_219_Ientradainversor_terracota_[A] ")
        header.insert(idx+1, "Canal 220-Canal_220_Potencia AC_InversorHuawei_[W] ")
        if 'Canal 420-Canal_420_101+102' in header:
            header = header[:-1]
    
    new_lt = []; new_lt.append(header); new_lt = new_lt + lt[1:]

    df = pd.DataFrame(new_lt)
    df = df[1:]
    df.columns = header

    if None in df.columns:
        df = df.drop(columns=[None])
        
    DataLoggerDataFrame = pd.concat([DataLoggerDataFrame, df], axis=0, ignore_index=True)


 

# %%
