#%%

from DatPlots import *
from submuestreo import Submuestreo, tiempo_submuestreo
from exportar_dataframe import combinar_dataframes_con_fechas_distintas, mover_archivo
from histograma_irradiacion import generar_histograma_irradiacion
from datetime import time

#%%

# Informamos de que comienza la aplicación de filtros
print(f"[INFO] Comienza la aplicación de filtros")
print("-" * 50)

# Filtro para los datos de corriente de los paneles solares en serie
def filtro_corriente_serie(df):

    # Creamos una copia del DataFrame original y añadimos la columna 'filtrar' para determinar qué datos concretos
    # deben ser filtradas en el filtro general (filtro_DataLogger)
    df_filtrado = df.copy()

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


def filtrar_irradiancias_similares(df, tolerancia, umbral_minimo, G_1='Celula Calibrada Arriba', 
                                   G_2='Celula Calibrada Abajo', G_3='Celula Calibrada Izquierda'):
    
    """
    Filtra filas donde la diferencia entre el máximo y mínimo valor es menor al % de tolerancia
    Se hace así porque calcula min y max una sola vez y usa esos valores como referencia, no una columna concreta, ya que si la
    diferencia entre el valor máximo y mínimo es ≤ 5-10% del mínimo, entonces todas las diferencias por pares de columnas serán ≤ 5-10%
    
    Parámetros:
    - df: DataFrame de Pandas con los valores de la célula de color concreto
    - tolerancia: Máxima diferencia posible entre valores de la irradiancia
    - umbral_minimo (W/m2): Valor mínimo de irradiancia para aplicar el filtro.
    - G_1, G_2, G_3: Columnas del DataFrame donde se guarda la irradiancia de las tres células calibradas
    
    ->Imponemos un umbral mínimo para desechar valores de ruido o erróneos. Además, como estaríamos dividiendo por números pequeños 
    en el cálculo de las irradiancias similares, puede dar lugar a problemas.
    
    """

    df_filtrado = df.copy()

    # Encontrar valores min y max para cada fila de irradiancia
    valores_irradiancia = df_filtrado[[G_1, G_2, G_3]]
    min_val_G = valores_irradiancia.min(axis=1)
    max_val_G = valores_irradiancia.max(axis=1)

    # Condiciones mínimas para aplicar el filtro
    condiciones_validas = (
        (min_val_G > 0) &  # Evitar valores negativos
        (min_val_G >= umbral_minimo)  # Evitar valores muy pequeños que pueden dar problemas al dividir
    )

    # La diferencia relativa debe ser menor a la tolerancia
    irradiancias_similares = condiciones_validas & ((max_val_G - min_val_G) / min_val_G > tolerancia)

    df_filtrado.loc[irradiancias_similares | ~condiciones_validas, 'filtrar'] = True
    
    return df_filtrado


def filtro_quitar_huecos(df):

    """
    Aplicar este filtro si se quiere quitar todas las filas en las que haya algun valor vacío.
    """

    df_filtrado = df.copy()

    # Eliminar filas que tengan cualquier valor faltante
    df_filtrado = df_filtrado.dropna(how='any') 

    return df_filtrado


# Función para aplicar todos los filtros
def filtro_DataLogger(df, name):

    df_filtrado = df.copy()
    df_filtrado['filtrar'] = False

    # Ejecutamos los filtros en un orden específico
    # 1. FILTROS DE VALIDACIÓN (eliminan datos claramente inválidos)
    df_filtrado = filtro_nulos(df_filtrado)  # Elimina NaN/None
    df_filtrado = filtro_temperatura(df_filtrado)  # Elimina temperaturas físicamente imposibles

    # 2. FILTRO DE IRRADIANCIA, que las irradiancias de las células sean similares
    df_filtrado = filtrar_irradiancias_similares(df_filtrado, tolerancia=0.05, umbral_minimo=20)
    
    # 3. FILTRO DE MEDIDAS ELÉCTRICAS
    df_filtrado = filtro_corriente_serie(df_filtrado)

    # 4. FILTRO DE DETECCIÓN DE ANOMALÍAS en el conexionado eléctrico
    df_filtrado = filtro_desconexiones(df_filtrado, name)

    # 5. FILTRO DE EFICIENCIA MÍNIMA/MÁXIMA
    df_filtrado = filtro_AC_DC(df_filtrado)

    df_filtrado = df_filtrado[~df_filtrado["filtrar"]].drop(columns=["filtrar"])
    # con df_filtrado[~df_filtrado["filtrar"]], solo conservamos las filas donde ~filtrar = True (~ es operador NOT)
    # Es decir, nos quedamos con las filas donde filtrar = False (las medidas que son buenas)

    # Eliminamos columnas auxiliares
    columnas_temporales = [col for col in df_filtrado.columns if any( term in col for term in ['delta_', 'voltaje_medio', 'voltaje_std', 'Eficiencia'])]
    df_filtrado = df_filtrado.drop(columns=columnas_temporales)

    # Por último, quitamos todas las filas con huecos que puedan haber quedado
    filtro_quitar_huecos(df_filtrado)

    return df_filtrado


##### FILTRADO PARA CADA TIPO DE TECNOLOGÍA DE PANELES SOLARES EN EL TEJADO #####

Antracita_filtered = filtro_DataLogger(Antracita, "Antracita")
Green_filtered     = filtro_DataLogger(Green, "Green")
Terracota_filtered = filtro_DataLogger(Terracota, "Terracota")

# Informamos de que todos los filtros han sido aplicados
print(f"[INFO] Todos los filtros aplicados")
print("-" * 50)

# Conteo del número de datos, para comparar la actuación de los filtros
print(f"-Datos de Antracita tras los filtros: {len(Antracita_filtered):,} filas")
print(f"-Datos de Green tras los filtros: {len(Green_filtered):,} filas")
print(f"-Datos de Terracota tras los filtros: {len(Terracota_filtered):,} filas")
print("-" * 50)


def sincronizar_dataframes(*dataframes, datetime_col='Datetime'):
    """
    Sincroniza múltiples DataFrames para que tengan exactamente las mismas filas
    basándose en la columna de datetime y eliminando filas con valores faltantes

    Lo hacemos para asegurarnos de que estamos comparando la producción energética de cada color en completa igualdad de condiciones,
    es decir, que todas las células tengan el mismo número de datos para comparar, ya que tras el filtro algunas células tienen 
    más datos y por lo tanto van a sumar más potencia

    """

    # Establecer datetime como índice si no lo es
    dfs = []
    for df in dataframes:
        if datetime_col in df.columns:
            df_temp = df.set_index(datetime_col)
        else:
            df_temp = df.copy()
        dfs.append(df_temp)
    
    # Encontrar índices comunes
    indices_comunes = dfs[0].index
    for df in dfs[1:]:
        indices_comunes = indices_comunes.intersection(df.index)
    
    # Filtrar todos los DataFrames
    dfs_sincronizados = []
    for df in dfs:
        df_sync = df.loc[indices_comunes]
        # Eliminar filas con valores faltantes
        df_sync = df_sync.dropna()
        dfs_sincronizados.append(df_sync)
    
    # Encontrar los índices finales comunes después de dropna
    indices_finales = dfs_sincronizados[0].index
    for df in dfs_sincronizados[1:]:
        indices_finales = indices_finales.intersection(df.index)
    
    # Aplicar filtro final
    resultado = [df.loc[indices_finales] for df in dfs_sincronizados]
    
    return resultado

# Aplicamos la sincronización
Antracita_filtered_sync, Green_filtered_sync, Terracota_filtered_sync = sincronizar_dataframes(
    Antracita_filtered, Green_filtered, Terracota_filtered)

# Informamos de que la sincronización se ha llevado a cabo
print(f"[INFO] Sincronización de DataFrames realizada")
print("-" * 50)


# Verificar que todos tengan el mismo número de filas e índices
print(f"-Datos de Antracita tras la sincronización: {len(Antracita_filtered_sync):,} filas")
print(f"-Datos de Green tras la sincronización: {len(Green_filtered_sync):,} filas")
print(f"-Datos de Terracota tras la sincronización: {len(Terracota_filtered_sync):,} filas")

# Verificar que los índices sean exactamente los mismos
print(f"-->¿Índices iguales tras la sincronización?: {Antracita_filtered_sync.index.equals(Green_filtered_sync.index) and Green_filtered_sync.index.equals(Terracota_filtered_sync.index)}")
print("-" * 50)


#%%

# Informamos de que comienza el submuestreo
print(f"[INFO] Comienza el submuestreo de datos filtrados y sincronizados, se agruparán los datos cada {tiempo_submuestreo} minutos.")
print("-" * 50)

Antracita_filtered_sync_Submuestreado = Submuestreo(Antracita_filtered_sync)
Green_filtered_sync_Submuestreado     = Submuestreo(Green_filtered_sync)
Terracota_filtered_sync_Submuestreado = Submuestreo(Terracota_filtered_sync)

DataFrame_Irradiancia_Submuestreado   = Submuestreo(DataFrame_Irradiancia)

# Informamos de que el submuestreo ha sido terminado
print(f"[INFO] Submuestreo completado, los datos se han agrupado cada {tiempo_submuestreo} minutos.")
print("-" * 50)

# Conteo del número de datos, para comparar la actuación de los filtros
print(f"-Datos de Antracita filtrados y submuestrados: {len(Antracita_filtered_sync_Submuestreado):,} filas")
print(f"-Datos de Green filtrados y submuestrados: {len(Green_filtered_sync_Submuestreado):,} filas")
print(f"-Datos de Terracota filtrados y submuestrados: {len(Terracota_filtered_sync_Submuestreado):,} filas")
print("-" * 50)

# Volcamos todos los datos submuestrados y filtrados a un archivo antes de aplicarle cualquier filtro
nombre_archivo_filtrado = f"Datos_filtrados_Datalogger_DAQ970A_Inic_{fecha_solsticio}_Fin_{fecha_ultimo_arch}_Submuestreo_{tiempo_submuestreo}_min.xlsx"

# Combinamos los DataFrames filtrados de Antracita, Green y Terracota con el orden específico en un solo archivo
archivo_datalogger_filtrado = combinar_dataframes_con_fechas_distintas(Antracita_filtered_sync_Submuestreado, 
                                                                       Green_filtered_sync_Submuestreado, 
                                                                       Terracota_filtered_sync_Submuestreado, 
                                                                       nombre_archivo_filtrado)

# Movemos el archivo al directorio adecuado
mover_archivo(nombre_archivo_filtrado, "Excel Resultados/Datos Submuestreados")


### Generamos un histograma con la irradiación FILTRADA Y SINCRONIZADA de la célula de arriba

# Meses (descomentar el del año entero si se tienen suficientes datos)
# meses = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
meses = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun']

titulo = 'Irradiación mensual sobre la célula calibrada de arriba (datos filtrados)'
mostrar_grafico = False

fig_hist_G_arriba_filtered, valores_hist_G_arriba_filtered = generar_histograma_irradiacion(Antracita_filtered_sync_Submuestreado, tiempo_submuestreo, meses, titulo, mostrar_grafico, col_irradiancia='Celula Calibrada Arriba')

fig_hist_G_arriba_filtered.savefig(f'figuras/Histogramas_Irradiacion/Hist_Irradiacion_CelCalib_Arriba_FILTRADOS_SYNC_{meses[0]}_a_{meses[-1]}_Submuestreo_{tiempo_submuestreo}.pdf', dpi=300, bbox_inches='tight')
fig_hist_G_arriba_filtered.savefig(f'figuras/Histogramas_Irradiacion/png/Hist_Irradiacion_CelCalib_Arriba_FILTRADOS_SYNC_{meses[0]}_a_{meses[-1]}_Submuestreo_{tiempo_submuestreo}.png', dpi=300, bbox_inches='tight')
plt.close(fig_hist_G_arriba_filtered)

# %%


"""
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
"""


# %%
