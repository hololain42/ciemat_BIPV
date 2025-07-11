#%%

from Filter import *
from exportar_dataframe import mover_archivo
import numpy as np
import pvlib
import math
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from scipy import stats
from matplotlib.colors import LinearSegmentedColormap

#%%

# Informamos de que empiezan los cálculos del modelo de Ross
print(f"[INFO] Comienza el cálculo del modelo de Ross")
print("-" * 50)

### FILTROS PREVIOS ###

# Para los cálculos del modelo de Ross solo nos quedaremos con los datos que tengan G>400 W/m2 y datos razonables de temperatura ambiente

# Filtro para irradiancias
#   El piranómetro de referencia capta la irradiancia global, y esto falsearía los resultados del modelo de Ross porque la irradiancia usada 
#   en los cálculos sería mayor que la que realmente reciben las células dada su orientación y sus pérdidas superficiales.
#   Vamos a filtrar con la célula calibrada de arriba, ya que tiene las mismas pérdidas angulares que los arrays de colores 

print(f"[INFO] Filtro de irradiancia:")
def filtro_irradiancias_400(df):

    # Creamos una copia del DataFrame original y añadimos la columna 'filtrar' para determinar qué datos concretos
    # deben ser filtradas en el filtro general (filtro_Ross)
    df_filtrado = df.copy()

    if 'filtrar' not in df_filtrado.columns:
        df_filtrado['filtrar'] = False

    # Búsqueda exacta de la columna, para que no coja también las columnas de temperatura de las células calibradas
    Irradiancias_Cel_Calib_400 = [col for col in df_filtrado.columns if col == 'Celula Calibrada Arriba']
    Temperatura_Cel_Calib_400  = [col for col in df_filtrado.columns if col == 'Temp (C) Celula Calibrada Arriba']

    umbral_irradiancia_min = 400  # W/m2

    # Procesamos cada panel
    for panel in Irradiancias_Cel_Calib_400:

        # Contar valores antes del filtro
        valores_validos_antes = df_filtrado[panel].notna().sum()
        valores_bajos = (df_filtrado[panel] < umbral_irradiancia_min).sum()
        
        print(f"    -[DEBUG] {panel}: De {(valores_validos_antes):,} valores, solo {(valores_validos_antes-valores_bajos):,} superan el umbral de {umbral_irradiancia_min} W/m2")
        
        # Marcamos valores NaN de forma segura
        irrad_cel_calib_arriba_nan = df_filtrado[panel].isna()

        # Marcar para filtrar las filas con irradiancias bajas (incluyendo NaN de forma segura)
        df_filtrado.loc[(df_filtrado[panel] < umbral_irradiancia_min) | irrad_cel_calib_arriba_nan, 'filtrar'] = True

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
        temp_nan = df_filtrado[panel].isna()
        
        # Marcar para filtrar las filas con temperaturas ambientes altas y bajas (incluyendo NaN de forma segura)
        df_filtrado.loc[temp_muy_baja | temp_muy_alta | temp_nan, 'filtrar'] = True

            # Datos del 29 de noviembre de 2024 hasta el 3 de junio de 2025:
                # Media: 12.86 ºC
                # STD: 7.01 ºC
                # Max: 37.77 ºC
                # Min: -6.99 ºC

    return df_filtrado

# Función para comparar la irradiancia corregida y original de la célula calibrada (de arriba)
def plot_irradiancia_comparacion(df, df_filtrado):

    columna_irradiancia = 'Celula Calibrada Arriba'
    columna_temperatura = 'Temp (C) Celula Calibrada Arriba'

    if columna_irradiancia in df.columns and columna_irradiancia in df_filtrado.columns:
        mascara_validos = df[columna_irradiancia].notna() & df[columna_temperatura].notna()
        irradiancia_original = df.loc[mascara_validos, columna_irradiancia]
        irradiancia_corregida = df_filtrado.loc[mascara_validos, columna_irradiancia]

        fig = plt.figure(figsize=(10, 6))
        fig.canvas.manager.set_window_title('Irradiancia experimental vs corregida')
        plt.scatter(irradiancia_corregida, irradiancia_original, alpha=0.8)
        plt.plot([irradiancia_original.min(), irradiancia_original.max()],
             [irradiancia_original.min(), irradiancia_original.max()],
             'r--', label='y = x')
        plt.axvline(x = 400, color = 'xkcd:red orange', alpha=0.8, label = 'Umbral de irradiancia para calcular NOCT')
        plt.xlabel('Irradiancia corregida (W/m²)')
        plt.ylabel('Irradiancia experimental (W/m²)')
        plt.title(f'Irradiancia experimental frente a corregida')
        plt.legend(loc='best')
        plt.grid(True, alpha=0.7)

        plt.tight_layout()
        plt.gcf().savefig('figuras/RossModel_fit/ALL_Irradiancia_Exp_vs_Corregida.pdf', bbox_inches='tight')
        plt.gcf().savefig('figuras/RossModel_fit/png/ALL_Irradiancia_Exp_vs_Corregida.png', bbox_inches='tight')
        #plt.show()


# Filtro general para poder aplicar el modelo de Ross
def filtro_modelo_Ross(df, name):

    df_filtrado = df.copy()
    df_filtrado = filtro_irradiancias_400(df_filtrado)
    df_filtrado = filtro_temperaturas(df_filtrado)
    df_filtrado = filtro_ambiente(df_filtrado)
    # mas filtros

    # Realizar plot comparativo de las irradiancias antes y después de corregirse
    plot_irradiancia_comparacion(df, df_filtrado)

    #df_filtrado.loc[df_filtrado["filtrar"] == True, :] = np.nan

    df_filtrado = df_filtrado[~df_filtrado["filtrar"]].drop(columns=["filtrar"])
    
    # con df_filtrado[~df_filtrado["filtrar"]], solo conservamos las filas donde ~filtrar = True (~ es operador NOT)
    # Es decir, nos quedamos con las filas donde filtrar = False (las medidas que son buenas)

    return df_filtrado


##### FILTRADO PARA CADA TIPO DE TECNOLOGÍA DE PANELES SOLARES EN EL TEJADO #####

Antracita_filtered_sync_Submuestreado_Ross = filtro_modelo_Ross(Antracita_filtered_sync_Submuestreado, "Antracita")
Green_filtered_sync_Submuestreado_Ross     = filtro_modelo_Ross(Green_filtered_sync_Submuestreado, "Green")
Terracota_filtered_sync_Submuestreado_Ross = filtro_modelo_Ross(Terracota_filtered_sync_Submuestreado, "Terracota")

# Informamos de los filtros del Modelo de Ross
print("-" * 50)
print(f"[INFO] Filtros del modelo de Ross aplicados")

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
            'intercept_0': ordenada_origen,
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
        G_cel_arriba (numeric): Serie de pandas de la irradiancia de la célula de arriba (ya filtrada)
        T_ambiente (numeric): Serie de pandas de las temperaturas ambiente medidas experimentalmente
        NOCT (numeric): Valor del NOCT calculado con la función modelo_Ross

    Devuelve:
        T_cell_sim (numeric): Serie de pandas de la temperatura de la célula simulada para cada instante
    '''
    # Según la documentación de pvlib, "This function expects irradiance in W/m2", aunque luego la convierte a mW/cm2
    # Por tanto, no cambiaré nada de G_cell_arriba

    T_cell_sim = pvlib.temperature.ross(G_cel_arriba, T_ambiente, NOCT)

    return T_cell_sim


# Función para calcular el Mean Bias Error (MBE) entre los valores calculados de T_cell y los medidos realmente
def mean_bias_error_NOCT(T_cell_sim, T_cell_real):
    '''
    Parámetros:
        T_cell_sim (numeric): Serie de pandas de los valores simulados con el NOCT calculado
        T_cell_real (numeric): Serie de pandas de las temperaturas medidas experimentalmente

    Devuelve:
        mbe (float): mean bias error
    '''

    # Definido como "simulado - real" para que el signo sea coherente con el resto de la investigación
    diff = (T_cell_sim - T_cell_real)
    mbe = diff.mean()

    return mbe


# Función para calcular el Mean Absolute Error (MAE) entre los valores calculados de T_cell y los medidos realmente
def mean_absolute_error_NOCT(T_cell_sim, T_cell_real):
    '''
    Parámetros:
        T_cell_sim (numeric): Serie de pandas de los valores simulados con el NOCT calculado
        T_cell_real (numeric): Serie de pandas de las temperaturas medidas experimentalmente

    Devuelve:
        mae (float): mean bias error
    '''

    # Valor absoluto de "simulado - real"
    diff = abs(T_cell_sim - T_cell_real)
    mae = diff.mean()

    return mae


# Función para calcular el Root Mean Square Error (RMSE) entre los valores calculados de T_cell y los medidos realmente
def root_mean_square_error_NOCT(T_cell_sim, T_cell_real):
    '''
    Parámetros:
        T_cell_sim (numeric): Serie de pandas de los valores simulados con el NOCT calculado
        T_cell_real (numeric): Serie de pandas de las temperaturas medidas experimentalmente

    Devuelve:
        rmse (float): root mean square error
    '''

    # Raíz cuadrada del segundo momento de la muestra de las diferencias entre los valores previstos y los valores observados
    diff_cuad = (T_cell_sim - T_cell_real)**2
    rmse = math.sqrt(diff_cuad.mean())

    return rmse


### RESULTADOS NOCT ###

resultados_NOCT_Antracita = modelo_Ross(Antracita_filtered_sync_Submuestreado_Ross, "Antracita")
resultados_NOCT_Green     = modelo_Ross(Green_filtered_sync_Submuestreado_Ross, "Green")
resultados_NOCT_Terracota = modelo_Ross(Terracota_filtered_sync_Submuestreado_Ross, "Terracota")


### Temperaturas simuladas con el NOCT y MBE ###

# IMPORTANTE: Calculamos empleando los DataFrames filtered, no filtered_Ross
# De esta forma, validamos el modelo contra todos los datos, no solo los que tengan G>400 W/m2
# (que a priori son los que mejor deberían funcionar)


    #################
    ### ANTRACITA ###
    #################

metrics_Antracita = {}

for i in range(1, 5):

    # Nombre de la columna de la temperatura de la célula experimental
    temp_celula_col = f"Temp {i} (C) Antracita"

    # Nombre de la columna de la temperatura de la célula simulada con el NOCT obtenido
    temp_sim_celula_col = f"Temp_Sim {i} (C) Antracita"

    # Nombre de la columna Delta_T (T_cell_real-T_cell_sim) de la célula
    delta_temp_celula_col = f"Delta_T Celula {i} (C) Antracita"

    # Aplicamos la función para simular la temperatura de la célula con el NOCT obtenido
    # y guardamos el resultado en una columna específica
    Antracita_filtered_sync_Submuestreado[temp_sim_celula_col] = simular_temperatura_celula(
        Antracita_filtered_sync_Submuestreado['Celula Calibrada Arriba'],
        Antracita_filtered_sync_Submuestreado['Temp (C) Ambiente'],
        resultados_NOCT_Antracita[f'Celula_{i}']['NOCT_eff']
    )

    # Creamos una columna específica para la diferencia entre temperatura real y la simulada con el NOCT
    # Definido como "simulado - real" para que el signo sea coherente con el resto de la investigación
    Antracita_filtered_sync_Submuestreado[delta_temp_celula_col] = Antracita_filtered_sync_Submuestreado[temp_sim_celula_col] - Antracita_filtered_sync_Submuestreado[temp_celula_col]

    # Métricas estadísticas de la Antracita
    # Calculamos el Mean Bias Error y Mean Absolute Error de esa columna 
    # (lo hago con la función en vez de con .mean() directamente por si en algún momento cambio algo)
    metrics_Antracita[f"Celula_{i}"] = {
        'MBE': mean_bias_error_NOCT(Antracita_filtered_sync_Submuestreado[temp_sim_celula_col], Antracita_filtered_sync_Submuestreado[temp_celula_col]),
        'MAE': mean_absolute_error_NOCT(Antracita_filtered_sync_Submuestreado[temp_sim_celula_col], Antracita_filtered_sync_Submuestreado[temp_celula_col]),
        'RMSE': root_mean_square_error_NOCT(Antracita_filtered_sync_Submuestreado[temp_sim_celula_col], Antracita_filtered_sync_Submuestreado[temp_celula_col])
    }

print("-" * 50)
print("MÉTRICAS-ANTRACITA")
for celula, resultado in metrics_Antracita.items():

    numero_celula = celula.split('_')[1]

    print(f"- Célula {numero_celula}:")
    print(f"    - MBE (ºC) = {resultado['MBE']:.2f}")
    print(f"    - MAE (ºC) = {resultado['MAE']:.2f}")
    print(f"    - RMSE (ºC) = {resultado['RMSE']:.2f}")


    #################
    ###   GREEN   ###
    #################

metrics_Green = {}

for i in range(1, 5):

    # Nombre de la columna de la temperatura de la célula experimental
    temp_celula_col = f"Temp {i} (C) Green"

    # Nombre de la columna de la temperatura de la célula simulada con el NOCT obtenido
    temp_sim_celula_col = f"Temp_Sim {i} (C) Green"

    # Nombre de la columna Delta_T (T_cell_real-T_cell_sim) de la célula
    delta_temp_celula_col = f"Delta_T Celula {i} (C) Green"

    # Aplicamos la función para simular la temperatura de la célula con el NOCT obtenido
    # y guardamos el resultado en una columna específica
    Green_filtered_sync_Submuestreado[temp_sim_celula_col] = simular_temperatura_celula(
        Green_filtered_sync_Submuestreado['Celula Calibrada Arriba'],
        Green_filtered_sync_Submuestreado['Temp (C) Ambiente'],
        resultados_NOCT_Green[f'Celula_{i}']['NOCT_eff']
    )

    # Creamos una columna específica para la diferencia entre temperatura real y la simulada con el NOCT
    # Definido como "simulado - real" para que el signo sea coherente con el resto de la investigación
    Green_filtered_sync_Submuestreado[delta_temp_celula_col] = Green_filtered_sync_Submuestreado[temp_sim_celula_col] - Green_filtered_sync_Submuestreado[temp_celula_col]

    # Métricas estadísticas de la Green
    # Calculamos el Mean Bias Error y Mean Absolute Error de esa columna 
    # (lo hago con la función en vez de con .mean() directamente por si en algún momento cambio algo)
    metrics_Green[f"Celula_{i}"] = {
        'MBE': mean_bias_error_NOCT(Green_filtered_sync_Submuestreado[temp_sim_celula_col], Green_filtered_sync_Submuestreado[temp_celula_col]),
        'MAE': mean_absolute_error_NOCT(Green_filtered_sync_Submuestreado[temp_sim_celula_col], Green_filtered_sync_Submuestreado[temp_celula_col]),
        'RMSE': root_mean_square_error_NOCT(Green_filtered_sync_Submuestreado[temp_sim_celula_col], Green_filtered_sync_Submuestreado[temp_celula_col])
    }

print("-" * 50)
print("MÉTRICAS-GREEN")
for celula, resultado in metrics_Green.items():

    numero_celula = celula.split('_')[1]

    print(f"- Célula {numero_celula}:")
    print(f"    - MBE (ºC) = {resultado['MBE']:.2f}")
    print(f"    - MAE (ºC) = {resultado['MAE']:.2f}")
    print(f"    - RMSE (ºC) = {resultado['RMSE']:.2f}")


    #################
    ### TERRACOTA ###
    #################

metrics_Terracota = {}

for i in range(1, 5):

    # Nombre de la columna de la temperatura de la célula experimental
    temp_celula_col = f"Temp {i} (C) Terracota"

    # Nombre de la columna de la temperatura de la célula simulada con el NOCT obtenido
    temp_sim_celula_col = f"Temp_Sim {i} (C) Terracota"

    # Nombre de la columna Delta_T (T_cell_real-T_cell_sim) de la célula
    delta_temp_celula_col = f"Delta_T Celula {i} (C) Terracota"

    # Aplicamos la función para simular la temperatura de la célula con el NOCT obtenido
    # y guardamos el resultado en una columna específica
    Terracota_filtered_sync_Submuestreado[temp_sim_celula_col] = simular_temperatura_celula(
        Terracota_filtered_sync_Submuestreado['Celula Calibrada Arriba'],
        Terracota_filtered_sync_Submuestreado['Temp (C) Ambiente'],
        resultados_NOCT_Terracota[f'Celula_{i}']['NOCT_eff']
    )

    # Creamos una columna específica para la diferencia entre temperatura real y la simulada con el NOCT
    # Definido como "simulado - real" para que el signo sea coherente con el resto de la investigación
    Terracota_filtered_sync_Submuestreado[delta_temp_celula_col] = Terracota_filtered_sync_Submuestreado[temp_sim_celula_col] - Terracota_filtered_sync_Submuestreado[temp_celula_col]

    # Métricas estadísticas de la Terracota
    # Calculamos el Mean Bias Error y Mean Absolute Error de esa columna 
    # (lo hago con la función en vez de con .mean() directamente por si en algún momento cambio algo)
    metrics_Terracota[f"Celula_{i}"] = {
        'MBE': mean_bias_error_NOCT(Terracota_filtered_sync_Submuestreado[temp_sim_celula_col], Terracota_filtered_sync_Submuestreado[temp_celula_col]),
        'MAE': mean_absolute_error_NOCT(Terracota_filtered_sync_Submuestreado[temp_sim_celula_col], Terracota_filtered_sync_Submuestreado[temp_celula_col]),
        'RMSE': root_mean_square_error_NOCT(Terracota_filtered_sync_Submuestreado[temp_sim_celula_col], Terracota_filtered_sync_Submuestreado[temp_celula_col])
    }

print("-" * 50)
print("MÉTRICAS-TERRACOTA")
for celula, resultado in metrics_Terracota.items():

    numero_celula = celula.split('_')[1]

    print(f"- Célula {numero_celula}:")
    print(f"    - MBE (ºC) = {resultado['MBE']:.2f}")
    print(f"    - MAE (ºC) = {resultado['MAE']:.2f}")
    print(f"    - RMSE (ºC) = {resultado['RMSE']:.2f}")


def construir_dataframe_resultados(tipo_celula, resultados_NOCT, metrics):
    columnas = [f"Celula {celula.split('_')[1]}" for celula in resultados_NOCT.keys()]
    
    fila_NOCT    = [round(resultados_NOCT[celula]['NOCT_eff'], 2) for celula in resultados_NOCT]
    fila_R2_NOCT = [round(resultados_NOCT[celula]['R2'], 4) for celula in resultados_NOCT]
    fila_MBE     = [round(metrics[celula]['MBE'], 2) for celula in resultados_NOCT]
    fila_MAE     = [round(metrics[celula]['MAE'], 2) for celula in resultados_NOCT]
    fila_RMSE    = [round(metrics[celula]['RMSE'], 2) for celula in resultados_NOCT]

    df = pd.DataFrame(
        [fila_NOCT, fila_R2_NOCT, fila_MBE, fila_MAE, fila_RMSE],
        index=["NOCT (ºC)", "R2_NOCT", "MBE (ºC)", "MAE (ºC)", "RMSE(ºC)"],
        columns=columnas
    )

    # Añade MultiIndex en columnas para indicar el tipo de celula
    df.columns = pd.MultiIndex.from_product([[tipo_celula], df.columns])

    return df


# Construimos dataframes para cada tecnología
df_Antracita_excel  = construir_dataframe_resultados("Antracita", resultados_NOCT_Antracita, metrics_Antracita)
df_Green_excel      = construir_dataframe_resultados("Green", resultados_NOCT_Green, metrics_Green)
df_Terracota_excel  = construir_dataframe_resultados("Terracota", resultados_NOCT_Terracota, metrics_Terracota)

# Unimos horizontalmente
df_resultados_final = pd.concat([df_Antracita_excel, df_Green_excel, df_Terracota_excel], axis=1)

# Guardamos en Excel
nombre_archivo_resultados = f"Resultados_NOCT_Modelo_Ross_Inic_{fecha_solsticio}_Fin_{fecha_ultimo_arch}_Submuestreo_{tiempo_submuestreo}_min.xlsx"

with pd.ExcelWriter(nombre_archivo_resultados, engine='xlsxwriter') as writer:
    df_resultados_final.to_excel(writer, sheet_name='Resumen', startrow=0, merge_cells=True)

print("-" * 50)
print(f"[INFO] Archivo Excel con los resultados guardado como '{nombre_archivo_resultados}'.")

# Movemos el archivo al directorio adecuado
mover_archivo(nombre_archivo_resultados, "Excel Resultados/NOCT")



##### =============================== #####
##### PLOT AND REPRESENTATION SECTION #####
##### =============================== #####

# ====================================
# FIGURA TEMPERATURA 3 CÉLULAS
# ====================================
# Plots comparación temperaturas
fig_T_comp_3_cels = plt.figure(figsize=(10, 6))
fig_T_comp_3_cels.canvas.manager.set_window_title('Comparacion T simulada y real')
plt.ioff()  # Use non-interactive mode.

# Definimos objeto ax para distinguir entre figuras
ax_T_comp_3_cels = fig_T_comp_3_cels.add_subplot(111)
ax_T_comp_3_cels.set_title("Comparación entre la temperatura simulada con NOCT y la experimental", fontsize=12, fontweight='normal')

# ANTRACITA
ax_T_comp_3_cels.plot(Antracita_filtered_sync_Submuestreado["Temp 1 (C) Antracita"], Antracita_filtered_sync_Submuestreado["Temp_Sim 1 (C) Antracita"], linestyle="", marker= ".", label= "Antracita", color= "xkcd:charcoal grey")
ax_T_comp_3_cels.plot(Antracita_filtered_sync_Submuestreado["Temp 2 (C) Antracita"], Antracita_filtered_sync_Submuestreado["Temp_Sim 2 (C) Antracita"], linestyle="", marker= ".", color= "xkcd:charcoal grey")
ax_T_comp_3_cels.plot(Antracita_filtered_sync_Submuestreado["Temp 3 (C) Antracita"], Antracita_filtered_sync_Submuestreado["Temp_Sim 3 (C) Antracita"], linestyle="", marker= ".", color= "xkcd:charcoal grey")
ax_T_comp_3_cels.plot(Antracita_filtered_sync_Submuestreado["Temp 4 (C) Antracita"], Antracita_filtered_sync_Submuestreado["Temp_Sim 4 (C) Antracita"], linestyle="", marker= ".", color= "xkcd:charcoal grey")

# ANTRACITA - Regresión lineal
# Concatenar todos los datos de Antracita
x_ant = np.concatenate([Antracita_filtered_sync_Submuestreado["Temp 1 (C) Antracita"], 
                        Antracita_filtered_sync_Submuestreado["Temp 2 (C) Antracita"],
                        Antracita_filtered_sync_Submuestreado["Temp 3 (C) Antracita"],
                        Antracita_filtered_sync_Submuestreado["Temp 4 (C) Antracita"]])
y_ant = np.concatenate([Antracita_filtered_sync_Submuestreado["Temp_Sim 1 (C) Antracita"],
                        Antracita_filtered_sync_Submuestreado["Temp_Sim 2 (C) Antracita"],
                        Antracita_filtered_sync_Submuestreado["Temp_Sim 3 (C) Antracita"],
                        Antracita_filtered_sync_Submuestreado["Temp_Sim 4 (C) Antracita"]])

# Calcular regresión
slope_ant, intercept_ant, r_value_ant, p_value_ant, std_err_ant = stats.linregress(x_ant, y_ant)
line_ant = slope_ant * x_ant + intercept_ant
ax_T_comp_3_cels.plot(x_ant, line_ant, color="xkcd:steel grey", linestyle='-', alpha=0.8, linewidth=2, zorder=3)

# GREEN
ax_T_comp_3_cels.plot(Green_filtered_sync_Submuestreado["Temp 1 (C) Green"], Green_filtered_sync_Submuestreado["Temp_Sim 1 (C) Green"], linestyle="", marker= ".", label= "Green", color= "xkcd:leaf green")
ax_T_comp_3_cels.plot(Green_filtered_sync_Submuestreado["Temp 2 (C) Green"], Green_filtered_sync_Submuestreado["Temp_Sim 2 (C) Green"], linestyle="", marker= ".", color= "xkcd:leaf green")
ax_T_comp_3_cels.plot(Green_filtered_sync_Submuestreado["Temp 3 (C) Green"], Green_filtered_sync_Submuestreado["Temp_Sim 3 (C) Green"], linestyle="", marker= ".", color= "xkcd:leaf green")
ax_T_comp_3_cels.plot(Green_filtered_sync_Submuestreado["Temp 4 (C) Green"], Green_filtered_sync_Submuestreado["Temp_Sim 4 (C) Green"], linestyle="", marker= ".", color= "xkcd:leaf green")

# GREEN - Regresión lineal
x_green = np.concatenate([Green_filtered_sync_Submuestreado["Temp 1 (C) Green"],
                          Green_filtered_sync_Submuestreado["Temp 2 (C) Green"],
                          Green_filtered_sync_Submuestreado["Temp 3 (C) Green"],
                          Green_filtered_sync_Submuestreado["Temp 4 (C) Green"]])
y_green = np.concatenate([Green_filtered_sync_Submuestreado["Temp_Sim 1 (C) Green"],
                          Green_filtered_sync_Submuestreado["Temp_Sim 2 (C) Green"],
                          Green_filtered_sync_Submuestreado["Temp_Sim 3 (C) Green"],
                          Green_filtered_sync_Submuestreado["Temp_Sim 4 (C) Green"]])

slope_green, intercept_green, r_value_green, p_value_green, std_err_green = stats.linregress(x_green, y_green)
line_green = slope_green * x_green + intercept_green
ax_T_comp_3_cels.plot(x_green, line_green, color="xkcd:irish green", linestyle='-', alpha=0.8, linewidth=2, zorder=3)

# TERRACOTA
ax_T_comp_3_cels.plot(Terracota_filtered_sync_Submuestreado["Temp 1 (C) Terracota"], Terracota_filtered_sync_Submuestreado["Temp_Sim 1 (C) Terracota"], linestyle="", marker= ".", label= "Terracota", color= "xkcd:terracotta")
ax_T_comp_3_cels.plot(Terracota_filtered_sync_Submuestreado["Temp 2 (C) Terracota"], Terracota_filtered_sync_Submuestreado["Temp_Sim 2 (C) Terracota"], linestyle="", marker= ".", color= "xkcd:terracotta")
ax_T_comp_3_cels.plot(Terracota_filtered_sync_Submuestreado["Temp 3 (C) Terracota"], Terracota_filtered_sync_Submuestreado["Temp_Sim 3 (C) Terracota"], linestyle="", marker= ".", color= "xkcd:terracotta")
ax_T_comp_3_cels.plot(Terracota_filtered_sync_Submuestreado["Temp 4 (C) Terracota"], Terracota_filtered_sync_Submuestreado["Temp_Sim 4 (C) Terracota"], linestyle="", marker= ".", color= "xkcd:terracotta")

# TERRACOTA - Regresión lineal
x_terra = np.concatenate([Terracota_filtered_sync_Submuestreado["Temp 1 (C) Terracota"],
                          Terracota_filtered_sync_Submuestreado["Temp 2 (C) Terracota"],
                          Terracota_filtered_sync_Submuestreado["Temp 3 (C) Terracota"],
                          Terracota_filtered_sync_Submuestreado["Temp 4 (C) Terracota"]])
y_terra = np.concatenate([Terracota_filtered_sync_Submuestreado["Temp_Sim 1 (C) Terracota"],
                          Terracota_filtered_sync_Submuestreado["Temp_Sim 2 (C) Terracota"],
                          Terracota_filtered_sync_Submuestreado["Temp_Sim 3 (C) Terracota"],
                          Terracota_filtered_sync_Submuestreado["Temp_Sim 4 (C) Terracota"]])

slope_terra, intercept_terra, r_value_terra, p_value_terra, std_err_terra = stats.linregress(x_terra, y_terra)
line_terra = slope_terra * x_terra + intercept_terra
ax_T_comp_3_cels.plot(x_terra, line_terra, color="xkcd:tangerine", linestyle='-', alpha=0.8, linewidth=2, zorder=3)


ax_T_comp_3_cels.set_xlabel('Temperatura experimental (ºC)')
ax_T_comp_3_cels.set_ylabel('Temperatura simulada (ºC)')
ax_T_comp_3_cels.legend(loc='best')
ax_T_comp_3_cels.grid(True, alpha=0.7)

fig_T_comp_3_cels.tight_layout()
fig_T_comp_3_cels.savefig('figuras/RossModel_fit/Temp_sim_VS_Temp_real_ALL_Celulas.pdf', bbox_inches='tight')
fig_T_comp_3_cels.savefig('figuras/RossModel_fit/png/Temp_sim_VS_Temp_real_ALL_Celulas.png', bbox_inches='tight')
fig_T_comp_3_cels.show()

# ====================================
# FIGURA INDIVIDUAL - ANTRACITA
# ====================================
fig_ant_ind = plt.figure(figsize=(10, 6))
fig_ant_ind.canvas.manager.set_window_title('Antracita - T simulada vs real')
ax_ant_ind = fig_ant_ind.add_subplot(111)
ax_ant_ind.set_title("Antracita - Temperatura simulada vs experimental", fontsize=12, fontweight='normal')

# Plot datos
ax_ant_ind.plot(Antracita_filtered_sync_Submuestreado["Temp 1 (C) Antracita"], Antracita_filtered_sync_Submuestreado["Temp_Sim 1 (C) Antracita"], linestyle="", marker= ".", label= "Célula 1", color= "xkcd:charcoal grey")
ax_ant_ind.plot(Antracita_filtered_sync_Submuestreado["Temp 2 (C) Antracita"], Antracita_filtered_sync_Submuestreado["Temp_Sim 2 (C) Antracita"], linestyle="", marker= ".", label= "Célula 2", color= "xkcd:dark grey")
ax_ant_ind.plot(Antracita_filtered_sync_Submuestreado["Temp 3 (C) Antracita"], Antracita_filtered_sync_Submuestreado["Temp_Sim 3 (C) Antracita"], linestyle="", marker= ".", label= "Célula 3", color= "xkcd:grey")
ax_ant_ind.plot(Antracita_filtered_sync_Submuestreado["Temp 4 (C) Antracita"], Antracita_filtered_sync_Submuestreado["Temp_Sim 4 (C) Antracita"], linestyle="", marker= ".", label= "Célula 4", color= "xkcd:light grey")

# Regresión lineal
ax_ant_ind.plot(x_ant, line_ant, color="xkcd:steel grey", linestyle='-', alpha=0.8, linewidth=2, zorder=3, 
           label=f'R²={r_value_ant**2:.3f}')

ax_ant_ind.set_xlabel('Temperatura experimental (ºC)')
ax_ant_ind.set_ylabel('Temperatura simulada (ºC)')
ax_ant_ind.legend(loc='best')
ax_ant_ind.grid(True, alpha=0.7)

fig_ant_ind.tight_layout()
fig_ant_ind.savefig('figuras/RossModel_fit/Temp_sim_VS_Temp_real_Antracita.pdf', bbox_inches='tight')
fig_ant_ind.savefig('figuras/RossModel_fit/png/Temp_sim_VS_Temp_real_Antracita.png', bbox_inches='tight')
fig_ant_ind.show()

# ====================================
# FIGURA INDIVIDUAL - GREEN
# ====================================
fig_green_ind = plt.figure(figsize=(10, 6))
fig_green_ind.canvas.manager.set_window_title('Green - T simulada vs real')
ax_green_ind = fig_green_ind.add_subplot(111)
ax_green_ind.set_title("Green - Temperatura simulada vs experimental", fontsize=12, fontweight='normal')

# Plot datos
ax_green_ind.plot(Green_filtered_sync_Submuestreado["Temp 1 (C) Green"], Green_filtered_sync_Submuestreado["Temp_Sim 1 (C) Green"], linestyle="", marker= ".", label= "Célula 1", color= "xkcd:leaf green")
ax_green_ind.plot(Green_filtered_sync_Submuestreado["Temp 2 (C) Green"], Green_filtered_sync_Submuestreado["Temp_Sim 2 (C) Green"], linestyle="", marker= ".", label= "Célula 2", color= "xkcd:forest green")
ax_green_ind.plot(Green_filtered_sync_Submuestreado["Temp 3 (C) Green"], Green_filtered_sync_Submuestreado["Temp_Sim 3 (C) Green"], linestyle="", marker= ".", label= "Célula 3", color= "xkcd:green")
ax_green_ind.plot(Green_filtered_sync_Submuestreado["Temp 4 (C) Green"], Green_filtered_sync_Submuestreado["Temp_Sim 4 (C) Green"], linestyle="", marker= ".", label= "Célula 4", color= "xkcd:lime green")

# Regresión lineal
ax_green_ind.plot(x_green, line_green, color="xkcd:irish green", linestyle='-', alpha=0.8, linewidth=2, zorder=3,
                 label=f'R²={r_value_green**2:.3f}')

ax_green_ind.set_xlabel('Temperatura experimental (ºC)')
ax_green_ind.set_ylabel('Temperatura simulada (ºC)')
ax_green_ind.legend(loc='best')
ax_green_ind.grid(True, alpha=0.7)

fig_green_ind.tight_layout()
fig_green_ind.savefig('figuras/RossModel_fit/Temp_sim_VS_Temp_real_Green.pdf', bbox_inches='tight')
fig_green_ind.savefig('figuras/RossModel_fit/png/Temp_sim_VS_Temp_real_Green.png', bbox_inches='tight')
fig_green_ind.show()

# ====================================
# FIGURA INDIVIDUAL - TERRACOTA
# ====================================
fig_terra_ind = plt.figure(figsize=(10, 6))
fig_terra_ind.canvas.manager.set_window_title('Terracota - T simulada vs real')
ax_terra_ind = fig_terra_ind.add_subplot(111)
ax_terra_ind.set_title("Terracota - Temperatura simulada vs experimental", fontsize=12, fontweight='normal')

# Plot datos
ax_terra_ind.plot(Terracota_filtered_sync_Submuestreado["Temp 1 (C) Terracota"], Terracota_filtered_sync_Submuestreado["Temp_Sim 1 (C) Terracota"], linestyle="", marker= ".", label= "Célula 1", color= "xkcd:terracotta")
ax_terra_ind.plot(Terracota_filtered_sync_Submuestreado["Temp 2 (C) Terracota"], Terracota_filtered_sync_Submuestreado["Temp_Sim 2 (C) Terracota"], linestyle="", marker= ".", label= "Célula 2", color= "xkcd:burnt orange")
ax_terra_ind.plot(Terracota_filtered_sync_Submuestreado["Temp 3 (C) Terracota"], Terracota_filtered_sync_Submuestreado["Temp_Sim 3 (C) Terracota"], linestyle="", marker= ".", label= "Célula 3", color= "xkcd:orange")
ax_terra_ind.plot(Terracota_filtered_sync_Submuestreado["Temp 4 (C) Terracota"], Terracota_filtered_sync_Submuestreado["Temp_Sim 4 (C) Terracota"], linestyle="", marker= ".", label= "Célula 4", color= "xkcd:peach")

# Regresión lineal
ax_terra_ind.plot(x_terra, line_terra, color="xkcd:tangerine", linestyle='-', alpha=0.8, linewidth=2, zorder=3,
                 label=f'R²={r_value_terra**2:.3f}')

ax_terra_ind.set_xlabel('Temperatura experimental (ºC)')
ax_terra_ind.set_ylabel('Temperatura simulada (ºC)')
ax_terra_ind.legend(loc='best')
ax_terra_ind.grid(True, alpha=0.7)

fig_terra_ind.tight_layout()
fig_terra_ind.savefig('figuras/RossModel_fit/Temp_sim_VS_Temp_real_Terracota.pdf', bbox_inches='tight')
fig_terra_ind.savefig('figuras/RossModel_fit/png/Temp_sim_VS_Temp_real_Terracota.png', bbox_inches='tight')
fig_terra_ind.show()


# ======================================
# FIGURAS DENSIDAD DE PUNTOS HEXAGONALES
# ======================================
# Crear colormap según la densidad (azul suave -> azul oscuro -> amarillo -> rojo -> rojo oscuro)
colors = ['lightsteelblue', 'cornflowerblue', 'royalblue', 'yellow', 'orange', 'red', 'darkred']
n_bins = 256
cmap_custom = LinearSegmentedColormap.from_list('density', colors, N=n_bins)

# ====================================
# FIGURA DENSIDAD - ANTRACITA (HEX)
# ====================================
fig_densidad_hex_ant = plt.figure(figsize=(10, 6))
fig_densidad_hex_ant.canvas.manager.set_window_title('Antracita - Densidad de puntos hexagonal')
ax_densidad_hex_ant = fig_densidad_hex_ant.add_subplot(111)

# Concatenar todos los datos de Antracita
x_ant_all = x_ant
y_ant_all = y_ant

# Crear plot de densidad 2D hexagonal
hb_ant = ax_densidad_hex_ant.hexbin(x_ant_all, y_ant_all, gridsize=30, cmap=cmap_custom, mincnt=1)
cb_hex = plt.colorbar(hb_ant, ax=ax_densidad_hex_ant, label='Número de puntos')

# Añadir regresión lineal como referencia
x_sorted = np.sort(x_ant_all)
line_sorted = slope_ant * x_sorted + intercept_ant
ax_densidad_hex_ant.plot(x_sorted, line_sorted, color='white', linestyle='--', linewidth=2,
               label=f'R²={r_value_ant**2:.3f}')

ax_densidad_hex_ant.set_xlabel('Temperatura experimental (°C)')
ax_densidad_hex_ant.set_ylabel('Temperatura simulada (°C)')
ax_densidad_hex_ant.set_title('Antracita - Densidad de puntos: Temperatura simulada vs experimental',
                    fontsize=12, fontweight='normal')
ax_densidad_hex_ant.legend(loc='best')
ax_densidad_hex_ant.grid(True, alpha=0.3)

fig_densidad_hex_ant.tight_layout()
fig_densidad_hex_ant.savefig('figuras/RossModel_fit/Hexbin_Temp_sim_VS_Temp_real_Antracita.pdf', bbox_inches='tight')
fig_densidad_hex_ant.savefig('figuras/RossModel_fit/png/Hexbin_Temp_sim_VS_Temp_real_Antracita.png', bbox_inches='tight')
fig_densidad_hex_ant.show()

# ====================================
# FIGURA DENSIDAD - GREEN (HEX)
# ====================================
fig_densidad_hex_green = plt.figure(figsize=(10, 6))
fig_densidad_hex_green.canvas.manager.set_window_title('Green - Densidad de puntos hexagonal')
ax_densidad_hex_green = fig_densidad_hex_green.add_subplot(111)

# Concatenar todos los datos de green
x_green_all = x_green
y_green_all = y_green

# Crear plot de densidad 2D hexagonal
hb_green = ax_densidad_hex_green.hexbin(x_green_all, y_green_all, gridsize=30, cmap=cmap_custom, mincnt=1)
cb_hex = plt.colorbar(hb_green, ax=ax_densidad_hex_green, label='Número de puntos')

# Añadir regresión lineal como referencia
x_sorted = np.sort(x_green_all)
line_sorted = slope_green * x_sorted + intercept_green
ax_densidad_hex_green.plot(x_sorted, line_sorted, color='white', linestyle='--', linewidth=2,
               label=f'R²={r_value_green**2:.3f}')

ax_densidad_hex_green.set_xlabel('Temperatura experimental (°C)')
ax_densidad_hex_green.set_ylabel('Temperatura simulada (°C)')
ax_densidad_hex_green.set_title('Green - Densidad de puntos: Temperatura simulada vs experimental',
                    fontsize=12, fontweight='normal')
ax_densidad_hex_green.legend(loc='best')
ax_densidad_hex_green.grid(True, alpha=0.3)

fig_densidad_hex_green.tight_layout()
fig_densidad_hex_green.savefig('figuras/RossModel_fit/Hexbin_Temp_sim_VS_Temp_real_Green.pdf', bbox_inches='tight')
fig_densidad_hex_green.savefig('figuras/RossModel_fit/png/Hexbin_Temp_sim_VS_Temp_real_Green.png', bbox_inches='tight')
fig_densidad_hex_green.show()

# ====================================
# FIGURA DENSIDAD - TERRACOTA (HEX)
# ====================================
fig_densidad_hex_terra = plt.figure(figsize=(10, 6))
fig_densidad_hex_terra.canvas.manager.set_window_title('Terracota - Densidad de puntos hexagonal')
ax_densidad_hex_terra = fig_densidad_hex_terra.add_subplot(111)

# Concatenar todos los datos de Terracota
x_terra_all = x_terra
y_terra_all = y_terra

# Crear plot de densidad 2D hexagonal
hb_terra = ax_densidad_hex_terra.hexbin(x_terra_all, y_terra_all, gridsize=30, cmap=cmap_custom, mincnt=1)
cb_hex = plt.colorbar(hb_terra, ax=ax_densidad_hex_terra, label='Número de puntos')

# Añadir regresión lineal como referencia
x_sorted = np.sort(x_terra_all)
line_sorted = slope_terra * x_sorted + intercept_terra
ax_densidad_hex_terra.plot(x_sorted, line_sorted, color='white', linestyle='--', linewidth=2,
               label=f'R²={r_value_terra**2:.3f}')

ax_densidad_hex_terra.set_xlabel('Temperatura experimental (°C)')
ax_densidad_hex_terra.set_ylabel('Temperatura simulada (°C)')
ax_densidad_hex_terra.set_title('Terracota - Densidad de puntos: Temperatura simulada vs experimental',
                    fontsize=12, fontweight='normal')
ax_densidad_hex_terra.legend(loc='best')
ax_densidad_hex_terra.grid(True, alpha=0.3)

fig_densidad_hex_terra.tight_layout()
fig_densidad_hex_terra.savefig('figuras/RossModel_fit/Hexbin_Temp_sim_VS_Temp_real_Terracota.pdf', bbox_inches='tight')
fig_densidad_hex_terra.savefig('figuras/RossModel_fit/png/Hexbin_Temp_sim_VS_Temp_real_Terracota.png', bbox_inches='tight')
fig_densidad_hex_terra.show()


# Imprimir estadísticas de las regresiones lineales

print(f"Antracita Ross - Total puntos: {len(x_ant)}")
print(f"Antracita: R² = {r_value_ant**2:.3f}, pendiente = {slope_ant:.3f}")

print(f"Green Ross - Total puntos: {len(x_green)}")
print(f"Green: R² = {r_value_green**2:.3f}, pendiente = {slope_green:.3f}")

print(f"Terracota Ross - Total puntos: {len(x_terra)}")
print(f"Terracota: R² = {r_value_terra**2:.3f}, pendiente = {slope_terra:.3f}")
print("-" * 50)

# IMPORTANTÍSIMO
# TODO: Corregir los datos de irradiancia de las células calibradas, cambiar de sitio la función que corrige

# TODO: las filas del delta T empiezan desde bastante pronto por la mañana, seguro que ya hay 400 W/m2?
# TODO: hay mucha diferencia (delta T grande) pronto por la mañana... ¿por qué? representar Delta T para ver esto
# TODO: Mirar como de desplazados entre sí están los valores obtenidos para cada tipo de célula (ver como el desplazamiento entre sí)
# TODO: Representar gráficamente todo (también el Delta_T, para ver cuanto es más diferente y cuando se parece más a lo largo de los meses y las horas)
# TODO: Mejorar presentación del output en la terminal
#### Una de las green da un NOCT mas bajo que las demás porque está mucho más ventilada??
# %%
