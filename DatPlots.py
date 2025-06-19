#%%

from Data import *
import threading

# Intervalo de tiempo para la gráfica (en horas)
TickInterval = 15
# Número de registros que vamos a representar en las gráficas
DataLength = 10000
# 10000 datos minutales se corresponde con aproximadamente 6.5 días

    ### DATETIME TO PLOT ###
    
# DataLoggerDataFrame["Date_local"] => 03/06/2025  7:01:13
# output de pd.to_datetime: 03-06-2025 07:01:13

Date = pd.to_datetime(DataLoggerDataFrame["Date_local"], dayfirst = True)


    ### REGISTRO PIRANÓMETRO ###

# Extraemos los datos de irradiancia del piranómetro y de las 3 células calibradas
IrradianciaPiranometro               = DataLoggerDataFrame["Canal 106-Canal_106_Gpyr_[W/m2] "].astype("float64")
IrradianciaCelulaCalibrada_Izquierda = DataLoggerDataFrame["Canal 306-Canal_306_G3_izda_[W/m2] "].astype("float64")
IrradianciaCelulaCalibrada_Arriba    = DataLoggerDataFrame["Canal 305-Canal_305_G2_arriba_[W/m2] "].astype("float64")
IrradianciaCelulaCalibrada_Abajo     = DataLoggerDataFrame["Canal 304-Canal_304_G1_abajo_[W/m2] "].astype("float64")

# Limpiamos datos negativos (los ponemos a 0, ya que la irradiancia nunca puede ser negativa)
# .loc permite establecer una condicion booleana (True/False para cada posición) y asignar un determinado valor en esa posición si la condición es True
IrradianciaPiranometro.loc[IrradianciaPiranometro < 0] = 0
IrradianciaCelulaCalibrada_Izquierda.loc[IrradianciaCelulaCalibrada_Izquierda < 0] = 0
IrradianciaCelulaCalibrada_Arriba.loc[IrradianciaCelulaCalibrada_Arriba < 0] = 0
IrradianciaCelulaCalibrada_Abajo.loc[IrradianciaCelulaCalibrada_Abajo < 0] = 0

# Extraemos los datos de temperatura ambiente y de temperatura de las células calibradas de arriba y abajo (no tenemos de la izquierda)
Temp_Ambiente               = DataLoggerDataFrame["Canal 105-Canal_105_Tambiente_[ºC] "].astype("float64")
Temp_CelulaCalibrada_Arriba = DataLoggerDataFrame["Canal 308-Canal_308_TG2_arriba_[ºC] "].astype("float64")
Temp_CelulaCalibrada_Abajo  = DataLoggerDataFrame["Canal 307-Canal_307_TG1_abajo_[ºC] "].astype("float64")


"""
Creamos el DataFrame de Irradiancia del piranómetro:
    pd.concat() combina dos series de pandas en un solo DataFrame:
        Date: Serie con las fechas
        IrradianciaPiranometro: Serie con los valores de irradiancia del piranómetro
        axis=1: Combinamos ambas series como columnas, una al lado de la otra
    Output: DataFrame con dos columnas:
        Una columna con las fechas (mantiene el nombre original "Date_local")
        Una columna con los valores de irradiancia
    .set_index("Date_local", inplace=True) convierte la columna "Date_local" en el índice del DataFrame:
        "Date_local" deja de ser una columna "normal" y pasa a ser el índice (etiqueta de las filas)
        inplace=True: Modifica el DataFrame original directamente, sin crear una copia

Resultado final: Un DataFrame indexado por fechas con una sola columna de datos de irradiancia
"""

DataFrame_Irradiancia = pd.concat([Date,IrradianciaPiranometro], axis=1)
DataFrame_Irradiancia.set_index("Date_local", inplace=True)

# Ploteamos la irradiancia del piranómetro
fig_Gpyr = plt.figure(figsize=(12, 8))
fig_Gpyr.canvas.manager.set_window_title('Irradiancia del piranómetro')

# Definimos objeto ax para distinguir entre figuras
ax_Gpyr = fig_Gpyr.add_subplot(111)
ax_Gpyr.set_title('Irradiancia del piranómetro', fontsize=12, fontweight='normal')

ax_Gpyr.plot(Date[:DataLength], IrradianciaPiranometro[:DataLength], linewidth=1.5, label= "Irradiancia del piranómetro ")

ax_Gpyr.set_xlabel('Fecha')
ax_Gpyr.set_ylabel('Irradiancia ($W/m^{2}$)')
ax_Gpyr.legend(loc='best')
ax_Gpyr.grid(True, alpha=0.7)

ax_Gpyr.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
ax_Gpyr.xaxis.set_major_locator(mdates.HourLocator(interval=TickInterval))
fig_Gpyr.autofmt_xdate() 

fig_Gpyr.tight_layout()
fig_Gpyr.show()


DataFrame_IrradianciaCelulaCalibrada_Arriba = pd.concat([Date,IrradianciaCelulaCalibrada_Arriba], axis=1)
DataFrame_IrradianciaCelulaCalibrada_Arriba.set_index("Date_local", inplace=True)

# Ploteamos la irradiancia de la célula calibrada de arriba
fig_G_arriba = plt.figure(figsize=(12, 8))
fig_G_arriba.canvas.manager.set_window_title('Irradiancia Célula Calibrada Arriba')

# Definimos objeto ax para distinguir entre figuras
ax_G_arriba = fig_G_arriba.add_subplot(111)
ax_G_arriba.set_title('Irradiancia de la célula calibrada de arriba', fontsize=12, fontweight='normal')

ax_G_arriba.plot(Date[:DataLength], IrradianciaCelulaCalibrada_Arriba[:DataLength], linewidth=1.5, label= "Irradiancia célula ")

ax_G_arriba.set_xlabel('Fecha')
ax_G_arriba.set_ylabel('Irradiancia ($W/m^{2}$)')
ax_G_arriba.legend(loc='best')
ax_G_arriba.grid(True, alpha=0.7)

ax_G_arriba.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
ax_G_arriba.xaxis.set_major_locator(mdates.HourLocator(interval=TickInterval))
fig_G_arriba.autofmt_xdate() 

fig_G_arriba.tight_layout()
fig_G_arriba.show()


DataFrame_Temp_Ambiente = pd.concat([Date,Temp_Ambiente], axis=1)
DataFrame_Temp_Ambiente.set_index("Date_local", inplace=True)

# Ploteamos la temperatura ambiente
fig_T_amb = plt.figure(figsize=(12, 8))
fig_T_amb.canvas.manager.set_window_title('Temperatura Ambiente')

# Definimos objeto ax para distinguir entre figuras
ax_T_amb = fig_T_amb.add_subplot(111)
ax_T_amb.set_title('Temperatura Ambiente', fontsize=12, fontweight='normal')

ax_T_amb.plot(Date[:DataLength], Temp_Ambiente[:DataLength], linewidth=1.5, label= "Temperatura ambiente ")

ax_T_amb.set_xlabel('Fecha')
ax_T_amb.set_ylabel('Temperatura ambiente (ºC)')
ax_T_amb.legend(loc='best')
ax_T_amb.grid(True, alpha=0.7)

ax_T_amb.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
ax_T_amb.xaxis.set_major_locator(mdates.HourLocator(interval=TickInterval))
fig_T_amb.autofmt_xdate() 

fig_T_amb.tight_layout()
fig_T_amb.show()


""" 
### HISTOGRAMA DE TEMPERATURA AMBIENTE (lo comentamos por el momento, no es necesario que salga siempre)

# Estadísticas básicas de la temperatura ambiente
print("Estadísticas de temperatura ambiente:")
col_T_amb = DataFrame_Temp_Ambiente.columns[0]
stats_T_amb = DataFrame_Temp_Ambiente.describe()
print(stats_T_amb)

# Plot del histograma de temperaturas
fig_hist_T_amb = plt.figure(figsize=(12, 4))
fig_hist_T_amb.canvas.manager.set_window_title('Histograma Temperatura Ambiente')

# Definimos objeto ax para distinguir entre figuras
ax_hist_T_amb = fig_hist_T_amb.add_subplot(111)
titulo_hist_T_amb = f'Histograma de Temperatura Ambiente ({DataFrame_Temp_Ambiente.index[0]} — {DataFrame_Temp_Ambiente.index[-1]})'
ax_hist_T_amb.set_title(titulo_hist_T_amb, fontsize=12, fontweight='normal')

ax_hist_T_amb.hist(DataFrame_Temp_Ambiente, bins=100, histtype='bar', alpha=0.9, color='tomato', edgecolor='black', label= "Temperatura ambiente ")

ax_hist_T_amb.set_xlim(-10, 40)

ax_hist_T_amb.set_xlabel('Temperatura ambiente (ºC)')
ax_hist_T_amb.set_ylabel('Número de medidas')
ax_hist_T_amb.legend(loc='best')
ax_hist_T_amb.grid(True, alpha=0.7)

str_estadisticas = '\n'.join((
    f'Media: {stats_T_amb.loc["mean", col_T_amb]:.2f} ºC',
    f'STD: {stats_T_amb.loc["std", col_T_amb]:.2f} ºC',
    f'Máx: {stats_T_amb.loc["max", col_T_amb]:.2f} ºC',
    f'Mín: {stats_T_amb.loc["min", col_T_amb]:.2f} ºC'
))

ax_hist_T_amb.text(0.05, 0.95, str_estadisticas, horizontalalignment='left',
    verticalalignment='top', transform=ax_hist_T_amb.transAxes, 
    bbox=dict(boxstyle='round', facecolor='whitesmoke', alpha=0.8))


fig_hist_T_amb.tight_layout()
fig_hist_T_amb.show()

"""


"""
    Definimos la función combine_series_list para arreglar cualquier fallo en los sensores de temperatura. 
    Por ejemplo, si falla el sensor de la célula 1, asumimos que la célula 2 tiene la misma temperatura y completamos el dato faltante 
    de la 1 con el dato medido de la 2.
        pandas.DataFrame.combine_first(series) es una función que modifica valores en caso necesario
            · Si 'result' tiene un valor, ese valor se mantiene
            · Si 'result' está vacío (NaN), toma el valor de 'series'
        De esta forma, combinamos las listas entre sí para que ninguna tenga un dato vacío

    Luego, rellenamos una lista con las columnas cuyo header contenga 'Tantra1':
        lt_temp = [col for col in DataLoggerDataFrame.columns if 'Tantra1' in col]
    
    Después vamos rellenando otra lista con los datos (importados como float64) y combinamos todas las listas en una sola, Temp_Antra_1, que
    incluya todas las listas redundantes (distintos sensores que midan la temperatura de la célula 1 de antracita). Hacemos esto así para que,
    si se decide incluir más sensores de temperatura, podamos combinar los sensores en una sola lista por si alguno falla.
        Temp_Antra_lt = []
        for i in lt_temp:
            Temp_Antra_lt.append(DataLoggerDataFrame[i].astype("float64"))
        Temp_Antra_1 = combine_series_list(Temp_Antra_lt)

"""

def combine_series_list(series_list):
    result = series_list[0] # Toma la primera serie como base
    
    for series in series_list[1:]: # Para cada serie restante
        result = result.combine_first(series) # Rellena huecos (si hay alguno) con los valores de las otras listas
    
    return result

    #################
    ### ANTRACITA ###
    #################

Vm_Antra_1 = DataLoggerDataFrame["Canal 113-Canal_113_Vm_antra1_[V] "].astype("float64")
Vm_Antra_2 = DataLoggerDataFrame["Canal 114-Canal_114_Vm_antra2_[V] "].astype("float64")
Vm_Antra_3 = DataLoggerDataFrame["Canal 115-Canal_115_Vm_antra3_[V] "].astype("float64")
Vm_Antra_4 = DataLoggerDataFrame["Canal 116-Canal_116_Vm_antra4_[V] "].astype("float64")

Im_Antra_1 = DataLoggerDataFrame["Canal 205-Canal_205_Im_antra1_[A] "].astype("float64")
Im_Antra_2 = DataLoggerDataFrame["Canal 206-Canal_206_Im_antra2_[A] "].astype("float64")
Im_Antra_3 = DataLoggerDataFrame["Canal 207-Canal_207_Im_antra3_[A] "].astype("float64")
Im_Antra_4 = DataLoggerDataFrame["Canal 208-Canal_208_Im_antra4_[A] "].astype("float64")

lt_temp = [col for col in DataLoggerDataFrame.columns if 'Tantra1' in col]
Temp_Antra_lt = []
for i in lt_temp:
    Temp_Antra_lt.append(DataLoggerDataFrame[i].astype("float64"))
Temp_Antra_1 = combine_series_list(Temp_Antra_lt)

lt_temp = [col for col in DataLoggerDataFrame.columns if 'Tantra2' in col]
Temp_Antra_lt = []
for i in lt_temp:
    Temp_Antra_lt.append(DataLoggerDataFrame[i].astype("float64"))
Temp_Antra_2 = combine_series_list(Temp_Antra_lt)

lt_temp = [col for col in DataLoggerDataFrame.columns if 'Tantra3' in col]
Temp_Antra_lt = []
for i in lt_temp:
    Temp_Antra_lt.append(DataLoggerDataFrame[i].astype("float64"))
Temp_Antra_3 = combine_series_list(Temp_Antra_lt)

lt_temp = [col for col in DataLoggerDataFrame.columns if 'Tantra4' in col]
Temp_Antra_lt = []
for i in lt_temp:
    Temp_Antra_lt.append(DataLoggerDataFrame[i].astype("float64"))
Temp_Antra_4 = combine_series_list(Temp_Antra_lt)

    #############
    ### GREEN ###
    #############

Vm_Green_1 = DataLoggerDataFrame["Canal 117-Canal_117_Vm_verde1_[V] "].astype("float64")
Vm_Green_2 = DataLoggerDataFrame["Canal 118-Canal_118_Vm_verde2_[V] "].astype("float64")
Vm_Green_3 = DataLoggerDataFrame["Canal 119-Canal_119_Vm_verde3_[V] "].astype("float64")
Vm_Green_4 = DataLoggerDataFrame["Canal 120-Canal_120_Vm_verde4_[V] "].astype("float64")

Im_Green_1 = DataLoggerDataFrame["Canal 209-Canal_209_Im_verde1_[A] "].astype("float64")
Im_Green_2 = DataLoggerDataFrame["Canal 210-Canal_210_Im_verde2_[A] "].astype("float64")
Im_Green_3 = DataLoggerDataFrame["Canal 211-Canal_211_Im_verde3_[A] "].astype("float64")
Im_Green_4 = DataLoggerDataFrame["Canal 212-Canal_212_Im_verde4_[A] "].astype("float64")

lt_temp = [col for col in DataLoggerDataFrame.columns if 'Tverde1' in col]
Temp_Green_lt = []
for i in lt_temp:
    Temp_Green_lt.append(DataLoggerDataFrame[i].astype("float64"))
Temp_Green_1 = combine_series_list(Temp_Green_lt)

lt_temp = [col for col in DataLoggerDataFrame.columns if 'Tverde2' in col]
Temp_Green_lt = []
for i in lt_temp:
    Temp_Green_lt.append(DataLoggerDataFrame[i].astype("float64"))
Temp_Green_2 = combine_series_list(Temp_Green_lt)

lt_temp = [col for col in DataLoggerDataFrame.columns if 'Tverde3' in col]
Temp_Green_lt = []
for i in lt_temp:
    Temp_Green_lt.append(DataLoggerDataFrame[i].astype("float64"))
Temp_Green_3 = combine_series_list(Temp_Green_lt)

lt_temp = [col for col in DataLoggerDataFrame.columns if 'Tverde4' in col]
Temp_Green_lt = []
for i in lt_temp:
    Temp_Green_lt.append(DataLoggerDataFrame[i].astype("float64"))
Temp_Green_4 = combine_series_list(Temp_Green_lt)

    #################
    ### TERRACOTA ###
    #################

Vm_Terra_1 = DataLoggerDataFrame["Canal 201-Canal_201_Vm_terra1_[V] "].astype("float64")
Vm_Terra_2 = DataLoggerDataFrame["Canal 202-Canal_202_Vm_terra2_[V] "].astype("float64")
Vm_Terra_3 = DataLoggerDataFrame["Canal 203-Canal_203_Vm_terra3_[V] "].astype("float64")
Vm_Terra_4 = DataLoggerDataFrame["Canal 204-Canal_204_Vm_terra4_[V] "].astype("float64")

Im_Terra_1 = DataLoggerDataFrame["Canal 213-Canal_213_Im_terra1_[A] "].astype("float64")
Im_Terra_2 = DataLoggerDataFrame["Canal 214-Canal_214_Im_terra2_[A] "].astype("float64")
Im_Terra_3 = DataLoggerDataFrame["Canal 215-Canal_215_Im_terra3_[A] "].astype("float64")
Im_Terra_4 = DataLoggerDataFrame["Canal 216-Canal_216_Im_terra4_[A] "].astype("float64")

lt_temp = [col for col in DataLoggerDataFrame.columns if 'Tterra1' in col]
Temp_Terracota_lt = []
for i in lt_temp:
    Temp_Terracota_lt.append(DataLoggerDataFrame[i].astype("float64"))
Temp_Terra_1 = combine_series_list(Temp_Terracota_lt)

lt_temp = [col for col in DataLoggerDataFrame.columns if 'Tterra2' in col]
Temp_Terracota_lt = []
for i in lt_temp:
    Temp_Terracota_lt.append(DataLoggerDataFrame[i].astype("float64"))
Temp_Terra_2 = combine_series_list(Temp_Terracota_lt)

lt_temp = [col for col in DataLoggerDataFrame.columns if 'Tterra3' in col]
Temp_Terracota_lt = []
for i in lt_temp:
    Temp_Terracota_lt.append(DataLoggerDataFrame[i].astype("float64"))
Temp_Terra_3 = combine_series_list(Temp_Terracota_lt)

lt_temp = [col for col in DataLoggerDataFrame.columns if 'Tterra4' in col]
Temp_Terracota_lt = []
for i in lt_temp:
    Temp_Terracota_lt.append(DataLoggerDataFrame[i].astype("float64"))
Temp_Terra_4 = combine_series_list(Temp_Terracota_lt)


##### PLOT AND REPRESENTATION SECTION #####

    #################
    ### Antracita ###
    #################

# Plots Voltaje
fig_V_antracita = plt.figure(figsize=(10, 6))
fig_V_antracita.canvas.manager.set_window_title('Voltaje células Antracita')

# Definimos objeto ax para distinguir entre figuras
ax_V_antracita = fig_V_antracita.add_subplot(111)
ax_V_antracita.set_title("Voltaje (V) individual para cada célula Antracita (Array en serie)", fontsize=12, fontweight='normal')

ax_V_antracita.plot(Date[:DataLength], Vm_Antra_1[:DataLength], linewidth=1.5, label= "Antra N°1")
ax_V_antracita.plot(Date[:DataLength], Vm_Antra_2[:DataLength], linewidth=1.5, label= "Antra N°2")
ax_V_antracita.plot(Date[:DataLength], Vm_Antra_3[:DataLength], linewidth=1.5, label= "Antra N°3")
ax_V_antracita.plot(Date[:DataLength], Vm_Antra_4[:DataLength], linewidth=1.5, label= "Antra N°4")

ax_V_antracita.set_xlabel('Fecha')
ax_V_antracita.set_ylabel('Voltaje Vm (V)')
ax_V_antracita.legend(loc='best')
ax_V_antracita.grid(True, alpha=0.7)

ax_V_antracita.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
ax_V_antracita.xaxis.set_major_locator(mdates.HourLocator(interval=TickInterval))
fig_V_antracita.autofmt_xdate() 

fig_V_antracita.tight_layout()
fig_V_antracita.show()


# Plots Corriente
fig_I_antracita = plt.figure(figsize=(10, 6))
fig_I_antracita.canvas.manager.set_window_title('Corriente células Antracita')

# Definimos objeto ax para distinguir entre figuras
ax_I_antracita = fig_I_antracita.add_subplot(111)
ax_I_antracita.set_title("Corriente (A) individual para cada célula Antracita (Array en serie)", fontsize=12, fontweight='normal')

ax_I_antracita.plot(Date[:DataLength], Im_Antra_1[:DataLength], linewidth=1.5, label= "Antra N°1")
ax_I_antracita.plot(Date[:DataLength], Im_Antra_2[:DataLength], linewidth=1.5, label= "Antra N°2")
ax_I_antracita.plot(Date[:DataLength], Im_Antra_3[:DataLength], linewidth=1.5, label= "Antra N°3")
ax_I_antracita.plot(Date[:DataLength], Im_Antra_4[:DataLength], linewidth=1.5, label= "Antra N°4")

ax_I_antracita.set_xlabel('Fecha')
ax_I_antracita.set_ylabel('Corriente Im (A)')
ax_I_antracita.legend(loc='best')
ax_I_antracita.grid(True, alpha=0.7)

ax_I_antracita.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
ax_I_antracita.xaxis.set_major_locator(mdates.HourLocator(interval=TickInterval))
fig_I_antracita.autofmt_xdate() 

fig_I_antracita.tight_layout()
fig_I_antracita.show()


# Plots Temperatura
fig_T_antracita = plt.figure(figsize=(10, 6))
fig_T_antracita.canvas.manager.set_window_title('Temperatura células Antracita')

# Definimos objeto ax para distinguir entre figuras
ax_T_antracita = fig_T_antracita.add_subplot(111)
ax_T_antracita.set_title("Temperatura (°C) individual para cada célula Antracita (Array en serie)", fontsize=12, fontweight='normal')

ax_T_antracita.plot(Date[:DataLength], Temp_Antra_1[:DataLength], linewidth=1.5, label= "Antra N°1")
ax_T_antracita.plot(Date[:DataLength], Temp_Antra_2[:DataLength], linewidth=1.5, label= "Antra N°2")
ax_T_antracita.plot(Date[:DataLength], Temp_Antra_3[:DataLength], linewidth=1.5, label= "Antra N°3")
ax_T_antracita.plot(Date[:DataLength], Temp_Antra_4[:DataLength], linewidth=1.5, label= "Antra N°4")

ax_T_antracita.set_xlabel('Fecha')
ax_T_antracita.set_ylabel('Temperatura (°C)')
ax_T_antracita.legend(loc='best')
ax_T_antracita.grid(True, alpha=0.7)

ax_T_antracita.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
ax_T_antracita.xaxis.set_major_locator(mdates.HourLocator(interval=TickInterval))
fig_T_antracita.autofmt_xdate() 

fig_T_antracita.tight_layout()
fig_T_antracita.show()

    #############
    ### GREEN ###
    #############

# Plots Voltaje
fig_V_green = plt.figure(figsize=(10, 6))
fig_V_green.canvas.manager.set_window_title('Voltaje células Green')

# Definimos objeto ax para distinguir entre figuras
ax_V_green = fig_V_green.add_subplot(111)
ax_V_green.set_title("Voltaje (V) individual para cada célula Green (Array en serie)", fontsize=12, fontweight='normal')

ax_V_green.plot(Date[:DataLength], Vm_Green_1[:DataLength], linewidth=1.5, label= "Green N°1")
ax_V_green.plot(Date[:DataLength], Vm_Green_2[:DataLength], linewidth=1.5, label= "Green N°2")
ax_V_green.plot(Date[:DataLength], Vm_Green_3[:DataLength], linewidth=1.5, label= "Green N°3")
ax_V_green.plot(Date[:DataLength], Vm_Green_4[:DataLength], linewidth=1.5, label= "Green N°4")

ax_V_green.set_xlabel('Fecha')
ax_V_green.set_ylabel('Voltaje Vm (V)')
ax_V_green.legend(loc='best')
ax_V_green.grid(True, alpha=0.7)

ax_V_green.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
ax_V_green.xaxis.set_major_locator(mdates.HourLocator(interval=TickInterval))
fig_V_green.autofmt_xdate() 

fig_V_green.tight_layout()
fig_V_green.show()


# Plots Corriente
fig_I_green = plt.figure(figsize=(10, 6))
fig_I_green.canvas.manager.set_window_title('Corriente células Green')

# Definimos objeto ax para distinguir entre figuras
ax_I_green = fig_I_green.add_subplot(111)
ax_I_green.set_title("Corriente (A) individual para cada célula Green (Array en serie)", fontsize=12, fontweight='normal')

ax_I_green.plot(Date[:DataLength], Im_Green_1[:DataLength], linewidth=1.5, label= "Green N°1")
ax_I_green.plot(Date[:DataLength], Im_Green_2[:DataLength], linewidth=1.5, label= "Green N°2")
ax_I_green.plot(Date[:DataLength], Im_Green_3[:DataLength], linewidth=1.5, label= "Green N°3")
ax_I_green.plot(Date[:DataLength], Im_Green_4[:DataLength], linewidth=1.5, label= "Green N°4")

ax_I_green.set_xlabel('Fecha')
ax_I_green.set_ylabel('Corriente Im (A)')
ax_I_green.legend(loc='best')
ax_I_green.grid(True, alpha=0.7)

ax_I_green.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
ax_I_green.xaxis.set_major_locator(mdates.HourLocator(interval=TickInterval))
fig_I_green.autofmt_xdate() 

fig_I_green.tight_layout()
fig_I_green.show()


# Plots Temperatura
fig_T_green = plt.figure(figsize=(10, 6))
fig_T_green.canvas.manager.set_window_title('Temperatura células Green')

# Definimos objeto ax para distinguir entre figuras
ax_T_green = fig_T_green.add_subplot(111)
ax_T_green.set_title("Temperatura (°C) individual para cada célula Green (Array en serie)", fontsize=12, fontweight='normal')

ax_T_green.plot(Date[:DataLength], Temp_Green_1[:DataLength], linewidth=1.5, label= "Green N°1")
ax_T_green.plot(Date[:DataLength], Temp_Green_2[:DataLength], linewidth=1.5, label= "Green N°2")
ax_T_green.plot(Date[:DataLength], Temp_Green_3[:DataLength], linewidth=1.5, label= "Green N°3")
ax_T_green.plot(Date[:DataLength], Temp_Green_4[:DataLength], linewidth=1.5, label= "Green N°4")

ax_T_green.set_xlabel('Fecha')
ax_T_green.set_ylabel('Temperatura (°C)')
ax_T_green.legend(loc='best')
ax_T_green.grid(True, alpha=0.7)

ax_T_green.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
ax_T_green.xaxis.set_major_locator(mdates.HourLocator(interval=TickInterval))
fig_T_green.autofmt_xdate() 

fig_T_green.tight_layout()
fig_T_green.show()

    #################
    ### TERRACOTA ###
    #################

# Plots Voltaje
fig_V_terra = plt.figure(figsize=(10, 6))
fig_V_terra.canvas.manager.set_window_title('Voltaje células Terracota')

# Definimos objeto ax para distinguir entre figuras
ax_V_terra = fig_V_terra.add_subplot(111)
ax_V_terra.set_title("Voltaje (V) individual para cada célula Terracota (Array en serie)", fontsize=12, fontweight='normal')

ax_V_terra.plot(Date[:DataLength], Vm_Terra_1[:DataLength], linewidth=1.5, label= "Terra N°1")
ax_V_terra.plot(Date[:DataLength], Vm_Terra_2[:DataLength], linewidth=1.5, label= "Terra N°2")
ax_V_terra.plot(Date[:DataLength], Vm_Terra_3[:DataLength], linewidth=1.5, label= "Terra N°3")
ax_V_terra.plot(Date[:DataLength], Vm_Terra_4[:DataLength], linewidth=1.5, label= "Terra N°4")

ax_V_terra.set_xlabel('Fecha')
ax_V_terra.set_ylabel('Voltaje Vm (V)')
ax_V_terra.legend(loc='best')
ax_V_terra.grid(True, alpha=0.7)

ax_V_terra.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
ax_V_terra.xaxis.set_major_locator(mdates.HourLocator(interval=TickInterval))
fig_V_terra.autofmt_xdate() 

fig_V_terra.tight_layout()
fig_V_terra.show()


# Plots Corriente
fig_I_terra = plt.figure(figsize=(10, 6))
fig_I_terra.canvas.manager.set_window_title('Corriente células Terracota')

# Definimos objeto ax para distinguir entre figuras
ax_I_terra = fig_I_terra.add_subplot(111)
ax_I_terra.set_title("Corriente (A) individual para cada célula Terracota (Array en serie)", fontsize=12, fontweight='normal')

ax_I_terra.plot(Date[:DataLength], Im_Terra_1[:DataLength], linewidth=1.5, label= "Terra N°1")
ax_I_terra.plot(Date[:DataLength], Im_Terra_2[:DataLength], linewidth=1.5, label= "Terra N°2")
ax_I_terra.plot(Date[:DataLength], Im_Terra_3[:DataLength], linewidth=1.5, label= "Terra N°3")
ax_I_terra.plot(Date[:DataLength], Im_Terra_4[:DataLength], linewidth=1.5, label= "Terra N°4")

ax_I_terra.set_xlabel('Fecha')
ax_I_terra.set_ylabel('Corriente Im (A)')
ax_I_terra.legend(loc='best')
ax_I_terra.grid(True, alpha=0.7)

ax_I_terra.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
ax_I_terra.xaxis.set_major_locator(mdates.HourLocator(interval=TickInterval))
fig_I_terra.autofmt_xdate() 

fig_I_terra.tight_layout()
fig_I_terra.show()


# Plots Temperatura
fig_T_terra = plt.figure(figsize=(10, 6))
fig_T_terra.canvas.manager.set_window_title('Temperatura células Terracota')

# Definimos objeto ax para distinguir entre figuras
ax_T_terra = fig_T_terra.add_subplot(111)
ax_T_terra.set_title("Temperatura (°C) individual para cada célula Terracota (Array en serie)", fontsize=12, fontweight='normal')

ax_T_terra.plot(Date[:DataLength], Temp_Terra_1[:DataLength], linewidth=1.5, label= "Terra N°1")
ax_T_terra.plot(Date[:DataLength], Temp_Terra_2[:DataLength], linewidth=1.5, label= "Terra N°2")
ax_T_terra.plot(Date[:DataLength], Temp_Terra_3[:DataLength], linewidth=1.5, label= "Terra N°3")
ax_T_terra.plot(Date[:DataLength], Temp_Terra_4[:DataLength], linewidth=1.5, label= "Terra N°4")

ax_T_terra.set_xlabel('Fecha')
ax_T_terra.set_ylabel('Temperatura (°C)')
ax_T_terra.legend(loc='best')
ax_T_terra.grid(True, alpha=0.7)

ax_T_terra.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
ax_T_terra.xaxis.set_major_locator(mdates.HourLocator(interval=TickInterval))
fig_T_terra.autofmt_xdate() 

fig_T_terra.tight_layout()
fig_T_terra.show()


#### INVERTER DATA ####

    ##################
    ### INPUT (DC) ###
    ##################

''' 
Los voltajes de entrada al inversor de GREEN y TERRACOTA han sido modificados al menos 
una vez, por lo que estamos utilizando ambos canales para acceder al REGISTRO COMPLETO.
El procedimiento es manual puesto que no se espera que los canales se mantengan en un 
futuro. Fuese lo contrario, puede modificarse manteniendo los canales intactos.
'''


### VOLTAJE ###
# Canal 403: Voltaje de las células Antracita a la entrada del inversor
#   - Suma de canales 401 y 402
#   - Canal 401: Suma de Vm_antra1 y Vm_antra2
#   - Canal 402: Suma de Vm_antra3 y Vm_antra4 
#   - Por tanto, el canal 403 es la suma de los voltajes de las 4 células individuales (array en serie)

V_input_Antra = DataLoggerDataFrame["Canal 403-Canal_403_Vinversor-antra_403_401+402 "].astype("float64")
V_input_Green = DataLoggerDataFrame["Canal 406-Canal_406_Vinversor-verde_406=404+405 "].astype("float64")
V_input_Terra = DataLoggerDataFrame["Canal 409-Canal_409_Vinversor-terra_409_407+408 "].astype("float64")


### CORRIENTE ###
# Canal 217: Corriente de las células Antracita a la entrada del inversor (array en serie)

I_input_Antra = DataLoggerDataFrame["Canal 217-Canal_217_Ientradainversor_antacita_[A] "].astype("float64")
I_input_Green = DataLoggerDataFrame["Canal 218-Canal_218_Ientradainversor_verde_[A] "].astype("float64")
I_input_Terra = DataLoggerDataFrame["Canal 219-Canal_219_Ientradainversor_terracota_[A] "].astype("float64")


### POTENCIA ###
# Hay un error en el nombre de los canales, PERO los valores de las celdas son correctos.
#   - El header de P_input_Antra debería ser 403*217 (Vm_antra*Im_antra), sin embargo es 403*218 (Vm_antra*Im_verde)
#   - Hemos comprobado que, pese al error en el header, los valores de las celdas se corresponden a multiplicar la columna 403 (Vm_antra) por la columna 217 (Im_antra)
#   - Por tanto, error en el header pero los valores de la potencia si se corresponden con los de la antracita.
#   - Esto también se aplica al 411 (células green). Está comprobado que pese al error en el header, los valores de las celdas se corresponden
#     a multiplicar la columna 406 (Vm_verde) por la columna 218 (Im_verde)

P_input_Antra = DataLoggerDataFrame["Canal 410-Canal_410_Pantra DC_410_403*218 "].astype("float64")
P_input_Green = DataLoggerDataFrame["Canal 411-Canal_411_Pverde DC_411_406*217 "].astype("float64")
P_input_Terra = DataLoggerDataFrame["Canal 412-Canal_412_Pterra DC_412_409*219 "].astype("float64")


# Plots voltaje
fig_V_microinversor = plt.figure(figsize=(10, 6))
fig_V_microinversor.canvas.manager.set_window_title('Voltaje DC entrada microinversores')

# Definimos objeto ax para distinguir entre figuras
ax_V_microinversor = fig_V_microinversor.add_subplot(111)
ax_V_microinversor.set_title("Voltaje (V) en DC de array de Antracita/Green/Terracota a la entrada del microinversor", fontsize=12, fontweight='normal')

ax_V_microinversor.plot(Date[:DataLength], V_input_Antra[:DataLength], linewidth=1.5, label= "Antracita")
ax_V_microinversor.plot(Date[:DataLength], V_input_Green[:DataLength], linewidth=1.5, label= "Green")
ax_V_microinversor.plot(Date[:DataLength], V_input_Terra[:DataLength], linewidth=1.5, label= "Terracota")

ax_V_microinversor.set_xlabel('Fecha')
ax_V_microinversor.set_ylabel('Voltaje (V)')
ax_V_microinversor.legend(loc='best')
ax_V_microinversor.grid(True, alpha=0.7)

ax_V_microinversor.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
ax_V_microinversor.xaxis.set_major_locator(mdates.HourLocator(interval=TickInterval))
fig_V_microinversor.autofmt_xdate() 

fig_V_microinversor.tight_layout()
fig_V_microinversor.show()


# Plots Corriente
fig_I_microinversor = plt.figure(figsize=(10, 6))
fig_I_microinversor.canvas.manager.set_window_title('Corriente DC entrada microinversores')

# Definimos objeto ax para distinguir entre figuras
ax_I_microinversor = fig_I_microinversor.add_subplot(111)
ax_I_microinversor.set_title("Corriente (A) en DC de array de Antracita/Green/Terracota a la entrada del microinversor", fontsize=12, fontweight='normal')

ax_I_microinversor.plot(Date[:DataLength], I_input_Antra[:DataLength], linewidth=1.5, label= "Antracita")
ax_I_microinversor.plot(Date[:DataLength], I_input_Green[:DataLength], linewidth=1.5, label= "Green")
ax_I_microinversor.plot(Date[:DataLength], I_input_Terra[:DataLength], linewidth=1.5, label= "Terracota")

ax_I_microinversor.set_xlabel('Fecha')
ax_I_microinversor.set_ylabel('Corriente (A)')
ax_I_microinversor.legend(loc='best')
ax_I_microinversor.grid(True, alpha=0.7)

ax_I_microinversor.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
ax_I_microinversor.xaxis.set_major_locator(mdates.HourLocator(interval=TickInterval))
fig_I_microinversor.autofmt_xdate() 

fig_I_microinversor.tight_layout()
fig_I_microinversor.show()


# Plots potencia
fig_P_microinversor = plt.figure(figsize=(10, 6))
fig_P_microinversor.canvas.manager.set_window_title('Potencia DC entrada microinversores')

# Definimos objeto ax para distinguir entre figuras
ax_P_microinversor = fig_P_microinversor.add_subplot(111)
ax_P_microinversor.set_title("Potencia (W) en DC de array de Antracita/Green/Terracota a la entrada del microinversor", fontsize=12, fontweight='normal')

ax_P_microinversor.plot(Date[:DataLength], P_input_Antra[:DataLength], linewidth=1.5, label= "Antracita")
ax_P_microinversor.plot(Date[:DataLength], P_input_Green[:DataLength], linewidth=1.5, label= "Green")
ax_P_microinversor.plot(Date[:DataLength], P_input_Terra[:DataLength], linewidth=1.5, label= "Terracota")

ax_P_microinversor.set_xlabel('Fecha')
ax_P_microinversor.set_ylabel('Potencia (W)')
ax_P_microinversor.legend(loc='best')
ax_P_microinversor.grid(True, alpha=0.7)

ax_P_microinversor.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
ax_P_microinversor.xaxis.set_major_locator(mdates.HourLocator(interval=TickInterval))
fig_P_microinversor.autofmt_xdate() 

fig_P_microinversor.tight_layout()
fig_P_microinversor.show()


    ###################
    ### OUTPUT (AC) ###
    ###################


P_output_Antra = DataLoggerDataFrame["Canal 301-Canal_301_PAC_inversor_antracita_[W] "].astype("float64")
P_output_Green = DataLoggerDataFrame["Canal 302-Canal_302_PAC_inversor_verde_[W] "].astype("float64")
P_output_Terra = DataLoggerDataFrame["Canal 303-Canal_303_PAC_inversor_terracota_[W] "].astype("float64")

# Plots potencia de salida del microinversor
fig_P_output_microinversor = plt.figure(figsize=(10, 6))
fig_P_output_microinversor.canvas.manager.set_window_title('Potencia AC salida microinversores')

# Definimos objeto ax para distinguir entre figuras
ax_P_output_microinversor = fig_P_output_microinversor.add_subplot(111)
ax_P_output_microinversor.set_title("Potencia (W) en AC a la salida del microinversor", fontsize=12, fontweight='normal')

ax_P_output_microinversor.plot(Date[:DataLength], P_output_Antra[:DataLength], linewidth=1.5, label= "Antracita")
ax_P_output_microinversor.plot(Date[:DataLength], P_output_Green[:DataLength], linewidth=1.5, label= "Green")
ax_P_output_microinversor.plot(Date[:DataLength], P_output_Terra[:DataLength], linewidth=1.5, label= "Terracota")

ax_P_output_microinversor.set_xlabel('Fecha')
ax_P_output_microinversor.set_ylabel('Potencia (W) - Salida de Microinversores en AC')
ax_P_output_microinversor.legend(loc='best')
ax_P_output_microinversor.grid(True, alpha=0.7)

ax_P_output_microinversor.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
ax_P_output_microinversor.xaxis.set_major_locator(mdates.HourLocator(interval=TickInterval))
fig_P_output_microinversor.autofmt_xdate() 

fig_P_output_microinversor.tight_layout()
fig_P_output_microinversor.show()


def input_with_timeout_threading(prompt, timeout=40):
    
    result = [None]
    
    def get_input():
        try:
            result[0] = input(prompt)
        except:
            pass
    
    thread = threading.Thread(target=get_input)
    thread.daemon = True
    thread.start()
    thread.join(timeout)
    
    if thread.is_alive():
        return None  # Timeout
    return result[0]


# Impedimos que las figuras se cierren automáticamente tras crearse
plt.show(block=False)

# Informamos de que el paso de las representaciones ha terminado
print("-" * 50)
print(f"[INFO] Todas las figuras representadas")
print("-" * 50)

# Pregunta si continuar con la ejecución del programa (no puede continuar si las figuras siguen abiertas)
# Damos 15 segundos para responder, si no continuamos con las 
respuesta = input_with_timeout_threading("¿Continuar con las figuras cerradas? (s/n) [40s]: ", 40)

if respuesta is None:
    plt.close('all')
    print(f"\n[INFO] Tiempo de respuesta agotado (40s). Cerramos figuras y continuamos automáticamente...")
    print("-" * 50)
elif respuesta.lower().strip() in ['s', 'si', 'sí', 'y', 'yes']:
    plt.close('all')
    print(f"[INFO] Figuras cerradas. Continuando con la ejecución del programa...")
    print("-" * 50)
else:
    print("[INFO] Mantenemos las figuras abiertas. Continuamos la ejecución del programa...")
    print("-" * 50)


"""
Hasta ahora se han importado datos que, en su pequeña minoría, han sido intercambiados
de canal (Caso de algunos voltajes de entrada, potencias de entrada al inversor), esto
si bien solo afecta a los registros tempranos cercanos al comienzo del monitoreo,
se puede asumir que los canales variarán a medida que se quiera monitorear aún más
magnitudes relevantes. 

Hasta entonces, el script implementado intentará solventar los dos cambios de canal
que se han registrado hasta entonces pero se propondrá una rutina mucho más robusta
para importar datos utilizando como referencia el nombre del canal al que hace 
referencia la serie.

"""


# Reorganizamos y estructuramos los datos por tipo de panel solar creando 3 DataFrames separados.
# Con .set_index('Datetime', inplace=True) usamos las fechas como índice, convirtiendo cada DataFrame en una serie temporal.
# Esto nos permite analizar de forma independiente cada panel solar sin necesidad de cruzar DataFrames.

Antracita = pd.DataFrame()
Green     = pd.DataFrame()
Terracota = pd.DataFrame()


Antracita["Datetime"] = Date
Antracita["Vm 1 (V) Antracita"] = Vm_Antra_1
Antracita["Vm 2 (V) Antracita"] = Vm_Antra_2
Antracita["Vm 3 (V) Antracita"] = Vm_Antra_3
Antracita["Vm 4 (V) Antracita"] = Vm_Antra_4
Antracita["Im 1 (A) Antracita"] = Im_Antra_1
Antracita["Im 2 (A) Antracita"] = Im_Antra_2
Antracita["Im 3 (A) Antracita"] = Im_Antra_3
Antracita["Im 4 (A) Antracita"] = Im_Antra_4
Antracita["Temp 1 (C) Antracita"] = Temp_Antra_1
Antracita["Temp 2 (C) Antracita"] = Temp_Antra_2
Antracita["Temp 3 (C) Antracita"] = Temp_Antra_3
Antracita["Temp 4 (C) Antracita"] = Temp_Antra_4
Antracita["Voltaje entrada (V) Antracita"]    = V_input_Antra
Antracita["Corriente entrada (A) Antracita"]  = I_input_Antra
Antracita["Potencia entrada (W) Antracita"]   = P_input_Antra
Antracita["Potencia AC salida (W) Antracita"] = P_output_Antra
Antracita["Piranometro Referencia"] = IrradianciaPiranometro
Antracita["Celula Calibrada Arriba"] = IrradianciaCelulaCalibrada_Arriba
Antracita["Celula Calibrada Abajo"] = IrradianciaCelulaCalibrada_Abajo
Antracita["Celula Calibrada Izquierda"] = IrradianciaCelulaCalibrada_Izquierda
Antracita["Temp (C) Celula Calibrada Arriba"] = Temp_CelulaCalibrada_Arriba
Antracita["Temp (C) Celula Calibrada Abajo"] = Temp_CelulaCalibrada_Abajo
Antracita["Temp (C) Ambiente"] = Temp_Ambiente
Antracita.set_index('Datetime', inplace=True)


Green["Datetime"] = Date
Green["Vm 1 (V) Green"] = Vm_Green_1
Green["Vm 2 (V) Green"] = Vm_Green_2
Green["Vm 3 (V) Green"] = Vm_Green_3
Green["Vm 4 (V) Green"] = Vm_Green_4
Green["Im 1 (A) Green"] = Im_Green_1
Green["Im 2 (A) Green"] = Im_Green_2
Green["Im 3 (A) Green"] = Im_Green_3
Green["Im 4 (A) Green"] = Im_Green_4
Green["Temp 1 (C) Green"] = Temp_Green_1
Green["Temp 2 (C) Green"] = Temp_Green_2
Green["Temp 3 (C) Green"] = Temp_Green_3
Green["Temp 4 (C) Green"] = Temp_Green_4
Green["Voltaje entrada (V) Green"]    = V_input_Green
Green["Corriente entrada (A) Green"]  = I_input_Green
Green["Potencia entrada (W) Green"]   = P_input_Green
Green["Potencia AC salida (W) Green"] = P_output_Green
Green["Piranometro Referencia"] = IrradianciaPiranometro
Green["Celula Calibrada Arriba"] = IrradianciaCelulaCalibrada_Arriba
Green["Celula Calibrada Abajo"] = IrradianciaCelulaCalibrada_Abajo
Green["Celula Calibrada Izquierda"] = IrradianciaCelulaCalibrada_Izquierda
Green["Temp (C) Celula Calibrada Arriba"] = Temp_CelulaCalibrada_Arriba
Green["Temp (C) Celula Calibrada Abajo"] = Temp_CelulaCalibrada_Abajo
Green["Temp (C) Ambiente"] = Temp_Ambiente
Green.set_index('Datetime', inplace=True)


Terracota["Datetime"] = Date
Terracota["Vm 1 (V) Terracota"] = Vm_Terra_1
Terracota["Vm 2 (V) Terracota"] = Vm_Terra_2
Terracota["Vm 3 (V) Terracota"] = Vm_Terra_3
Terracota["Vm 4 (V) Terracota"] = Vm_Terra_4
Terracota["Im 1 (A) Terracota"] = Im_Terra_1
Terracota["Im 2 (A) Terracota"] = Im_Terra_2
Terracota["Im 3 (A) Terracota"] = Im_Terra_3
Terracota["Im 4 (A) Terracota"] = Im_Terra_4
Terracota["Temp 1 (C) Terracota"] = Temp_Terra_1
Terracota["Temp 2 (C) Terracota"] = Temp_Terra_2
Terracota["Temp 3 (C) Terracota"] = Temp_Terra_3
Terracota["Temp 4 (C) Terracota"] = Temp_Terra_4
Terracota["Voltaje entrada (V) Terracota"]    = V_input_Terra
Terracota["Corriente entrada (A) Terracota"]  = I_input_Terra
Terracota["Potencia entrada (W) Terracota"]   = P_input_Terra
Terracota["Potencia AC salida (W) Terracota"] = P_output_Terra
Terracota["Piranometro Referencia"] = IrradianciaPiranometro
Terracota["Celula Calibrada Arriba"] = IrradianciaCelulaCalibrada_Arriba
Terracota["Celula Calibrada Abajo"] = IrradianciaCelulaCalibrada_Abajo
Terracota["Celula Calibrada Izquierda"] = IrradianciaCelulaCalibrada_Izquierda
Terracota["Temp (C) Celula Calibrada Arriba"] = Temp_CelulaCalibrada_Arriba
Terracota["Temp (C) Celula Calibrada Abajo"] = Temp_CelulaCalibrada_Abajo
Terracota["Temp (C) Ambiente"] = Temp_Ambiente
Terracota.set_index('Datetime', inplace=True)



# %%
