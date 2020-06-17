import sqlite3
import time
import mqttConf
from Sensores import sensor_temperatura
from Sensores import i2c
from sqlite3 import Error


tiempo = 20.0

def sql_connection():
    try:
        conn = sqlite3.connect('Sonda_Test.db')  # Nombre de la Base de datos 
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
##sql_table(conn)


c = conn.cursor()
##Lectura de Sensores
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
    ourClient.publish("sonda/raspberry/ph", PH)
    ourClient.publish("sonda/raspberry/temp", temp)
    ourClient.publish("sonda/raspberry/do", DO)
    ourClient.publish("sonda/raspberry/opr", OPR)
    ourClient.publish("sonda/raspberry/ce", CE)
    ourClient.publish("sonda/raspberry/tds", TDS)
    ourClient.publish("sonda/raspberry/s", S)

    ## Almacenamiento en BD

   # sql_insert(conn,lect)
    print("Carga Exitosa, timepo de espera: " + str(tiempo) +" [s]. ")
    time.sleep(tiempo)

