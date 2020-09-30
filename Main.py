import os
import sqlite3
from sqlite3 import Error
import time
from mqttConf import *
from Sensores import sensor_temperatura
from Sensores import i2c
from sqlite3 import Error
#from Base_Datos import Ftp
import json

tiempo = 5.0
cont1=0
#sensor = i2c.AtlasI2C()
dir= {97:"DO",98:"OPR",99:"PH",100:"CE"}



######################################################################################################################
################################  Creacion de Tablas para Base de Datos
######################################################################################################################
def sql_connection():
    try:
        conn = sqlite3.connect('Base_Datos/Sonda_30Setiembre.db')  # Nombre de la Base de datos 
        return conn
    except Error:
        print(Error)
        
def sql_table(conn):
    cur =conn.cursor()
    cur.execute("CREATE TABLE lecturas(N integer PRIMARY KEY AUTOINCREMENT, datatime integer, Tempertatura integer,pH integer,DO integer,CE integer,TDS integer, S integer, OPR integer)")
    conn.commit()

def sql_insert(conn,lecturas):
    cur=conn.cursor()
    #Se crea la table lecturas
    cur.execute("INSERT INTO lecturas(datatime,Tempertatura,pH,DO,CE,TDS,S,OPR) VALUES(datetime('now','localtime'),?,?,?,?,?,?,?)",lecturas)
    conn.commit()
    

conn= sql_connection() 


try:
    sql_table(conn)
except Error:
    pass 

    
c = conn.cursor()

######################################################################################################################
################################ Validacion de Datos######## 

def valDate(dateAct,dateAnt,tol):
    global aux
    aux= False
    if (dateAct< (dateAnt + tol) and dateAct> (dateAnt - tol)):
        aux=False
        return dateAct
    else:
        aux=True 
        return dateAnt

######################################################################################################################


######################################################################################################################
################################ Lectura de Sensores
######################################################################################################################
def sensorsRead():
    temp=0.0
    PH=0.0
    DO=0.0
    CE=0.0
    TDS=0.0
    S=0.0
    OPR=0.0
    sensor = i2c.AtlasI2C()
    ##Lectura de Sensores i2c
    i2cAdd=sensor.list_i2c_devices()
    print(i2cAdd)
    temp=sensor_temperatura.read_temp()[0]
    print ("Temperatura Medido Correctamente: " + str(temp))

    for x in  range(0,len(i2cAdd)):
        mesure=sensor.leerSensores("R",dir.get(i2cAdd[x]))
        print (dir.get(i2cAdd[x])+ " Medido Correctamente: " + mesure)
        if (dir.get(i2cAdd[x])== "PH"):
            PH=mesure
        elif(dir.get(i2cAdd[x])== "DO"):
            DO=mesure
        elif(dir.get(i2cAdd[x])== "CE"):
            CET=mesure
            ce = CET.split(",")
            CE = ce[0]
            TDS= ce[1]
            S  = ce[2]
        elif(dir.get(i2cAdd[x])== "OPR"):
            OPR=mesure
        else:
            pass
            
        sensor.apagarSensor(dir.get(i2cAdd[x]))
        
    lect=(temp,PH,DO,CE,TDS,S,OPR)
    SEN= {"Temp":temp,"DO":DO,"OPR":OPR,"PH":PH, "CE":CE,"TDS": TDS, "S": S}
    print ("Lectura Corecta de "+ str(len(i2cAdd)) + " Sensores " )
    print (SEN)
    return lect
    
while True:
    
    LAT=0
    LON=0
    ALT=0
    cont1 +=1
    
    #sensorsRead()
    mqttConf.ourClient.publish("sonda/sensores",json.dumps({"lat": int(float(LAT)),"lon": int(float(LON)),"alt": int(float(ALT)),"temp": int(temp),"ph": int(float(PH)),"do": int(float(DO)),"opr": int(float(OPR)),"ce": int(float(CE)),"tds": int(float(TDS)), "s": int(float(S)), "cont":cont1}))
#     ourClient.publish("sonda/sensores",json.dumps({"lat": LAT,"lon": LON,"alt": ALT,"temp": temp,"ph":PH,"do": DO,"opr": OPR,"ce": CE,"tds":TDS, "s": S, "cont":cont1}))


        ## Almacenamiento en BD

    sql_insert(conn,sensorsRead())
#    os.system("Base_Datos/Ftp.py"1)
    print("Carga Exitosa, timepo de espera: " + str(tiempo) +" [s]. "+ "Lectura Continua Nro: " + str(cont1))
#     try:
#         Ftp.ftpSend()
#     
#     except:
#         print("No se pudo mandar Base de datos")
#         pass
    time.sleep(tiempo)
     
