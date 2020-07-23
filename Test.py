import sqlite3
import time
import mqttConf
from Sensores import sensor_temperatura
from Sensores import i2c
from sqlite3 import Error







######################################################################################################################
######## Lectura de Sensores
######################################################################################################################

def muestreo(n,tiempo):
    while n>1:
        temp=sensor_temperatura.read_temp()[0]
        print ("Midiendo Temperatura: ")
        print (temp)
        reading_time = time.ctime(time.time())
        print ("Midiendo OPR: ")
        OPR= i2c.leerSensores("R","OPR")
        print (OPR)
        print ("Midiendo DO: ")
        DO= i2c.leerSensores("R","DO")
        print (DO)
        print ("Midiendo PH: ")
        PH= i2c.leerSensores("R","PH")
        print (PH)
        print ("Midiendo CE: ")
        CEt= i2c.leerSensores("R","CE")
        print (CEt) 
        print ("DATOS RECOLECTADOS : ")

        ce= CEt.split(",")
        CE=ce[0]
        TDS= ce[1]
        S= ce[2]
        
        SEN= {"Temp":temp,"DO":DO,"OPR":OPR,"PH":PH, "CE":CE,"TDS": TDS, "S": S}
        print (SEN)
        lect=(temp,PH,DO,CE,TDS,S,OPR)
        mqttConf.ourClient.publish("sonda/raspberry/ph", PH)
        mqttConf.ourClient.publish("sonda/raspberry/temp", temp)
        mqttConf.ourClient.publish("sonda/raspberry/do", DO)
        mqttConf.ourClient.publish("sonda/raspberry/opr", OPR)
        mqttConf.ourClient.publish("sonda/raspberry/ce", CE)
        mqttConf.ourClient.publish("sonda/raspberry/tds", TDS)
        mqttConf.ourClient.publish("sonda/raspberry/s", S)

        ## Almacenamiento en BD

       # sql_insert(conn,lect)
        print("Carga Exitosa, timepo de espera: " + str(tiempo) +" [s]. ")
        time.sleep(tiempo)
        n -=1

if __name__ == '__main__':
    muestreo():
muestreo(5,5)