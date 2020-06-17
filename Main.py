import sqlite3
import time
from Sensores import sensor_temperatura
from Sensores import i2c
from sqlite3 import Error

tiempo = 20.0

def sql_connection():
    try:
        conn = sqlite3.connect('Sonda_P4.db')
        return conn
    except Error:
        print(Error)
        
def sql_table(conn):
    cur =conn.cursor()
    cur.execute("CREATE TABLE lecturas(N integer PRIMARY KEY AUTOINCREMENT, datatime integer, Tempertatura integer,pH integer,DO integer,CE integer,TDS integer, S integer, OPR integer)")
    conn.commit()

def sql_insert(conn,lecturas):
    cur=conn.cursor()
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
    #
   ## CEt=[1, 1, 1, 1, 1,1,1,1,1,1,1]
    CE= CEt[0:4]
    ##CE=1
    TDS= CEt[5]
    S= CEt[7:11]
    
    SEN= {"Temp":temp,"DO":DO,"OPR":OPR,"PH":PH, "CE":CE,"TDS": TDS, "S": S}
    print (SEN)
    lect=(temp,PH,DO,CE,TDS,S,OPR)
   ## print (temp)
   ## aux=(temp,temp,temp,temp,temp)
    ##print (reading_time)
    ##print ("CE: "+ str(CE[0:4]))
    ##print ("TDS: "+ str(CE[5]))
    ##print ("S: "+ str(CE[7:11]))



    ## Almacenamiento en BD

  ##  c.execute("INSERT INTO lecturas VALUES ( 1,datetime('now','localtime'), temp, PH, CE, TDS,S)")

#    c.execute('''INSERT INTO lecturasPy(datatime,Tempertatura,pH,CE,TDS,S) VALUES(datetime('now','localtime'),?,?,?,?,?)''', aux)
  #  conn.commit()
    sql_insert(conn,lect)
    print ("Carga Exitosa, timepo de espera: " + str(tiempo) +" [s]. ")
    time.sleep(tiempo)

