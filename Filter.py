#%%

from DatPlots import *  
from datetime import time

#%%

def filtro_corriente_serie(df):

    df_filtrado = df.copy()
    df_filtrado['filtrar'] = False

    if 'hora_dia' not in df_filtrado.columns:
        df_filtrado['hora_dia'] = pd.to_datetime(df_filtrado.index).hour
    
    #horas_diurnas = (df_filtrado['hora_dia'] >= 6) & (df_filtrado['hora_dia'] <= 20)
    
    # Para cada grupo, verificamos si la corriente es muy baja durante el día
    corrientes = [col for col in df_filtrado.columns if 'Im' in col]
    for panel in corrientes:  
        umbral_corriente_min = 0 # Ajustar según las especificaciones de los paneles
        df_filtrado.loc[df_filtrado[panel] <= umbral_corriente_min, 'filtrar'] = True

    umbral_corriente_std = 0.6

    df_filtrado["std_corriente"] = df_filtrado[corrientes].std(axis=1)
    df_filtrado.loc[df_filtrado["std_corriente"] > umbral_corriente_std, 'filtrar'] = True

    df_filtrado = df_filtrado.drop(columns=['hora_dia'])
    df_filtrado = df_filtrado.drop(columns=['std_corriente'])

    return df_filtrado


def filtro_temperatura(df):

    df_filtrado = df.copy()

    temperaturas = [col for col in df_filtrado.columns if 'Temp' in col]

    for panel in temperaturas:

        temp_muy_baja = df_filtrado[panel] < -10  
        temp_muy_alta = df_filtrado[panel] > 85   
        
        df_filtrado.loc[temp_muy_baja | temp_muy_alta, 'filtrar'] = True

    return df_filtrado

def filtro_desconexiones(df, name):

    df_filtrado = df.copy()

    voltajes   = [col for col in df_filtrado.columns if 'Vm' in col]
    corrientes = [col for col in df_filtrado.columns if 'Im' in col]

    for vpanel, ipanel in zip(voltajes, corrientes):
        
        df_filtrado[f'delta_voltaje_{name}'] = df_filtrado[vpanel].diff().abs()
        df_filtrado[f'delta_corriente_{name}'] = df_filtrado[ipanel].diff().abs()
        
        umbral_cambio_voltaje = 15  
        umbral_cambio_corriente = 4  
        
        desconexion_v = df_filtrado[f'delta_voltaje_{name}'] > umbral_cambio_voltaje
        desconexion_i = df_filtrado[f'delta_corriente_{name}'] > umbral_cambio_corriente
        
        df_filtrado.loc[desconexion_v | desconexion_i, 'filtrar'] = True
    
    return df_filtrado




'''
Si bien el filtro de potencia funciona correctamente, evita casos donde la potencia AC
sea 0 ya que son eliminadas por el umbral superior, ocurre que para el array de Antracita
los valores de AC de salida son muy variables, tenemos muchos negativos (muy grandes que
también se presentan en Green y Terracota) pero solo se encuentran presentes en tres o cuatro días
en específico, lo que podría indicar que el microinversor (asociado al array Antracita) podría estar 
sufriendo algún despefecto o, por otra parte, las vías de medida del datalogger para con el array de
Antracita requieren atención ya que marcan potencias de incluso más de 800 W lo cual no es correcto.
-- (REVISADO Y SOLUCIONADO: ERROR EN CABECERAS DEL DATALOGGER) --
'''

'''
Parece ser que el filtro de corriente sí logra filtrar los valores de corriente, y por lo tanto,
potencia de los días que han tenido poca iluminación pero en algunos casos donde el cambio es pronunciado,
corta valores de corriente elevadas que incluso implican pérdidas puntuales de potencia de hasta 20 W
que, a priori, no debería afectar de forma importante si la consideración de los cálculos solo tomaremos
los valores de energía diarios (integración de la curva de potencia). A nivel de cálculo mensual parece ser
que no afectará demasiado, aún así, debemos revisarlo   --(SIN REVISAR)--
'''


def filtro_AC_DC(df):

    df_filtrado = df.copy()

    AC_DC_power = [col for col in df_filtrado.columns if 'Potencia' in col]

    df_filtrado['Eficiencia'] = df_filtrado[AC_DC_power[1]] / df_filtrado[AC_DC_power[0]].where(df_filtrado[AC_DC_power[0]] != 0, np.nan)
 
    eficiencia_baja = df_filtrado['Eficiencia'] < -1  # Típicamente 70-95% para microinversores
    eficiencia_alta = df_filtrado['Eficiencia'] > 1.1

    df_filtrado.loc[eficiencia_baja | eficiencia_alta , 'filtrar'] = True
    
    return df_filtrado



def filtro_nulos(df):

    df_filtrado = df.copy()

    columnas_criticas = [col for col in df_filtrado.columns if any(
        term in col for term in ['Vm', 'Im', 'Potencia'])]
    
    df_filtrado.loc[df_filtrado[columnas_criticas].isna().any(axis=1), 'filtrar'] = True

    return df_filtrado



def filtro_DataLogger(df, name):

    df_filtrado = df.copy()
    df_filtrado = filtro_corriente_serie(df_filtrado)
    df_filtrado = filtro_temperatura(df_filtrado)
    df_filtrado = filtro_desconexiones(df_filtrado, name)
    df_filtrado = filtro_nulos(df_filtrado)
    df_filtrado = filtro_AC_DC(df_filtrado)

    #df_filtrado.loc[df_filtrado["filtrar"] == True, :] = np.nan
    df_filtrado = df_filtrado[~df_filtrado["filtrar"]].drop(columns=["filtrar"])
    columnas_temporales = [col for col in df_filtrado.columns if any( term in col for term in ['delta_', 'voltaje_medio', 'voltaje_std', 'Eficiencia'])]
    df_filtrado = df_filtrado.drop(columns=columnas_temporales)
    return df_filtrado


##### FILTRADO PARA CADA TIPO DE TECNOLOGÍA DE PANELES SOLARES EN EL TEJADO #####

Antracita_filtered = filtro_DataLogger(Antracita, "Antracita")
Green_filtered = filtro_DataLogger(Green, "Green")
Terracota_filtered = filtro_DataLogger(Terracota, "Terracota")


#%%

#def Submuestreo(df, subgroup=2):
#
#    df = df.copy()
#    if not pd.api.types.is_datetime64_any_dtype(df.index):
#        df.index = pd.to_datetime(df.index)
#    
#    def nan_support(serie):
#        if serie.isna().all():
#            return np.nan
#        return serie.dropna().mean()
#    
#    df_submuestreado = df.resample(f'{subgroup}min').apply(nan_support)
#    
#    return df_submuestreado


def Submuestreo(df, subgroup=2):
    df = df.copy()
    
    # Aseguramos que el índice sea datetime
    if not pd.api.types.is_datetime64_any_dtype(df.index):
        df.index = pd.to_datetime(df.index)
    
    # Función para manejar valores NaN
    def nan_support(serie):
        if serie.isna().all():
            return np.nan
        return serie.dropna().mean()
    
    # Crear una columna auxiliar para agrupar por periodos de tiempo
    df['grupo_tiempo'] = df.index.floor(f'{subgroup}min')
    
    # Usar groupby en lugar de resample
    df_submuestreado = df.groupby('grupo_tiempo').apply(lambda x: x.apply(nan_support))
    
    # Eliminar la columna auxiliar si está en el resultado
    if 'grupo_tiempo' in df_submuestreado.columns:
        df_submuestreado = df_submuestreado.drop('grupo_tiempo', axis=1)
    
    # Establecer el índice correcto
    if isinstance(df_submuestreado.index, pd.MultiIndex):
        df_submuestreado = df_submuestreado.droplevel(1)
    
    return df_submuestreado


Antracita_filtered = Submuestreo(Antracita_filtered)
Green_filtered = Submuestreo(Green_filtered)
Terracota_filtered = Submuestreo(Terracota_filtered)

DataFrame_Irradiancia_Submuestreado = Submuestreo(DataFrame_Irradiancia)




#Antracita_filtered.interpolate(method='linear', inplace=True)
#Green_filtered.interpolate(method='linear', inplace=True)
#Terracota_filtered.interpolate(method='linear', inplace=True)

#Antracita_filtered.fillna(0, inplace = True)
#Green_filtered.fillna(0, inplace = True)
#Terracota_filtered.fillna(0, inplace = True)



def entre_horas(hora, hinicio=10, hfin=16):
    return (hora.time() >= time(hinicio, 0)) and (hora.time() <= time(hfin, 0))

def interpolate(DataFrame):

    df= DataFrame.copy()

    df_dia = df[df.index.map(entre_horas)]
    df_noche = df[~df.index.map(entre_horas)]

    df_dia_procesado = df_dia.copy()
    df_noche_procesado = df_noche.copy()

    colV = [col for col in df.columns if 'Vm' in col]
    colI = [col for col in df.columns if 'Im' in col]

    for col in colV:
        df_dia_procesado[col] = df_dia[col].interpolate(method='linear')

    for col in colI:
        df_dia_procesado[col] = df_dia[col].interpolate(method='linear')

    df_procesado = pd.concat([df_dia_procesado, df_noche_procesado])
    df_procesado = df_procesado.sort_index()
    df_procesado.fillna(0, inplace = True)
    return df_procesado

def zeros(DataFrame):
    df= DataFrame.copy()

    df_dia = df[df.index.map(entre_horas)]
    df_noche = df[~df.index.map(entre_horas)]

    df_dia_procesado = df_dia.copy()
    df_noche_procesado = df_noche.copy()

    colV = [col for col in df.columns if 'Vm' in col]
    colI = [col for col in df.columns if 'Im' in col]
    colEntradaDC = [col for col in df.columns if 'entrada' in col]
    colSalidaAC = [col for col in df.columns if 'salida' in col]

    for col in colV:
        df_noche_procesado[col] = df_noche[col].fillna(0)

    for col in colI:
        df_noche_procesado[col] = df_noche[col].fillna(0)

    for col in colEntradaDC:
        df_noche_procesado[col] = df_noche[col].fillna(0)

    for col in colSalidaAC:
        df_noche_procesado[col] = df_noche[col].fillna(0)

    df_procesado = pd.concat([df_dia_procesado, df_noche_procesado])
    df_procesado = df_procesado.sort_index()
    return df_procesado


# %%
