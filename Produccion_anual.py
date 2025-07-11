#%%

from RossModel_fitting import *
import numpy as np
from datetime import time
import pvlib

#%%

"""
Para calcular la potencia y la energía generada por el sistema vamos a comparar la potencia obtenida experimentalmente con una
potencia simulada a partir de la experimental y teniendo en cuenta la TONC calculada en RossModel_fitting.py

Por simplicidad, vamos a considerar la media de la TONC de cada color y la temperatura experimental media de los módulos.

"""

# Informamos de que empiezan los cálculos de la potencia
print(f"[INFO] Comienza el cálculo de la potencia y la producción energética")
print("-" * 50)

##################
### CONSTANTES ###
##################

# Coeficientes de potencia [%/ºC]. Cogemos los medidos por ERTEX con los módulos.

gamma_antra = -0.32
gamma_green = -0.32
gamma_terra = -0.32


###########################
### CÁLCULO DE POTENCIA ###
###########################

def calculo_potencia(df, resultados_NOCT, inicio_rango, final_rango, tipo_celula, gamma_pot, columna_potencia_exp_DC_celula,
                     columna_temp_ambiente="Temp (C) Ambiente", columna_irradiancia="Celula Calibrada Arriba"
                     ):
    
    columnas_temp_celula = [f"Temp {i} (C) {tipo_celula}" for i in range(inicio_rango, final_rango)]

    # Creamos un DataFrame temporal eliminando datos con NaN si los hubiera
    df_calculos = df[columnas_temp_celula + [columna_temp_ambiente, columna_irradiancia, columna_potencia_exp_DC_celula]].dropna()

    # Hacemos el promedio de la temperatura experimental de los módulos (axis = 1 opera por filas)
    df_calculos[f'Temp (C) media {tipo_celula}'] = df_calculos[columnas_temp_celula].mean(axis=1)

    # TONC promedio:
    # Para la TONC de la Green, la medida de la célula 1 se desvía del resto al estar más ventilada, por lo que 
    # la media será considerando solo las otras 3 células
    TONC_mean = np.mean([resultados_NOCT[f'Celula_{i}']['NOCT_eff'] for i in range(inicio_rango, final_rango)])
    
    print(f"-TONC promedio de {tipo_celula}: {TONC_mean:.2f} (ºC)")

    # Nombre de la columna de la temperatura simulada con el NOCT PROMEDIO
    columna_temp_sim_celula_con_NOCT_mean = f"Temp_Sim_con_NOCT_promedio (C) {tipo_celula}"

    # Aplicamos la función para simular la temperatura de la célula con el NOCT obtenido
    # y guardamos el resultado en una columna específica
    df_calculos[columna_temp_sim_celula_con_NOCT_mean] = simular_temperatura_celula(
        df_calculos[columna_irradiancia],
        df_calculos[columna_temp_ambiente],
        TONC_mean
        )

    ### DELTA T
    # Nombre de la columna Delta_T (T_cell_sim_NOCT_prom - T_cell_exp_prom) de la célula
    columna_delta_temp_celula_mean = f"Delta_T_promedios (C) {tipo_celula}"

    df_calculos[columna_delta_temp_celula_mean] = df_calculos[columna_temp_sim_celula_con_NOCT_mean] - df_calculos[f'Temp (C) media {tipo_celula}']

    ### POTENCIA DC
    columna_potencia_sim_DC_celula = f"Potencia DC simulada (W) {tipo_celula}"

    df_calculos[columna_potencia_sim_DC_celula] = df_calculos[columna_potencia_exp_DC_celula] * (1 - abs(gamma_pot/100) * df_calculos[columna_delta_temp_celula_mean])

    return df_calculos


###################
### ESTADÍSTICA ###
###################

# Función para calcular el Mean Bias Error (MBE) entre los valores calculados de Potencia_cell y los medidos realmente
def mean_bias_error_prod(P_cell_sim, P_cell_real, normalized):
    '''
    Parámetros:
        P_cell_sim (numeric): Serie de pandas de los valores de potencia simulados con el NOCT promedio
        P_cell_real (numeric): Serie de pandas de las potencias medidas experimentalmente
        normalized (boolean): Parámetro para indicar si queremos realizar el cálculo del MBE o del nMBE

    Devuelve:
        mbe (float): mean bias error
    '''

    # Definido como "simulado - real" para que el signo sea coherente con el resto de la investigación
    diff = (P_cell_sim - P_cell_real)

    if normalized == False:
        # Devuelve el MBE como tal
        mbe = diff.mean()

    else:
        # Devuelve el normalized MBE, que es un porcentaje (%)
        m_prom = P_cell_real.mean()
        mbe = (1/m_prom)*(diff.sum()/(len(diff)-1))*100

    return mbe


# Función para calcular el Mean Absolute Error (MAE) entre los valores calculados de Potencia_cell y los medidos realmente
def mean_absolute_error_prod(P_cell_sim, P_cell_real):
    '''
    Parámetros:
        T_cell_sim (numeric): Serie de pandas de los valores de potencia simulados con el NOCT promedio
        T_cell_real (numeric): Serie de pandas de las potencias medidas experimentalmente

    Devuelve:
        mae (float): mean bias error
    '''

    # Valor absoluto de "simulado - real"
    diff = abs(P_cell_sim - P_cell_real)
    mae = diff.mean()

    return mae


# Función para calcular el Root Mean Square Error (RMSE) entre los valores calculados de Potencia_cell y los medidos realmente
def root_mean_square_error_prod(P_cell_sim, P_cell_real, normalized):
    '''
    Parámetros:
        T_cell_sim (numeric): Serie de pandas de los valores simulados con el NOCT calculado
        T_cell_real (numeric): Serie de pandas de las temperaturas medidas experimentalmente

    Devuelve:
        rmse (float): root mean square error
    '''

    # Raíz cuadrada del segundo momento de la muestra de las diferencias entre los valores previstos y los valores observados
    diff_cuad = (P_cell_sim - P_cell_real)**2

    if normalized == False:
        # Devuelve el RMSE como tal
        rmse = math.sqrt(diff_cuad.mean())

    else:
        # Devuelve el normalized RMSE, que es un porcentaje (%)
        m_prom = P_cell_real.mean()
        rmse = (1/m_prom)*math.sqrt(diff_cuad.sum()/(len(diff_cuad)-1))*100

    return rmse


def to_kWh(energia_Wmin):
    '''
    Convierte la energía (Potencia total * tiempo de submuestreo) de W*min a kWh

    Parámetros:
        energia_Wmin (float): Valor de la energía total (sumatorio de la columna Potencia*tiempo de submuestreo) en W*min

    Devuelve:
        energia_kWh (float): Valor de la energía kWh
    '''

    energia_kWh = energia_Wmin*(1/1000)*(1/60)

    return energia_kWh


### ANTRACITA ###
Antracita_df_potencia = calculo_potencia(Antracita_filtered_sync_Submuestreado, resultados_NOCT_Antracita, 1, 5, "Antracita",
                                         gamma_antra, columna_potencia_exp_DC_celula="Potencia entrada (W) Antracita")

### GREEN ###
Green_df_potencia     = calculo_potencia(Green_filtered_sync_Submuestreado, resultados_NOCT_Green, 2, 5, "Green",
                                         gamma_green, columna_potencia_exp_DC_celula="Potencia entrada (W) Green")

### TERRACOTA ###
Terracota_df_potencia = calculo_potencia(Terracota_filtered_sync_Submuestreado, resultados_NOCT_Terracota, 1, 5, "Terracota",
                                         gamma_terra, columna_potencia_exp_DC_celula="Potencia entrada (W) Terracota")



resultados_potencia_celulas = {}

# Crear un diccionario que mapee nombres de células a sus DataFrames
dataframes_celulas_potencia = {
    "Antracita": Antracita_df_potencia,
    "Green": Green_df_potencia,
    "Terracota": Terracota_df_potencia
}

for nombre, df_celula_potencia in dataframes_celulas_potencia.items():

    # Nombre de la columna de la potencia de la célula experimental
    columna_potencia_exp_DC_celula = f"Potencia entrada (W) {nombre}"

    # Nombre de la columna de la potencia de la célula simulada con el NOCT promedio
    columna_potencia_sim_DC_celula = f"Potencia DC simulada (W) {nombre}"
    
    # Nombre de la columna Delta_P (P_cell_real-P_cell_sim) de la célula
    delta_potencia_celula_col = f"Delta_P (W) {nombre}"

    # Creamos una columna específica para la diferencia entre potencia real y la simulada con el NOCT promedio
    # Definido como "simulado - real" para que el signo sea coherente con el resto de la investigación
    df_celula_potencia[delta_potencia_celula_col] = df_celula_potencia[columna_potencia_sim_DC_celula] - df_celula_potencia[columna_potencia_exp_DC_celula]

    # Potencia total (suma de todos los valores)
    potencia_DC_exp_total = df_celula_potencia[columna_potencia_exp_DC_celula].sum()
    potencia_DC_sim_total = df_celula_potencia[columna_potencia_sim_DC_celula].sum()

    diff_rel_potencia = (potencia_DC_sim_total-potencia_DC_exp_total)/abs(potencia_DC_exp_total)*100

    potencia_DC_exp_media = df_celula_potencia[columna_potencia_exp_DC_celula].mean()

    # Energía total (suma de los valores y multiplicada por el tiempo de submuestreo, pasada a kWh
    produccion_energetica_exp = to_kWh(potencia_DC_exp_total*tiempo_submuestreo)
    produccion_energetica_sim = to_kWh(potencia_DC_sim_total*tiempo_submuestreo)

    diff_rel_energia = (produccion_energetica_sim-produccion_energetica_exp)/abs(produccion_energetica_exp)*100

    resultados_potencia_celulas[f"{nombre}"] = {
        'P_exp': potencia_DC_exp_total,
        'P_sim': potencia_DC_sim_total,
        'diff_rel_Potencia': diff_rel_potencia,
        'mean_P_exp': potencia_DC_exp_media,
        'MBE': mean_bias_error_prod(df_celula_potencia[columna_potencia_sim_DC_celula], df_celula_potencia[columna_potencia_exp_DC_celula], normalized = False),
        'nMBE': mean_bias_error_prod(df_celula_potencia[columna_potencia_sim_DC_celula], df_celula_potencia[columna_potencia_exp_DC_celula], normalized = True),
        'MAE': mean_absolute_error_prod(df_celula_potencia[columna_potencia_sim_DC_celula], df_celula_potencia[columna_potencia_exp_DC_celula]),
        'RMSE': root_mean_square_error_prod(df_celula_potencia[columna_potencia_sim_DC_celula], df_celula_potencia[columna_potencia_exp_DC_celula], normalized=False),
        'nRMSE': root_mean_square_error_prod(df_celula_potencia[columna_potencia_sim_DC_celula], df_celula_potencia[columna_potencia_exp_DC_celula], normalized=True),
        'Prod_Energia_exp': produccion_energetica_exp,
        'Prod_Energia_sim': produccion_energetica_sim,
        'diff_rel_Energia': diff_rel_energia
    }


print("-" * 50)
print("RESULTADOS PRODUCCIÓN ANUAL")
for tipo_celula, resultado in resultados_potencia_celulas.items():

    print(f"- Células de {tipo_celula}:")
    print(f"  - POTENCIA:")
    print(f"    - Potencia experimental (W) = {resultado['P_exp']:.2f}")
    print(f"    - Potencia simulada (W) = {resultado['P_sim']:.2f}")
    print(f"    - Diferencia relativa Potencias = {resultado['diff_rel_Potencia']:.2f}%")
    print(f"    - Valor medio experimental (W) = {resultado['mean_P_exp']:.2f}")
    print(f"  - MÉTRICAS POTENCIA:")
    print(f"    - MBE (W) = {resultado['MBE']:.2f}")
    print(f"    - nMBE = {resultado['nMBE']:.2f}%")
    print(f"    - MAE (W) = {resultado['MAE']:.2f}")
    print(f"    - RMSE (W) = {resultado['RMSE']:.2f}")
    print(f"    - nRMSE = {resultado['nRMSE']:.2f}%")
    print(f"  - ENERGÍA:")
    print(f"    - Energía experimental (kWh) = {resultado['Prod_Energia_exp']:.2f}")
    print(f"    - Energía simulada (kWh) = {resultado['Prod_Energia_sim']:.2f}")
    print(f"    - Diferencia relativa Energía = {resultado['diff_rel_Energia']:.2f}%")


def construir_dataframe_resultados_produccion(resultados_potencia_celulas):

    colores = list(resultados_potencia_celulas.keys())

    # Filas de métricas por color
    fila_P_exp      = [round(resultados_potencia_celulas[color]['P_exp'], 2) for color in colores]
    fila_P_sim      = [round(resultados_potencia_celulas[color]['P_sim'], 2) for color in colores]
    fila_diff_P     = [round(resultados_potencia_celulas[color]['diff_rel_Potencia'], 2) for color in colores]
    fila_mean_P_exp = [round(resultados_potencia_celulas[color]['mean_P_exp'], 2) for color in colores]
    fila_MBE        = [round(resultados_potencia_celulas[color]['MBE'], 2) for color in colores]
    fila_nMBE       = [round(resultados_potencia_celulas[color]['nMBE'], 2) for color in colores]
    fila_MAE        = [round(resultados_potencia_celulas[color]['MAE'], 2) for color in colores]
    fila_RMSE       = [round(resultados_potencia_celulas[color]['RMSE'], 2) for color in colores]
    fila_nRMSE      = [round(resultados_potencia_celulas[color]['nRMSE'], 2) for color in colores]
    fila_Prod_E_exp = [round(resultados_potencia_celulas[color]['Prod_Energia_exp'], 2) for color in colores]
    fila_Prod_E_sim = [round(resultados_potencia_celulas[color]['Prod_Energia_sim'], 2) for color in colores]
    fila_diff_E     = [round(resultados_potencia_celulas[color]['diff_rel_Energia'], 2) for color in colores]

    df = pd.DataFrame(
        [
            fila_P_exp,
            fila_P_sim,
            fila_diff_P,
            fila_mean_P_exp,
            fila_MBE,
            fila_nMBE,
            fila_MAE,
            fila_RMSE,
            fila_nRMSE,
            fila_Prod_E_exp,
            fila_Prod_E_sim,
            fila_diff_E,
        ],
        index=[
            "Potencia exp. (W)",
            "Potencia sim. (W)",
            "Diff Rel. Potencia (%)",
            "Potencia media exp. (W)",
            "MBE (W)",
            "nMBE (%)",
            "MAE (W)",
            "RMSE (W)",
            "nRMSE (%)",
            "Producción E exp. (kWh)",
            "Producción E sim. (kWh)",
            "Diff Rel. Energía (%)"
        ],
        columns=colores
    )

    return df


# Construimos el DataFrame
df_resultados_produccion  = construir_dataframe_resultados_produccion(resultados_potencia_celulas)

# Nombre del archivo
nombre_archivo_produccion = f"Resultados_Produccion_Inic_{fecha_solsticio}_Fin_{fecha_ultimo_arch}_Submuestreo_{tiempo_submuestreo}_min.xlsx"

# Guardamos en Excel
with pd.ExcelWriter(nombre_archivo_produccion, engine='xlsxwriter') as writer:
    df_resultados_produccion.to_excel(writer, sheet_name='Resumen_Produccion', startrow=0)

print("-" * 50)
print(f"[INFO] Archivo Excel con los resultados de Producción Anual guardado como '{nombre_archivo_produccion}'.")

# Mover al directorio deseado
mover_archivo(nombre_archivo_produccion, "Excel Resultados/Produccion_anual")


# ======================================
# FIGURA INDIVIDUAL POTENCIA - ANTRACITA
# ======================================

# ANTRACITA - Regresión lineal
# Concatenar todos los datos de Antracita
x_ant_P = Antracita_df_potencia["Potencia entrada (W) Antracita"]
y_ant_P = Antracita_df_potencia["Potencia DC simulada (W) Antracita"]

# Calcular regresión
slope_ant_P, intercept_ant_P, r_value_ant_P, p_value_ant_P, std_err_ant_P = stats.linregress(x_ant_P, y_ant_P)
line_ant_P = slope_ant_P * x_ant_P + intercept_ant_P

fig_ant_P = plt.figure(figsize=(10, 6))
fig_ant_P.canvas.manager.set_window_title('Antracita - Potencia simulada vs real')
ax_ant_P = fig_ant_P.add_subplot(111)
ax_ant_P.set_title("Antracita - Potencia simulada vs experimental", fontsize=12, fontweight='normal')

# Plot datos
ax_ant_P.plot(Antracita_df_potencia["Potencia entrada (W) Antracita"], Antracita_df_potencia["Potencia DC simulada (W) Antracita"], linestyle="", marker= ".", label= "Antracita", color= "xkcd:charcoal grey")

# Regresión lineal
ax_ant_P.plot(x_ant_P, line_ant_P, color="xkcd:steel grey", linestyle='-', alpha=0.8, linewidth=2, zorder=3, 
           label=f'R²={r_value_ant_P**2:.3f}')

ax_ant_P.set_xlabel('Potencia experimental (W)')
ax_ant_P.set_ylabel('Potencia simulada (W)')
ax_ant_P.legend(loc='best')
ax_ant_P.grid(True, alpha=0.7)

fig_ant_P.tight_layout()
fig_ant_P.savefig('figuras/Produccion_anual/Pot_sim_VS_Pot_real_Antracita.pdf', bbox_inches='tight')
fig_ant_P.savefig('figuras/Produccion_anual/png/Pot_sim_VS_Pot_real_Antracita.png', bbox_inches='tight')
fig_ant_P.show()


# ==================================
# FIGURA INDIVIDUAL POTENCIA - GREEN
# ==================================

# GREEN - Regresión lineal
# Concatenar todos los datos de Green
x_green_P = Green_df_potencia["Potencia entrada (W) Green"]
y_green_P = Green_df_potencia["Potencia DC simulada (W) Green"]

# Calcular regresión
slope_green_P, intercept_green_P, r_value_green_P, p_value_green_P, std_err_green_P = stats.linregress(x_green_P, y_green_P)
line_green_P = slope_green_P * x_green_P + intercept_green_P

fig_green_P = plt.figure(figsize=(10, 6))
fig_green_P.canvas.manager.set_window_title('Green - Potencia simulada vs real')
ax_green_P = fig_green_P.add_subplot(111)
ax_green_P.set_title("Green - Potencia simulada vs experimental", fontsize=12, fontweight='normal')

# Plot datos
ax_green_P.plot(Green_df_potencia["Potencia entrada (W) Green"], Green_df_potencia["Potencia DC simulada (W) Green"], linestyle="", marker= ".", label= "Green", color= "xkcd:leaf green")

# Regresión lineal
ax_green_P.plot(x_green_P, line_green_P, color="xkcd:irish green", linestyle='-', alpha=0.8, linewidth=2, zorder=3, 
           label=f'R²={r_value_green_P**2:.3f}')

ax_green_P.set_xlabel('Potencia experimental (W)')
ax_green_P.set_ylabel('Potencia simulada (W)')
ax_green_P.legend(loc='best')
ax_green_P.grid(True, alpha=0.7)

fig_green_P.tight_layout()
fig_green_P.savefig('figuras/Produccion_anual/Pot_sim_VS_Pot_real_Green.pdf', bbox_inches='tight')
fig_green_P.savefig('figuras/Produccion_anual/png/Pot_sim_VS_Pot_real_Green.png', bbox_inches='tight')
fig_green_P.show()


# ======================================
# FIGURA INDIVIDUAL POTENCIA - TERRACOTA
# ======================================

# TERRACOTA - Regresión lineal
# Datos de Terracota
x_terra_P = Terracota_df_potencia["Potencia entrada (W) Terracota"]
y_terra_P = Terracota_df_potencia["Potencia DC simulada (W) Terracota"]

# Calcular regresión
slope_terra_P, intercept_terra_P, r_value_terra_P, p_value_terra_P, std_err_terra_P = stats.linregress(x_terra_P, y_terra_P)
line_terra_P = slope_terra_P * x_terra_P + intercept_terra_P

fig_terra_P = plt.figure(figsize=(10, 6))
fig_terra_P.canvas.manager.set_window_title('Terracota - Potencia simulada vs real')
ax_terra_P = fig_terra_P.add_subplot(111)
ax_terra_P.set_title("Terracota - Potencia simulada vs experimental", fontsize=12, fontweight='normal')

# Plot datos
ax_terra_P.plot(Terracota_df_potencia["Potencia entrada (W) Terracota"], Terracota_df_potencia["Potencia DC simulada (W) Terracota"], linestyle="", marker= ".", label= "Terracota", color= "xkcd:terracotta")

# Regresión lineal
ax_terra_P.plot(x_terra_P, line_terra_P, color="xkcd:tangerine", linestyle='-', alpha=0.8, linewidth=2, zorder=3, 
           label=f'R²={r_value_terra_P**2:.3f}')

ax_terra_P.set_xlabel('Potencia experimental (W)')
ax_terra_P.set_ylabel('Potencia simulada (W)')
ax_terra_P.legend(loc='best')
ax_terra_P.grid(True, alpha=0.7)

fig_terra_P.tight_layout()
fig_terra_P.savefig('figuras/Produccion_anual/Pot_sim_VS_Pot_real_Terracota.pdf', bbox_inches='tight')
fig_terra_P.savefig('figuras/Produccion_anual/png/Pot_sim_VS_Pot_real_Terracota.png', bbox_inches='tight')
fig_terra_P.show()


# Imprimir estadísticas de las regresiones lineales
print(f"Antracita Potencia - Total puntos: {len(x_ant_P)}")
print(f"Antracita: R² = {r_value_ant_P**2:.3f}, pendiente = {slope_ant_P:.3f}")

print(f"Green Potencia - Total puntos: {len(x_green_P)}")
print(f"Green: R² = {r_value_green_P**2:.3f}, pendiente = {slope_green_P:.3f}")

print(f"Terracota Potencia - Total puntos: {len(x_terra_P)}")
print(f"Terracota: R² = {r_value_terra_P**2:.3f}, pendiente = {slope_terra_P:.3f}")
print("-" * 50)


# ====================================
# HISTOGRAMA DE POTENCIAS EXP. vs SIM.
# ====================================

# Extraer datos para el histograma y convertir a kW
celulas = ['Antracita', 'Green', 'Terracota']
P_exp = [resultados_potencia_celulas[celula]['P_exp'] / 1000 for celula in celulas]  # Convertir a kW
P_sim = [resultados_potencia_celulas[celula]['P_sim'] / 1000 for celula in celulas]  # Convertir a kW

# Configuración del gráfico
x = np.arange(len(celulas) * 2)  # Posiciones en el eje X (doble para cada par)
width = 0.35  # Ancho de las barras

# Crear la figura y el eje
fig_hist_P = plt.figure(figsize=(10, 6))
fig_hist_P.canvas.manager.set_window_title('Histograma de potencias según colores')
ax_hist_P = fig_hist_P.add_subplot(111)
ax_hist_P.set_title('Comparación de Potencia Experimental vs Simulada por colores', fontsize=12, fontweight='normal')

# Colores para cada célula (tonos diferentes)
colores_exp = ['xkcd:charcoal grey', 'xkcd:irish green', 'xkcd:terracotta']  
colores_sim = ['xkcd:steel grey', 'xkcd:leaf green', 'xkcd:tangerine']  

# Crear las barras con posiciones agrupadas por pares
# Crear listas con todos los valores intercalados
all_values = []
all_colors = []
all_labels = []

for i, celula in enumerate(celulas):
    all_values.extend([P_exp[i], P_sim[i]])
    all_colors.extend([colores_exp[i], colores_sim[i]])
    all_labels.extend([f'{celula} exp.', f'{celula} sim.'])

# Posiciones para las barras - agrupadas por pares
positions = []
for i in range(len(celulas)):
    positions.extend([i * 3, i * 3 + 0.8])  # Pares pegados con separación entre grupos

# Crear las barras
bars_hist_P = ax_hist_P.bar(positions, all_values, width=0.7, color=all_colors, alpha=0.8)

# Personalizar el gráfico
ax_hist_P.set_xlabel('Color', fontsize=12)
ax_hist_P.set_ylabel('Potencia (kW)', fontsize=12)
ax_hist_P.set_xticks(positions)
ax_hist_P.set_xticklabels(all_labels, rotation=45, ha='right')

# Fijar ylim para que quepa el texto encima de las barras
max_value = max(all_values)
ax_hist_P.set_ylim(0, max_value * 1.15)  # 15% más alto que el valor máximo

# Añadir valores encima de las barras
for bar in bars_hist_P:
    height = bar.get_height()
    ax_hist_P.text(bar.get_x() + bar.get_width()/2., height + max_value * 0.01,
            f'{height:.1f}', ha='center', va='bottom', fontsize=9)

# Ajustar el layout para evitar que se corten las etiquetas
fig_hist_P.tight_layout()
fig_hist_P.savefig('figuras/Produccion_anual/Hist_Pot_sim_VS_Pot_real.pdf', bbox_inches='tight')
fig_hist_P.savefig('figuras/Produccion_anual/png/Hist_Pot_sim_VS_Pot_real.png', bbox_inches='tight')
# Mostrar el gráfico
fig_hist_P.show()

mostrar_tiempo_total()

# %%