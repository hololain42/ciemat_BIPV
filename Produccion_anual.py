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
##################
### CONSTANTES ###
##################

# TONC promedio:
# Para la TONC de la Green, la medida de la célula 1 se desvía del resto al estar más ventilada, por lo que 
# la media será considerando solo las otras 3 células

TONC_antra_mean = (resultados_NOCT_Antracita[f'Celula_1']['NOCT_eff']
                 + resultados_NOCT_Antracita[f'Celula_2']['NOCT_eff']
                 + resultados_NOCT_Antracita[f'Celula_3']['NOCT_eff']
                 + resultados_NOCT_Antracita[f'Celula_4']['NOCT_eff'])/4

print(TONC_antra_mean)

TONC_green_mean = (resultados_NOCT_Green[f'Celula_2']['NOCT_eff']
                 + resultados_NOCT_Green[f'Celula_3']['NOCT_eff']
                 + resultados_NOCT_Green[f'Celula_4']['NOCT_eff'])/3

print(TONC_green_mean)

TONC_terra_mean = (resultados_NOCT_Terracota[f'Celula_1']['NOCT_eff']
                 + resultados_NOCT_Terracota[f'Celula_2']['NOCT_eff']
                 + resultados_NOCT_Terracota[f'Celula_3']['NOCT_eff']
                 + resultados_NOCT_Terracota[f'Celula_4']['NOCT_eff'])/4

print(TONC_terra_mean)

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

    TONC_mean = np.mean([resultados_NOCT[f'Celula_{i}']['NOCT_eff'] for i in range(inicio_rango, final_rango)])
    
    print(f"TONC {tipo_celula}: {TONC_mean}")

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
    # Nombre de la columna Delta_T (T_cell_exp_prom - T_cell_sim_NOCT_prom) de la célula
    columna_delta_temp_celula_mean = f"Delta_T_promedios (C) {tipo_celula}"

    df_calculos[columna_delta_temp_celula_mean] = df_calculos[columna_temp_sim_celula_con_NOCT_mean] - df_calculos[f'Temp (C) media {tipo_celula}']

    ### POTENCIA DC
    columna_potencia_sim_DC_celula = f"Potencia DC simulada (W) {tipo_celula}"

    df_calculos[columna_potencia_sim_DC_celula] = df_calculos[columna_potencia_exp_DC_celula] * (1 - gamma_pot * df_calculos[columna_delta_temp_celula_mean])

    potencia_DC_total = df_calculos[columna_potencia_sim_DC_celula].sum()

    return potencia_DC_total



### ANTRACITA ###
potencia_Antracita = calculo_potencia(Antracita_filtered, resultados_NOCT_Antracita, 1, 5, "Antracita",
                                      gamma_antra, columna_potencia_exp_DC_celula="Potencia entrada (W) Antracita")

### GREEN ###
potencia_Green     = calculo_potencia(Green_filtered, resultados_NOCT_Green, 2, 5, "Green",
                                      gamma_green, columna_potencia_exp_DC_celula="Potencia entrada (W) Green")

### TERRACOTA ###
potencia_Terracota = calculo_potencia(Terracota_filtered, resultados_NOCT_Terracota, 1, 5, "Terracota",
                                      gamma_terra, columna_potencia_exp_DC_celula="Potencia entrada (W) Terracota")

print(f"Potencia sim Antracita (W): {potencia_Antracita:.2f}")
print(f"Potencia exp Antracita (W): {Antracita_filtered["Potencia entrada (W) Antracita"].sum():.2f}")
print(f"Potencia sim Green (W): {potencia_Green:.2f}")
print(f"Potencia exp Green (W): {Green_filtered["Potencia entrada (W) Green"].sum():.2f}")
print(f"Potencia sim Terracota (W): {potencia_Terracota:.2f}")
print(f"Potencia exp Terracota (W): {Terracota_filtered["Potencia entrada (W) Terracota"].sum():.2f}")




mostrar_tiempo_total()

# %%