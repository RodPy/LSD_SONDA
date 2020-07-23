import sqlite3
import time
import mqttConf
from Sensores import sensor_temperatura
from Sensores import i2c
from sqlite3 import Error


#tiempo = 10.0

######################################################################################################################
########  Creacion de Tablas para Base de Datos
######################################################################################################################
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
        
        client.publish("sensores",
               json.dumps(
                   {
                       "pos": {"lat": 1, "lng": 1},
                       "temp": temp,
                       "ph": PH,
                       "do": DO,
                       "ce": CE,
                       "tds": TDS,
                       "s": S
                   }
               )
        )

        ## Almacenamiento en BD

       # sql_insert(conn,lect)
        print("Carga Exitosa, timepo de espera: " + str(tiempo) +" [s]. ")
        time.sleep(tiempo)
        n -=1

if __name__ == '__main__':
    muestreo():
muestreo(5,5)