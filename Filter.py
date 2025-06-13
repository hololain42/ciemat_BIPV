#%%

from DatPlots import *  
from datetime import time

#%%

# Filtro para los datos de corriente de los paneles solares en serie
def filtro_corriente_serie(df):

    # Creamos una copia del DataFrame original y añadimos la columna 'filtrar' para determinar qué datos concretos
    # deben ser filtradas en el filtro general (filtro_DataLogger)
    df_filtrado = df.copy()
    df_filtrado['filtrar'] = False

    # Extraemos la hora del índice del DataFrame (datetime)
    if 'hora_dia' not in df_filtrado.columns:
        df_filtrado['hora_dia'] = pd.to_datetime(df_filtrado.index).hour
    
    #horas_diurnas = (df_filtrado['hora_dia'] >= 6) & (df_filtrado['hora_dia'] <= 20)
    
    # Para cada grupo, verificamos si la corriente es muy baja durante el día
    corrientes = [col for col in df_filtrado.columns if 'Im' in col]
    for panel in corrientes:
        umbral_corriente_min = 0 # Ajustar según las especificaciones de los paneles
        # marcamos como 'filtrar' = True las corrientes que cumplan esta condición (Im negativas)
        df_filtrado.loc[df_filtrado[panel] <= umbral_corriente_min, 'filtrar'] = True

    # Ahora calculamos la desviación estándar de las corrientes para cada momento (desviación estándar para cada fila de las corrientes)
    # En serie, todos los paneles deberían tener corrientes muy similares. Si los datos tienen desviación estándar alta, 
    # puede ser que haya problemas en algún panel. Marcamos esas filas para filtrar.
    df_filtrado["std_corriente"] = df_filtrado[corrientes].std(axis=1)
    umbral_corriente_std = 0.6
    df_filtrado.loc[df_filtrado["std_corriente"] > umbral_corriente_std, 'filtrar'] = True

    # Eliminamos las columnas auxiliares
    df_filtrado = df_filtrado.drop(columns=['hora_dia'])
    df_filtrado = df_filtrado.drop(columns=['std_corriente'])

    return df_filtrado


# Filtro para temperaturas irreales
def filtro_temperatura(df):

    df_filtrado = df.copy()

    temperaturas = [col for col in df_filtrado.columns if 'Temp' in col]

    for panel in temperaturas:

        temp_muy_baja = df_filtrado[panel] < -10  
        temp_muy_alta = df_filtrado[panel] > 85   
        
        df_filtrado.loc[temp_muy_baja | temp_muy_alta, 'filtrar'] = True

    return df_filtrado


# Detección de cambios bruscos en el voltaje y la corriente (por desconexiones entre paneles, problemas de sombreado, 
# problemas en el inversor, fallos eléctricos...)
def filtro_desconexiones(df, name):

    df_filtrado = df.copy()

    voltajes   = [col for col in df_filtrado.columns if 'Vm' in col]
    corrientes = [col for col in df_filtrado.columns if 'Im' in col]

    for vpanel, ipanel in zip(voltajes, corrientes):
        
        # Comprobamos la diferencia en valor absoluto con el valor inmediatamente anterior
        df_filtrado[f'delta_voltaje_{name}'] = df_filtrado[vpanel].diff().abs()
        df_filtrado[f'delta_corriente_{name}'] = df_filtrado[ipanel].diff().abs()
        
        umbral_cambio_voltaje = 15  
        umbral_cambio_corriente = 4  
        
        desconexion_v = df_filtrado[f'delta_voltaje_{name}'] > umbral_cambio_voltaje
        desconexion_i = df_filtrado[f'delta_corriente_{name}'] > umbral_cambio_corriente
        
        # Marcamos para filtrar la fila donde tenemos el cambio brusco
        df_filtrado.loc[desconexion_v | desconexion_i, 'filtrar'] = True

        # TODO: Este filtro es incompleto. Si el dato inmediatamente posterior al que filtramos también es anómalo, no va a ser detectado.
        # Es decir, si tenemos la secuencia 16.1 V, 16.4 V, 7 V, 6.5 V, 14 V... el único dato que marca este filtro es el de 7 V,
        # el de 6.5 V también cumple el requisito pero no está marcado. ¿Tal vez un filtro recursivo o porcentual?
    
    return df_filtrado


'''
Si bien el filtro de potencia funciona correctamente, evita casos donde la potencia AC
sea 0 ya que son eliminadas por el umbral superior, ocurre que para el array de Antracita
los valores de AC de salida son muy variables, tenemos muchos negativos (muy grandes que
también se presentan en Green y Terracota) pero solo se encuentran presentes en tres o cuatro días
en específico, lo que podría indicar que el microinversor (asociado al array Antracita) podría estar 
sufriendo algún desperfecto o, por otra parte, las vías de medida del datalogger para con el array de
Antracita requieren atención ya que marcan potencias de incluso más de 800 W lo cual no es correcto.
-- (REVISADO Y SOLUCIONADO: ERROR EN CABECERAS DEL DATALOGGER) --
'''

'''
Parece ser que el filtro de corriente sí logra filtrar los valores de corriente, y por lo tanto, la
potencia de los días que han tenido poca iluminación, pero en algunos casos donde el cambio es pronunciado
corta valores de corriente elevadas que incluso implican pérdidas puntuales de potencia de hasta 20 W.
A priori, esto no debería afectar de forma importante, aunque en la consideración de los cálculos solo tomaremos
los valores de energía diarios (integración de la curva de potencia). A nivel de cálculo mensual parece ser
que no afectará demasiado, aún así, debemos revisarlo --(TODO: SIN REVISAR)--
'''


# Filtro para eficiencias de los microinversores
def filtro_AC_DC(df):

    df_filtrado = df.copy()

    AC_DC_power = [col for col in df_filtrado.columns if 'Potencia' in col]
    # AC_DC_power es una lista que almacena los nombres de las columnas con potencia ['Potencia entrada (W)...', 'Potencia AC salida (W)...']

    # Eficiencia = Potencia_AC / Potencia_DC (ponemos NaN si fuese a dividir por 0)
    df_filtrado['Eficiencia'] = df_filtrado[AC_DC_power[1]] / df_filtrado[AC_DC_power[0]].where(df_filtrado[AC_DC_power[0]] != 0, np.nan)
 
    # Filtramos posibles errores en la detección de la potencia, fallos y pérdidas excesivas en los microinversores, etc
    eficiencia_baja = df_filtrado['Eficiencia'] < 0.5 # Típicamente 70-95% para microinversores, en este caso van un poco cortos así lo reducimos a 0.5
    eficiencia_alta = df_filtrado['Eficiencia'] > 1.1

    df_filtrado.loc[eficiencia_baja | eficiencia_alta , 'filtrar'] = True
    
    return df_filtrado


# Filtro para eliminar cualquier valor NaN o faltante
def filtro_nulos(df):

    df_filtrado = df.copy()

    columnas_criticas = [col for col in df_filtrado.columns if any(
        term in col for term in ['Vm', 'Im', 'Potencia'])]
    
    # Con .isna() detectamos valores NaN/None en cada fila de las columnas críticas (Vm, Im, Potencia) -> .any(axis=1)
    df_filtrado.loc[df_filtrado[columnas_criticas].isna().any(axis=1), 'filtrar'] = True

    return df_filtrado


# Función para aplicar todos los filtros
def filtro_DataLogger(df, name):

    df_filtrado = df.copy()
    df_filtrado = filtro_corriente_serie(df_filtrado)
    df_filtrado = filtro_temperatura(df_filtrado)
    df_filtrado = filtro_desconexiones(df_filtrado, name)
    df_filtrado = filtro_nulos(df_filtrado)
    df_filtrado = filtro_AC_DC(df_filtrado)

    #df_filtrado.loc[df_filtrado["filtrar"] == True, :] = np.nan
    df_filtrado = df_filtrado[~df_filtrado["filtrar"]].drop(columns=["filtrar"])
    # con df_filtrado[~df_filtrado["filtrar"]], solo conservamos las filas donde ~filtrar = True (~ es operador NOT)
    # Es decir, nos quedamos con las filas donde filtrar = False (las medidas que son buenas)

    # Eliminamos columnas auxiliares
    columnas_temporales = [col for col in df_filtrado.columns if any( term in col for term in ['delta_', 'voltaje_medio', 'voltaje_std', 'Eficiencia'])]
    df_filtrado = df_filtrado.drop(columns=columnas_temporales)

    return df_filtrado


##### FILTRADO PARA CADA TIPO DE TECNOLOGÍA DE PANELES SOLARES EN EL TEJADO #####

Antracita_filtered = filtro_DataLogger(Antracita, "Antracita")
Green_filtered     = filtro_DataLogger(Green, "Green")
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

# Submuestreo reduce la frecuencia de muestreo de los datos, convirtiendo medidas realizadas con alta frecuencia 
# en medidas promediadas y con menor frecuencia. Así reducimos el ruido manteniendo las tendencias principales.

def Submuestreo(df, subgroup=2):
    df = df.copy()
    
    # Aseguramos que el índice sea datetime
    if not pd.api.types.is_datetime64_any_dtype(df.index):
        df.index = pd.to_datetime(df.index)
    
    # Función para manejar valores NaN
    def nan_support(serie):
        if serie.isna().all():
            return np.nan
        return serie.dropna().mean() # promediamos los valores que no son NaN
    
    # Crear una columna auxiliar para agrupar por periodos de tiempo (definidos por subgroup, argumento de Submuestreo)
    # Por ejemplo: df.index.floor('2min') redondea hacia abajo al intervalo de 2 minutos más cercano
    df['grupo_tiempo'] = df.index.floor(f'{subgroup}min')
    
    # Usar groupby en lugar de resample
    # Para cada grupo de tiempo, aplica a función nan_support (que hace el promedio ignorando NaN) a cada columna.
    df_submuestreado = df.groupby('grupo_tiempo').apply(lambda x: x.apply(nan_support))
    
    # Eliminar la columna auxiliar si está en el resultado
    if 'grupo_tiempo' in df_submuestreado.columns:
        df_submuestreado = df_submuestreado.drop('grupo_tiempo', axis=1)
    
    # Establecer el índice correcto (limpiamos el MultiIndex que se ha creado antes en la función)
    if isinstance(df_submuestreado.index, pd.MultiIndex):
        df_submuestreado = df_submuestreado.droplevel(1)
    
    return df_submuestreado


Antracita_filtered = Submuestreo(Antracita_filtered)
Green_filtered     = Submuestreo(Green_filtered)
Terracota_filtered = Submuestreo(Terracota_filtered)

DataFrame_Irradiancia_Submuestreado = Submuestreo(DataFrame_Irradiancia)




#Antracita_filtered.interpolate(method='linear', inplace=True)
#Green_filtered.interpolate(method='linear', inplace=True)
#Terracota_filtered.interpolate(method='linear', inplace=True)

#Antracita_filtered.fillna(0, inplace = True)
#Green_filtered.fillna(0, inplace = True)
#Terracota_filtered.fillna(0, inplace = True)


# Determina si una hora está entre las 10:00 y 16:00 (horario solar útil)
def entre_horas(hora, hinicio=10, hfin=16):
    return (hora.time() >= time(hinicio, 0)) and (hora.time() <= time(hfin, 0))


# Rellenamos valores faltantes interpolando con los demás
def interpolate(DataFrame):

    df= DataFrame.copy()

    # Separación entre horarios día (10-16) y noche (fuera de 10-16)
    df_dia = df[df.index.map(entre_horas)]
    df_noche = df[~df.index.map(entre_horas)]

    df_dia_procesado = df_dia.copy()
    df_noche_procesado = df_noche.copy()

    colV = [col for col in df.columns if 'Vm' in col]
    colI = [col for col in df.columns if 'Im' in col]

    # interpolate rellena los valores NaN en el voltaje y la corriente usando interpolación lineal entre valores conocidos
    # solo procesamos los datos con horario de día
    for col in colV:
        df_dia_procesado[col] = df_dia[col].interpolate(method='linear')

    for col in colI:
        df_dia_procesado[col] = df_dia[col].interpolate(method='linear')

    # Reunificamos los datos en df_procesado, y todos los NaN restantes los pasamos a 0 con .fillna(0)
    df_procesado = pd.concat([df_dia_procesado, df_noche_procesado])
    df_procesado = df_procesado.sort_index()
    df_procesado.fillna(0, inplace = True)

    return df_procesado


# Eliminamos valores NaN, pasandolos a 0
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

    # solo procesamos los datos con horario de noche (NaN -> 0)
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
