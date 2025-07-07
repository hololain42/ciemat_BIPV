#%%

import numpy as np
import pandas as pd

#%%
"""
Aislamos la función de submuestreo en su propio archivo para facilitar la modularidad 
(tendremos que hacer submuestreos del dataset en distintos momentos, incluido antes de aplicar filtros)
"""

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

# Tiempo de submuestreo (en minutos)
tiempo_submuestreo = 5

def Submuestreo(df, subgroup=tiempo_submuestreo):
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

#%%
