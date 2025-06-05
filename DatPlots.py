#%%

from Data import *


TickInterval = 15
DataLength = 10000

    ### DATETIME TO PLOT ###
Date = pd.to_datetime(DataLoggerDataFrame["Date_local"], dayfirst = True)


    ### REGISTRO PIRANÓMETRO ###

IrradianciaPiranometro = DataLoggerDataFrame["Canal 106-Canal_106_Gpyr_[W/m2] "].astype("float64")
IrradianciaPiranometro_Izquierda = DataLoggerDataFrame["Canal 306-Canal_306_G3_izda_[W/m2] "].astype("float64")
IrradianciaPiranometro_Arriba    = DataLoggerDataFrame["Canal 305-Canal_305_G2_arriba_[W/m2] "].astype("float64")
IrradianciaPiranometro_Abajo   = DataLoggerDataFrame["Canal 304-Canal_304_G1_abajo_[W/m2] "].astype("float64")

IrradianciaPiranometro.loc[IrradianciaPiranometro < 0] = 0
IrradianciaPiranometro_Izquierda.loc[IrradianciaPiranometro < 0] = 0
IrradianciaPiranometro_Arriba.loc[IrradianciaPiranometro < 0] = 0
IrradianciaPiranometro_Abajo.loc[IrradianciaPiranometro < 0] = 0

DataFrame_Irradiancia = pd.concat([Date,IrradianciaPiranometro], axis=1)
DataFrame_Irradiancia.set_index("Date_local", inplace=True)

plt.figure(figsize=(10, 6))
plt.plot(Date[:DataLength], IrradianciaPiranometro[:DataLength], linewidth=1.5, label= "Irradiancia piranómetro ")
plt.grid()
plt.ylabel('Irradiancia ($W/m^{2}$)')
plt.xlabel('Fecha')
plt.legend()


plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=TickInterval))
plt.gcf().autofmt_xdate() 
plt.show()


def combine_series_list(series_list):
    result = series_list[0]
    
    for series in series_list[1:]:
        result = result.combine_first(series)
    
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

Temp_Antra_2 = DataLoggerDataFrame["Canal 310-Canal_310_Tantra2_[ºC] "].astype("float64")

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

plt.figure(figsize=(10, 6))
plt.plot(Date[:DataLength], Vm_Antra_1[:DataLength], linewidth=1.5, label= "Antra N°1")
plt.plot(Date[:DataLength], Vm_Antra_2[:DataLength], linewidth=1.5, label= "Antra N°2")
plt.plot(Date[:DataLength], Vm_Antra_3[:DataLength], linewidth=1.5, label= "Antra N°3")
plt.plot(Date[:DataLength], Vm_Antra_4[:DataLength], linewidth=1.5, label= "Antra N°4")
plt.grid()
plt.ylabel('Voltaje Vm (V)')
plt.xlabel('Fecha')
plt.legend()
plt.title("Voltaje (V) individual para cada célula Antracita (Array en serie)")


plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=TickInterval))
plt.gcf().autofmt_xdate() 
plt.show()



plt.figure(figsize=(10, 6))
plt.plot(Date[:DataLength], Im_Antra_1[:DataLength], linewidth=1.5, label= "Antra N°1")
plt.plot(Date[:DataLength], Im_Antra_2[:DataLength], linewidth=1.5, label= "Antra N°2")
plt.plot(Date[:DataLength], Im_Antra_3[:DataLength], linewidth=1.5, label= "Antra N°3")
plt.plot(Date[:DataLength], Im_Antra_4[:DataLength], linewidth=1.5, label= "Antra N°4")
plt.grid()
plt.ylabel('Corriente Im (A)')
plt.xlabel('Fecha')
plt.legend()
plt.title("Corriente (A) individual para cada célula Antracita (Array en serie)")


plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=TickInterval))
plt.gcf().autofmt_xdate()  
plt.show()




plt.figure(figsize=(10, 6))
plt.plot(Date[:DataLength], Temp_Antra_1[:DataLength], linewidth=1.5, label= "Antra N°1")
plt.plot(Date[:DataLength], Temp_Antra_2[:DataLength], linewidth=1.5, label= "Antra N°2")
plt.plot(Date[:DataLength], Temp_Antra_3[:DataLength], linewidth=1.5, label= "Antra N°3")
plt.plot(Date[:DataLength], Temp_Antra_4[:DataLength], linewidth=1.5, label= "Antra N°4")
plt.grid()
plt.ylabel('Temperatura (°C)')
plt.xlabel('Fecha')
plt.legend()
plt.title("Temperatura (°C) individual para cada célula Antracita (Array en serie)")


plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=TickInterval))
plt.gcf().autofmt_xdate()  
plt.show()


    #############
    ### GREEN ###
    #############


plt.figure(figsize=(10, 6))
plt.plot(Date[:DataLength], Vm_Green_1[:DataLength], linewidth=1.5, label= "Green N°1")
plt.plot(Date[:DataLength], Vm_Green_2[:DataLength], linewidth=1.5, label= "Green N°2")
plt.plot(Date[:DataLength], Vm_Green_3[:DataLength], linewidth=1.5, label= "Green N°3")
plt.plot(Date[:DataLength], Vm_Green_4[:DataLength], linewidth=1.5, label= "Green N°4")
plt.grid()
plt.ylabel('Voltaje Vm (V)')
plt.xlabel('Fecha')
plt.legend()
plt.title("Voltaje (V) individual para cada célula Green (Array en serie)")


plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=TickInterval))
plt.gcf().autofmt_xdate() 
plt.show()



plt.figure(figsize=(10, 6))
plt.plot(Date[:DataLength], Im_Green_1[:DataLength], linewidth=1.5, label= "Green N°1")
plt.plot(Date[:DataLength], Im_Green_2[:DataLength], linewidth=1.5, label= "Green N°2")
plt.plot(Date[:DataLength], Im_Green_3[:DataLength], linewidth=1.5, label= "Green N°3")
plt.plot(Date[:DataLength], Im_Green_4[:DataLength], linewidth=1.5, label= "Green N°4")
plt.grid()
plt.ylabel('Corriente Im (A)')
plt.xlabel('Fecha')
plt.legend()
plt.title("Corriente (A) individual para cada célula Green (Array en serie)")


plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=TickInterval))
plt.gcf().autofmt_xdate()  
plt.show()




plt.figure(figsize=(10, 6))
plt.plot(Date[:DataLength], Temp_Green_1[:DataLength], linewidth=1.5, label= "Green N°1")
plt.plot(Date[:DataLength], Temp_Green_2[:DataLength], linewidth=1.5, label= "Green N°2")
plt.plot(Date[:DataLength], Temp_Green_3[:DataLength], linewidth=1.5, label= "Green N°3")
plt.plot(Date[:DataLength], Temp_Green_4[:DataLength], linewidth=1.5, label= "Green N°4")
plt.grid()
plt.ylabel('Temperatura (°C)')
plt.xlabel('Fecha')
plt.legend()
plt.title("Temperatura (°C) individual para cada célula Green (Array en serie)")


plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=TickInterval))
plt.gcf().autofmt_xdate()  
plt.show()

    #################
    ### TERRACOTA ###
    #################

plt.figure(figsize=(10, 6))
plt.plot(Date[:DataLength], Vm_Terra_1[:DataLength], linewidth=1.5, label= "Terra N°1")
plt.plot(Date[:DataLength], Vm_Terra_2[:DataLength], linewidth=1.5, label= "Terra N°2")
plt.plot(Date[:DataLength], Vm_Terra_3[:DataLength], linewidth=1.5, label= "Terra N°3")
plt.plot(Date[:DataLength], Vm_Terra_4[:DataLength], linewidth=1.5, label= "Terra N°4")
plt.grid()
plt.ylabel('Voltaje Vm (V)')
plt.xlabel('Fecha')
plt.legend()
plt.title("Voltaje (V) individual para cada célula Terracota (Array en serie)")


plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=TickInterval))
plt.gcf().autofmt_xdate() 
plt.show()



plt.figure(figsize=(10, 6))
plt.plot(Date[:DataLength], Im_Terra_1[:DataLength], linewidth=1.5, label= "Terra N°1")
plt.plot(Date[:DataLength], Im_Terra_2[:DataLength], linewidth=1.5, label= "Terra N°2")
plt.plot(Date[:DataLength], Im_Terra_3[:DataLength], linewidth=1.5, label= "Terra N°3")
plt.plot(Date[:DataLength], Im_Terra_4[:DataLength], linewidth=1.5, label= "Terra N°4")
plt.grid()
plt.ylabel('Corriente Im (A)')
plt.xlabel('Fecha')
plt.legend()
plt.title("Corriente (A) individual para cada célula Terracota (Array en serie)")


plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=TickInterval))
plt.gcf().autofmt_xdate()  
plt.show()




plt.figure(figsize=(10, 6))
plt.plot(Date[:DataLength], Temp_Terra_1[:DataLength], linewidth=1.5, label= "Terra N°1")
plt.plot(Date[:DataLength], Temp_Terra_2[:DataLength], linewidth=1.5, label= "Terra N°2")
plt.plot(Date[:DataLength], Temp_Terra_3[:DataLength], linewidth=1.5, label= "Terra N°3")
plt.plot(Date[:DataLength], Temp_Terra_4[:DataLength], linewidth=1.5, label= "Terra N°4")
plt.grid()
plt.ylabel('Temperatura (°C)')
plt.xlabel('Fecha')
plt.legend()
plt.title("Temperatura (°C) individual para cada célula Terracota (Array en serie)")


plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=TickInterval))
plt.gcf().autofmt_xdate()  
plt.show()


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

#v1_input_Green = DataLoggerDataFrame["Canal 406-Canal_406_Vinversor-verde_406=404+405 "].astype("float64")
#v2_input_Green = DataLoggerDataFrame["Canal 407-Canal_406_Vinversor-verde_406=404+405 "].astype("float64")
#
#v1_input_Terra = DataLoggerDataFrame["Canal 409-Canal_409_Vinversor-terra_409_407+408 "].astype("float64")
#v2_input_Terra = DataLoggerDataFrame["Canal 410-Canal_409_Vinversor-terra_409_407+408 "].astype("float64")
#
#V_input_Antra = DataLoggerDataFrame["Canal 403-Canal_403_Vinversor-antra_403_401+402 "].astype("float64")
#V_input_Green = v2_input_Green.combine_first(v1_input_Green)
#V_input_Terra = v2_input_Terra.combine_first(v1_input_Terra)

V_input_Green = DataLoggerDataFrame["Canal 406-Canal_406_Vinversor-verde_406=404+405 "].astype("float64")
V_input_Terra = DataLoggerDataFrame["Canal 409-Canal_409_Vinversor-terra_409_407+408 "].astype("float64")
V_input_Antra = DataLoggerDataFrame["Canal 403-Canal_403_Vinversor-antra_403_401+402 "].astype("float64")


### CORRIENTE ###

I_input_Antra = DataLoggerDataFrame["Canal 217-Canal_217_Ientradainversor_antacita_[A] "].astype("float64")
I_input_Green = DataLoggerDataFrame["Canal 218-Canal_218_Ientradainversor_verde_[A] "].astype("float64")
I_input_Terra = DataLoggerDataFrame["Canal 219-Canal_219_Ientradainversor_terracota_[A] "].astype("float64")


### POTENCIA ###

P_input_Antra = DataLoggerDataFrame["Canal 410-Canal_410_Pantra DC_410_403*218 "].astype("float64")

P_input_Green = DataLoggerDataFrame["Canal 411-Canal_411_Pverde DC_411_406*217 "].astype("float64")

P_input_Terra = DataLoggerDataFrame["Canal 412-Canal_412_Pterra DC_412_409*219 "].astype("float64")


plt.figure(figsize=(10, 6))
plt.plot(Date[:DataLength], V_input_Antra[:DataLength], linewidth=1.5, label= "Antra N°1")
plt.plot(Date[:DataLength], V_input_Green[:DataLength], linewidth=1.5, label= "Green N°2")
plt.plot(Date[:DataLength], V_input_Terra[:DataLength], linewidth=1.5, label= "Terra N°3")

plt.grid()
plt.ylabel('Voltaje (V)')
plt.xlabel('Fecha')
plt.legend()
plt.title("Volataje (V) en DC de array de Antracita/Green/Terracota a la entrada del microinversor")


plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=TickInterval))
plt.gcf().autofmt_xdate()  
plt.show()



plt.figure(figsize=(10, 6))
plt.plot(Date[:DataLength], I_input_Antra[:DataLength], linewidth=1.5, label= "Antra N°1")
plt.plot(Date[:DataLength], I_input_Green[:DataLength], linewidth=1.5, label= "Green N°2")
plt.plot(Date[:DataLength], I_input_Terra[:DataLength], linewidth=1.5, label= "Terra N°3")
plt.grid()
plt.ylabel('Corriente (A)')
plt.xlabel('Fecha')
plt.legend()
plt.title("Corriente (A) en DC de array de Antracita/Green/Terracota a la entrada del microinversor")


plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=TickInterval))
plt.gcf().autofmt_xdate()  
plt.show()




plt.figure(figsize=(10, 6))
plt.plot(Date[:DataLength], P_input_Antra[:DataLength], linewidth=1.5, label= "Antra N°1")
plt.plot(Date[:DataLength], P_input_Green[:DataLength], linewidth=1.5, label= "Green N°2")
plt.plot(Date[:DataLength], P_input_Terra[:DataLength], linewidth=1.5, label= "Terra N°3")
plt.grid()
plt.ylabel('Potencia (W)')
plt.xlabel('Fecha')
plt.legend()
plt.title("Potencia (W) en DC de array de Antracita/Green/Terracota a la entrada del microinversor")


plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=TickInterval))
plt.gcf().autofmt_xdate()  
plt.show()


    ###################
    ### OUTPUT (AC) ###
    ###################


P_output_Antra = DataLoggerDataFrame["Canal 301-Canal_301_PAC_inversor_antracita_[W] "].astype("float64")
P_output_Green = DataLoggerDataFrame["Canal 302-Canal_302_PAC_inversor_verde_[W] "].astype("float64")
P_output_Terra = DataLoggerDataFrame["Canal 303-Canal_303_PAC_inversor_terracota_[W] "].astype("float64")



plt.figure(figsize=(10, 6))
plt.plot(Date[:DataLength], P_output_Antra[:DataLength], linewidth=1.5, label= "Antra N°1")
plt.plot(Date[:DataLength], P_output_Green[:DataLength], linewidth=1.5, label= "Green N°2")
plt.plot(Date[:DataLength], P_output_Terra[:DataLength], linewidth=1.5, label= "Terra N°3")
plt.grid()
plt.ylabel('Potencia (W) - Salida de Microinversores en AC')
plt.xlabel('Fecha')
plt.legend()
plt.title("Potencia (W) en AC a la salida del microinversor")


plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=TickInterval))
plt.gcf().autofmt_xdate()  
plt.show()



"""
Hasta ahora se han importado datos que, en su pequeña minoría, han sido intercambiado
de canal (Caso de algunos voltajes de entrada, potencias de entrada al inversor), esto
si bien solo afecta a los registros tempranos cercanos al comienzo del monitoreo,
se puede asumir que los canales variarán a medida que se quiera monitorear aún más
magnitudes relevantes. 

Hasta entonces, el script implementado intentará solventar los dos cambios de canal
que se han registrado hasta entonces pero se propondrá una rutina mucho más robusta
para importar datos utilizando como referencia el nombre del canal al que hace 
referencia la serie.

"""


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
Antracita["Piranometro Arriba"] = IrradianciaPiranometro_Arriba
Antracita["Piranometro Abajo"] = IrradianciaPiranometro_Abajo
Antracita["Piranometro Izquierda"] = IrradianciaPiranometro_Izquierda
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
Green["Piranometro Arriba"] = IrradianciaPiranometro_Arriba
Green["Piranometro Abajo"] = IrradianciaPiranometro_Abajo
Green["Piranometro Izquierda"] = IrradianciaPiranometro_Izquierda
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
Terracota["Piranometro Arriba"] = IrradianciaPiranometro_Arriba
Terracota["Piranometro Abajo"] = IrradianciaPiranometro_Abajo
Terracota["Piranometro Izquierda"] = IrradianciaPiranometro_Izquierda
Terracota.set_index('Datetime', inplace=True)



# %%
