#%%

#from Filter import Antracita_filtered, Green_filtered, Terracota_filtered
from Filter import *
import numpy as np
from datetime import time
import pvlib
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

#%%

# Informamos de que empiezan los cálculos del modelo de Ross
print(f"[INFO] Comienza el cálculo del modelo de Ross")
print("-" * 50)

### FILTROS PREVIOS ###

# Para los cálculos del modelo de Ross solo nos quedaremos con los datos que tengan G>400 W/m2 y datos razonables de temperatura ambiente
# TODO: Decidir si uso los datos del submuestreo o uso todos los datos? -> para lo cual habría que cambiar un par de cosas en Filter.py
#       (nombres especiales para Antracita_filtered antes del submuestreo, o cambiar los nombres de después)



# Filtro para irradiancias
#   El piranómetro de referencia capta la irradiancia global, y esto falsearía los resultados del modelo de Ross porque la irradiancia usada 
#   en los cálculos sería mayor que la que realmente reciben las células dada su orientación y sus pérdidas superficiales.
#   Vamos a filtrar con la célula calibrada de arriba, ya que tiene las mismas pérdidas angulares que los arrays de colores 

def filtro_irradiancias_400(df):

    # Creamos una copia del DataFrame original y añadimos la columna 'filtrar' para determinar qué datos concretos
    # deben ser filtradas en el filtro general (filtro_Ross)
    df_filtrado = df.copy()

    if 'filtrar' not in df_filtrado.columns:
        df_filtrado['filtrar'] = False

    # Búsqueda exacta de la columna, para que no coja también las columnas de temperatura de las células calibradas
    Irradiancias_Cel_Calib_400 = [col for col in df_filtrado.columns if col == 'Celula Calibrada Arriba']
        
    umbral_irradiancia_min = 400  # W/m2
    
    for panel in Irradiancias_Cel_Calib_400:

        # Contar valores antes del filtro
        valores_validos_antes = df_filtrado[panel].notna().sum()
        valores_bajos = (df_filtrado[panel] < umbral_irradiancia_min).sum()
        
        print(f"[DEBUG] {panel}: {valores_validos_antes} valores pasan el filtro, {valores_bajos} por debajo de {umbral_irradiancia_min} W/m2")
        
        # Marcar para filtrar las filas con irradiancias bajas (incluyendo NaN de forma segura)
        df_filtrado.loc[(df_filtrado[panel] < umbral_irradiancia_min) | df_filtrado[panel].isna(), 'filtrar'] = True

    return df_filtrado


# Filtro para temperaturas (temperaturas negativas, temperaturas con una desviación estándar demasiado alta 
# (todos los paneles deberían estar a mas o menos la misma temperatura al mismo tiempo)...)

def filtro_temperaturas(df):

    df_filtrado = df.copy()




    return df_filtrado


# Filtro para temperatura ambiente (nos quitamos cualquier error que puede haber en el registro de temperatura)

def filtro_ambiente(df):

    df_filtrado = df.copy()

    temperaturas = [col for col in df_filtrado.columns if 'Temp (C) Ambiente' in col]

    for panel in temperaturas:

        temp_muy_baja = df_filtrado[panel] < -10
        temp_muy_alta = df_filtrado[panel] > 50
        
        df_filtrado.loc[temp_muy_baja | temp_muy_alta, 'filtrar'] = True

            # Datos del 29 de noviembre de 2024 hasta el 3 de junio de 2025:
                # Media: 12.86 ºC
                # STD: 7.01 ºC
                # Max: 37.77 ºC
                # Min: -6.99 ºC

    return df_filtrado


# Filtro general para poder aplicar el modelo de Ross
def filtro_modelo_Ross(df, name):

    df_filtrado = df.copy()
    df_filtrado = filtro_irradiancias_400(df_filtrado)
    df_filtrado = filtro_temperaturas(df_filtrado)
    df_filtrado = filtro_ambiente(df_filtrado)
    # mas cosas

    #df_filtrado.loc[df_filtrado["filtrar"] == True, :] = np.nan

    df_filtrado = df_filtrado[~df_filtrado["filtrar"]].drop(columns=["filtrar"])
    
    # con df_filtrado[~df_filtrado["filtrar"]], solo conservamos las filas donde ~filtrar = True (~ es operador NOT)
    # Es decir, nos quedamos con las filas donde filtrar = False (las medidas que son buenas)

    return df_filtrado


##### FILTRADO PARA CADA TIPO DE TECNOLOGÍA DE PANELES SOLARES EN EL TEJADO #####

Antracita_filtered_Ross = filtro_modelo_Ross(Antracita_filtered, "Antracita")
Green_filtered_Ross     = filtro_modelo_Ross(Green_filtered, "Green")
Terracota_filtered_Ross = filtro_modelo_Ross(Terracota_filtered, "Terracota")

# Informamos de los filtros del Modelo de Ross
print(f"[INFO] Filtros del modelo de Ross aplicados")
print("-" * 50)

### TODA LA APLICACIÓN DEL MODELO DE ROSS A PARTIR DE AQUÍ ###

# T_cell = T_amb + (NOCT-20)*G/80
# G en mW/cm2

# Con T_cell, T_amb y G (célula calibrada de arriba) calculamos TONC de cada célula en cada instante
def modelo_Ross(df, tipo_celula, irradiancia_col="Celula Calibrada Arriba"):
    
    """
    Esta función calcula el NOCT de las células empleando el modelo de Ross
        T_cell = T_amb + (NOCT-20)*G/800
        G en W/m2
    
    Parámetros:
    df : pandas.DataFrame
        DataFrame con los datos (Green, Antracita, o Terracota)
    tipo_celula : str
        Tipo de célula: "Green", "Antracita", o "Terracota"
    irradiancia_col : str
        Columna de irradiancia a usar (por defecto: "Celula Calibrada Arriba")
    
    La función devuelve un dict con los resultados para las 4 células
    """

    resultados = {}

    for i in range(1, 5):

        # Nombres de las columnas, como por ejemplo "Temp 1 (C) Antracita"
        temp_celula_col = f"Temp {i} (C) {tipo_celula}"
        temp_ambiente_col = "Temp (C) Ambiente"
    
        # Creamos un DataFrame temporal eliminando datos con NaN si los hubiera
        df_temp = df[[temp_celula_col, temp_ambiente_col, irradiancia_col]].dropna()
        
        # Variables del modelo de Ross
        #   Variable dependiente (diferencia de temperaturas)
        df_temp['delta_T'] = df_temp[temp_celula_col] - df_temp[temp_ambiente_col]

        #   Variable independiente (irradiancia normalizada a 800 W/m2)
        df_temp['G_normalizada'] = df_temp[irradiancia_col]/800
        
        # Regresión lineal
        x = df_temp['G_normalizada'].values.reshape(-1, 1)
        y = df_temp['delta_T'].values
        
        model = LinearRegression()
        model.fit(x, y)

        # Resultados del modelo
        #   Calculamos el R^2 con la predicción y la real
        y_predict = model.predict(x) # predicciones del modelo para la diferencia de temperatura empleando la irradiancia normalizada
        r2 = r2_score(y, y_predict)


        #   Calculamos la NOCT efectiva de la célula i de este tipo
        pendiente = model.coef_[0]
        ordenada_origen = model.intercept_
        NOCT_eff = pendiente + 20

        ecuacion_ross = f"ΔT = {pendiente:.3f} × (G/800) + {ordenada_origen:.3f}"

        resultados[f"Celula_{i}"] = {
            'NOCT_eff': NOCT_eff,
            'R2': r2,
            'pendiente': pendiente,
            'intercepto': ordenada_origen,
            'ecuacion': ecuacion_ross
        }
        
    # Resumen de resultados
    print("-" * 50)
    print(f"RESULTADOS - {tipo_celula.upper()}")

    for celula, resultado in resultados.items():

        numero_celula = celula.split('_')[1]

        print(f"- Célula {numero_celula}:")
        print(f"    - NOCT (°C) = {resultado['NOCT_eff']:.2f}")
        print(f"    - $R^{2}$ = {resultado['R2']:.4f}")
        print(f"    - Ecuación de Ross: {resultado['ecuacion']}")

    return resultados


# Función para simular la temperatura de la célula en cada instante con el NOCT calculado en modelo_Ross
def simular_temperatura_celula(G_cel_arriba, T_ambiente, NOCT):
    '''
    Parámetros:
        T_ambiente (array): Array de las temperaturas ambiente medidas experimentalmente
        G_cel_arriba (array): Array de la irradiancia de la célula de arriba (ya filtrada)
        NOCT (float): Valor del NOCT calculado con la función modelo_Ross

    Devuelve:
        T_cell_sim (array): Valor de la temperatura de la célula simulada para cada instante
    '''
    # Según la documentación de pvlib, "This function expects irradiance in W/m2", aunque luego la convierte a mW/cm2
    # Por tanto no cambiaré nada de G_cell_arriba

    T_cell_sim = pvlib.temperature.ross(G_cel_arriba, T_ambiente, NOCT)

    return T_cell_sim


# Función para calcular el Mean Bias Error (MBE) entre los valores calculados de T_cell y los medidos realmente
def mean_bias_error(T_cell_real, T_cell_sim):
    '''
    Parámetros:
        T_cell_real (array): Array de las temperaturas medidas experimentalmente
        T_cell_sim (array): Array de los valores simulados con el NOCT calculado

    Devuelve:
        mbe (float): mean bias error
    '''

    T_cell_real = np.array(T_cell_real)
    T_cell_sim  = np.array(T_cell_sim)

    # reshape devuelve un array 2D, de forma que sea un número len(T_cell) de arrays con 1 elemento cada uno
    # Quedando de esta forma:
    # [[ 1]
    # [ 2]
    # (...)
    #  [12]]
    T_cell_real = T_cell_real.reshape(len(T_cell_real),1)
    T_cell_sim  = T_cell_sim.reshape(len(T_cell_sim),1)

    diff = (T_cell_real - T_cell_sim)
    mbe = diff.mean()

    return mbe


### RESULTADOS NOCT ###

resultados_antracita = modelo_Ross(Antracita_filtered_Ross, "Antracita")
resultados_green     = modelo_Ross(Green_filtered_Ross, "Green")
resultados_terracota = modelo_Ross(Terracota_filtered_Ross, "Terracota")

# TODO: Mirar como de desplazados entre sí están los valores obtenidos para cada tipo de célula (ver como el desplazamiento entre sí)
# TODO: Usar los datos del submuestreo? O usar los datos normales?
# TODO: Añadir un elapsed time y un dato final de cuántos archivos se han analizado
# TODO: Representar gráficamente todo
# TODO: Mejorar presentación del output en la terminal
#### Una de las green da un NOCT mas bajo que las demás porque está mucho más ventilada??
# %%
