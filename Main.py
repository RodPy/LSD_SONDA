import sqlite3
from sqlite3 import Error
import time
from mqttConf import *
from Sensores import sensor_temperatura
from Sensores import i2c
from sqlite3 import Error
import json

tiempo = 5.0
cont1=0
######################################################################################################################
########  Creacion de Tablas para Base de Datos
######################################################################################################################
def sql_connection():
    try:
        conn = sqlite3.connect('Sonda_off.db')  # Nombre de la Base de datos 
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
######## Validacion de Datos######## 

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
######## Lectura de Sensores
######################################################################################################################

while True:
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
    LAT=0
    LON=0
    ALT=0
    cont1 +=1
    ourClient.publish("sonda/sensores",json.dumps({"lat": int(float(LAT)),"lon": int(float(LON)),"alt": int(float(ALT)),"temp": int(temp),"ph": int(float(PH)),"do": int(float(DO)),"opr": int(float(OPR)),"ce": int(float(CE)),"tds": int(float(TDS)), "s": int(float(S)), "cont":cont1}))
    #client.publish("sonda/sensores",json.dumps({"lat": LAT,"lon": LON,"alt": ALT,"temp": temp,"ph":PH,"do": DO,"opr": OPR,"ce": CE,"tds":TDS, "s": S, "cont":cont1}))


        ## Almacenamiento en BD

    sql_insert(conn,lect)
    print("Carga Exitosa, timepo de espera: " + str(tiempo) +" [s]. "+ "Lectura Continua Nro: " str(cont1))
    time.sleep(tiempo)
     