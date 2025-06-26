#%%

from Filter import *
import numpy as np
from datetime import time
import pvlib
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from scipy import stats

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
    
    print("-" * 50)
    print(f"[INFO] Filtro de irradiancia:")

    for panel in Irradiancias_Cel_Calib_400:

        # Contar valores antes del filtro
        valores_validos_antes = df_filtrado[panel].notna().sum()
        valores_bajos = (df_filtrado[panel] < umbral_irradiancia_min).sum()
        
        print(f"    -[DEBUG] {panel}: De {valores_validos_antes} valores, solo {valores_validos_antes-valores_bajos} superan el umbral de {umbral_irradiancia_min} W/m2")
        
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
def mean_bias_error(T_cell_real, T_cell_sim):
    '''
    Parámetros:
        T_cell_real (numeric): Serie de pandas de las temperaturas medidas experimentalmente
        T_cell_sim (numeric): Serie de pandas de los valores simulados con el NOCT calculado

    Devuelve:
        mbe (float): mean bias error
    '''

    diff = (T_cell_real - T_cell_sim)
    mbe = diff.mean()

    return mbe


### RESULTADOS NOCT ###

resultados_NOCT_Antracita = modelo_Ross(Antracita_filtered_Ross, "Antracita")
resultados_NOCT_Green     = modelo_Ross(Green_filtered_Ross, "Green")
resultados_NOCT_Terracota = modelo_Ross(Terracota_filtered_Ross, "Terracota")


### Temperaturas simuladas con el NOCT y MBE ###

# IMPORTANTE: Calculamos empleando los DataFrames filtered, no filtered_Ross
# De esta forma, validamos el modelo contra todos los datos, no solo los que tengan G>400 W/m2
# (que a priori son los que mejor deberían funcionar)


    #################
    ### ANTRACITA ###
    #################

mbe_Antracita = {}

for i in range(1, 5):

    # Nombre de la columna de la temperatura de la célula experimental
    temp_celula_col = f"Temp {i} (C) Antracita"

    # Nombre de la columna de la temperatura de la célula simulada con el NOCT obtenido
    temp_sim_celula_col = f"Temp_Sim {i} (C) Antracita"

    # Nombre de la columna Delta_T (T_cell_real-T_cell_sim) de la célula
    delta_temp_celula_col = f"Delta_T Celula {i} (C) Antracita"

    # Aplicamos la función para simular la temperatura de la célula con el NOCT obtenido
    # y guardamos el resultado en una columna específica
    Antracita_filtered[temp_sim_celula_col] = simular_temperatura_celula(
        Antracita_filtered['Celula Calibrada Arriba'],
        Antracita_filtered['Temp (C) Ambiente'],
        resultados_NOCT_Antracita[f'Celula_{i}']['NOCT_eff']
    )

    # Creamos una columna específica para la diferencia entre temperatura real y la simulada con el NOCT
    Antracita_filtered[delta_temp_celula_col] = Antracita_filtered[temp_celula_col] - Antracita_filtered[temp_sim_celula_col]

    # Calculamos el Mean Bias Error de esa columna (lo hago con la función en vez de con .mean() directamente por si en algún momento cambio algo)
    mbe_Antracita[f"Celula_{i}"] = {
        'MBE': mean_bias_error(Antracita_filtered[temp_celula_col], Antracita_filtered[temp_sim_celula_col])
    }

print("-" * 50)
print("MBE-ANTRACITA")
for celula, resultado in mbe_Antracita.items():

    numero_celula = celula.split('_')[1]

    print(f"- Célula {numero_celula}:")
    print(f"    - MBE (ºC) = {resultado['MBE']:.2f}")


    #################
    ###   GREEN   ###
    #################

mbe_Green = {}

for i in range(1, 5):

    # Nombre de la columna de la temperatura de la célula experimental
    temp_celula_col = f"Temp {i} (C) Green"

    # Nombre de la columna de la temperatura de la célula simulada con el NOCT obtenido
    temp_sim_celula_col = f"Temp_Sim {i} (C) Green"

    # Nombre de la columna Delta_T (T_cell_real-T_cell_sim) de la célula
    delta_temp_celula_col = f"Delta_T Celula {i} (C) Green"

    # Aplicamos la función para simular la temperatura de la célula con el NOCT obtenido
    # y guardamos el resultado en una columna específica
    Green_filtered[temp_sim_celula_col] = simular_temperatura_celula(
        Green_filtered['Celula Calibrada Arriba'],
        Green_filtered['Temp (C) Ambiente'],
        resultados_NOCT_Green[f'Celula_{i}']['NOCT_eff']
    )

    # Creamos una columna específica para la diferencia entre temperatura real y la simulada con el NOCT
    Green_filtered[delta_temp_celula_col] = Green_filtered[temp_celula_col] - Green_filtered[temp_sim_celula_col]

    # Calculamos el Mean Bias Error de esa columna (lo hago con la función en vez de con .mean() directamente por si en algún momento cambio algo)
    mbe_Green[f"Celula_{i}"] = {
        'MBE': mean_bias_error(Green_filtered[temp_celula_col], Green_filtered[temp_sim_celula_col])
    }

print("-" * 50)
print("MBE-GREEN")
for celula, resultado in mbe_Green.items():

    numero_celula = celula.split('_')[1]

    print(f"- Célula {numero_celula}:")
    print(f"    - MBE (ºC) = {resultado['MBE']:.2f}")


    #################
    ### TERRACOTA ###
    #################

mbe_Terracota = {}

for i in range(1, 5):

    # Nombre de la columna de la temperatura de la célula experimental
    temp_celula_col = f"Temp {i} (C) Terracota"

    # Nombre de la columna de la temperatura de la célula simulada con el NOCT obtenido
    temp_sim_celula_col = f"Temp_Sim {i} (C) Terracota"

    # Nombre de la columna Delta_T (T_cell_real-T_cell_sim) de la célula
    delta_temp_celula_col = f"Delta_T Celula {i} (C) Terracota"

    # Aplicamos la función para simular la temperatura de la célula con el NOCT obtenido
    # y guardamos el resultado en una columna específica
    Terracota_filtered[temp_sim_celula_col] = simular_temperatura_celula(
        Terracota_filtered['Celula Calibrada Arriba'],
        Terracota_filtered['Temp (C) Ambiente'],
        resultados_NOCT_Terracota[f'Celula_{i}']['NOCT_eff']
    )

    # Creamos una columna específica para la diferencia entre temperatura real y la simulada con el NOCT
    Terracota_filtered[delta_temp_celula_col] = Terracota_filtered[temp_celula_col] - Terracota_filtered[temp_sim_celula_col]

    # Calculamos el Mean Bias Error de esa columna (lo hago con la función en vez de con .mean() directamente por si en algún momento cambio algo)
    mbe_Terracota[f"Celula_{i}"] = {
        'MBE': mean_bias_error(Terracota_filtered[temp_celula_col], Terracota_filtered[temp_sim_celula_col])
    }

print("-" * 50)
print("MBE-TERRACOTA")
for celula, resultado in mbe_Terracota.items():

    numero_celula = celula.split('_')[1]

    print(f"- Célula {numero_celula}:")
    print(f"    - MBE (ºC) = {resultado['MBE']:.2f}")



# Plots comparación temperaturas
fig_T_comp = plt.figure(figsize=(10, 6))
fig_T_comp.canvas.manager.set_window_title('Comparacion T simulada y real')
plt.ioff()  # Use non-interactive mode.

# Definimos objeto ax para distinguir entre figuras
ax_T_comp = fig_T_comp.add_subplot(111)
ax_T_comp.set_title("Comparación entre la temperatura simulada con NOCT y la experimental", fontsize=12, fontweight='normal')

# ANTRACITA
ax_T_comp.plot(Antracita_filtered["Temp 1 (C) Antracita"], Antracita_filtered["Temp_Sim 1 (C) Antracita"], linestyle="", marker= ".", label= "Antracita", color= "xkcd:charcoal grey")
ax_T_comp.plot(Antracita_filtered["Temp 2 (C) Antracita"], Antracita_filtered["Temp_Sim 2 (C) Antracita"], linestyle="", marker= ".", color= "xkcd:charcoal grey")
ax_T_comp.plot(Antracita_filtered["Temp 3 (C) Antracita"], Antracita_filtered["Temp_Sim 3 (C) Antracita"], linestyle="", marker= ".", color= "xkcd:charcoal grey")
ax_T_comp.plot(Antracita_filtered["Temp 4 (C) Antracita"], Antracita_filtered["Temp_Sim 4 (C) Antracita"], linestyle="", marker= ".", color= "xkcd:charcoal grey")

# ANTRACITA - Regresión lineal
# Concatenar todos los datos de Antracita
x_ant = np.concatenate([Antracita_filtered["Temp 1 (C) Antracita"], 
                        Antracita_filtered["Temp 2 (C) Antracita"],
                        Antracita_filtered["Temp 3 (C) Antracita"],
                        Antracita_filtered["Temp 4 (C) Antracita"]])
y_ant = np.concatenate([Antracita_filtered["Temp_Sim 1 (C) Antracita"],
                        Antracita_filtered["Temp_Sim 2 (C) Antracita"],
                        Antracita_filtered["Temp_Sim 3 (C) Antracita"],
                        Antracita_filtered["Temp_Sim 4 (C) Antracita"]])

# Calcular regresión
slope_ant, intercept_ant, r_value_ant, p_value_ant, std_err_ant = stats.linregress(x_ant, y_ant)
line_ant = slope_ant * x_ant + intercept_ant
ax_T_comp.plot(x_ant, line_ant, color="xkcd:steel grey", linestyle='-', alpha=0.8, linewidth=2, zorder=3)

# GREEN
ax_T_comp.plot(Green_filtered["Temp 1 (C) Green"], Green_filtered["Temp_Sim 1 (C) Green"], linestyle="", marker= ".", label= "Green", color= "xkcd:leaf green")
ax_T_comp.plot(Green_filtered["Temp 2 (C) Green"], Green_filtered["Temp_Sim 2 (C) Green"], linestyle="", marker= ".", color= "xkcd:leaf green")
ax_T_comp.plot(Green_filtered["Temp 3 (C) Green"], Green_filtered["Temp_Sim 3 (C) Green"], linestyle="", marker= ".", color= "xkcd:leaf green")
ax_T_comp.plot(Green_filtered["Temp 4 (C) Green"], Green_filtered["Temp_Sim 4 (C) Green"], linestyle="", marker= ".", color= "xkcd:leaf green")

# GREEN - Regresión lineal
x_green = np.concatenate([Green_filtered["Temp 1 (C) Green"],
                          Green_filtered["Temp 2 (C) Green"],
                          Green_filtered["Temp 3 (C) Green"],
                          Green_filtered["Temp 4 (C) Green"]])
y_green = np.concatenate([Green_filtered["Temp_Sim 1 (C) Green"],
                          Green_filtered["Temp_Sim 2 (C) Green"],
                          Green_filtered["Temp_Sim 3 (C) Green"],
                          Green_filtered["Temp_Sim 4 (C) Green"]])

slope_green, intercept_green, r_value_green, p_value_green, std_err_green = stats.linregress(x_green, y_green)
line_green = slope_green * x_green + intercept_green
ax_T_comp.plot(x_green, line_green, color="xkcd:irish green", linestyle='-', alpha=0.8, linewidth=2, zorder=3)

# TERRACOTA
ax_T_comp.plot(Terracota_filtered["Temp 1 (C) Terracota"], Terracota_filtered["Temp_Sim 1 (C) Terracota"], linestyle="", marker= ".", label= "Terracota", color= "xkcd:terracotta")
ax_T_comp.plot(Terracota_filtered["Temp 2 (C) Terracota"], Terracota_filtered["Temp_Sim 2 (C) Terracota"], linestyle="", marker= ".", color= "xkcd:terracotta")
ax_T_comp.plot(Terracota_filtered["Temp 3 (C) Terracota"], Terracota_filtered["Temp_Sim 3 (C) Terracota"], linestyle="", marker= ".", color= "xkcd:terracotta")
ax_T_comp.plot(Terracota_filtered["Temp 4 (C) Terracota"], Terracota_filtered["Temp_Sim 4 (C) Terracota"], linestyle="", marker= ".", color= "xkcd:terracotta")

# TERRACOTA - Regresión lineal
x_terra = np.concatenate([Terracota_filtered["Temp 1 (C) Terracota"],
                          Terracota_filtered["Temp 2 (C) Terracota"],
                          Terracota_filtered["Temp 3 (C) Terracota"],
                          Terracota_filtered["Temp 4 (C) Terracota"]])
y_terra = np.concatenate([Terracota_filtered["Temp_Sim 1 (C) Terracota"],
                          Terracota_filtered["Temp_Sim 2 (C) Terracota"],
                          Terracota_filtered["Temp_Sim 3 (C) Terracota"],
                          Terracota_filtered["Temp_Sim 4 (C) Terracota"]])

slope_terra, intercept_terra, r_value_terra, p_value_terra, std_err_terra = stats.linregress(x_terra, y_terra)
line_terra = slope_terra * x_terra + intercept_terra
ax_T_comp.plot(x_terra, line_terra, color="xkcd:tangerine", linestyle='-', alpha=0.8, linewidth=2, zorder=3)


ax_T_comp.set_xlabel('Temperatura experimental (C)')
ax_T_comp.set_ylabel('Temperatura simulada (C)')
ax_T_comp.legend(loc='best')
ax_T_comp.grid(True, alpha=0.7)

fig_T_comp.tight_layout()
fig_T_comp.show()
plt.savefig('fig_T_comp.pdf')


# Imprimir estadísticas de las regresiones lineales
print(f"Antracita - Total puntos: {len(x_ant)}")
print(f"Antracita: R² = {r_value_ant**2:.3f}, pendiente = {slope_ant:.3f}")

print(f"Green - Total puntos: {len(x_green)}")
print(f"Green: R² = {r_value_green**2:.3f}, pendiente = {slope_green:.3f}")

print(f"Terracota - Total puntos: {len(x_terra)}")
print(f"Terracota: R² = {r_value_terra**2:.3f}, pendiente = {slope_terra:.3f}")


mostrar_tiempo_total()

# TODO: las filas del delta T empiezan desde bastante pronto por la mañana, seguro que ya hay 400 W/m2?
# TODO: hay mucha diferencia (delta T grande) pronto por la mañana... ¿por qué? representar Delta T para ver esto
# TODO: Mirar como de desplazados entre sí están los valores obtenidos para cada tipo de célula (ver como el desplazamiento entre sí)
# TODO: Representar gráficamente todo (también el Delta_T, para ver cuanto es más diferente y cuando se parece más a lo largo de los meses y las horas)
# TODO: Mejorar presentación del output en la terminal
#### Una de las green da un NOCT mas bajo que las demás porque está mucho más ventilada??
# %%
