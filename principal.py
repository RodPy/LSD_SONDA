import os
import threading
import paho.mqtt.client as mqtt     # Import the MQTT library
import time                         # The time library is useful for delays
import argparse
import json
import logging

import time
from Sensores import sensor_temperatura
from Sensores import i2c
from sqlite3 import Error
from time import sleep

###################################################################
connected       =   False
Messagerecieved =   False
auxMuestra      =   False
_running        =   False
broker_address  =  "192.168.20.20"
port            =   1883
muestras    =   10
tiempo      =   2
###################################################################


def on_connect (_client, userdata,flags,rc ):
    global _running
    _running = True
    print("Conectado al Servidor: " + str(broker_address))
   
def handle_mqtt_message(_client, userdata, msg):
    global auxMuestra, aux_lon,aux_lat
    try:
        topic = str(msg.topic)
        msgg= str(msg.payload.decode("utf-8"))
        print ("Mensaje Recibido :")
        print (topic + " :  " + msgg)
        
        if "sonda/muestreo" in topic:
            
            if "inicio" in topic:
                data_received = json.loads(str(msg.payload).encode("utf-8"))
                client.publish("sonda/status",True)                         # enviar mensaje de confirmacion de orden                
                aux_lat=float(data_received["position"]["lat"]),
                aux_lon=float(data_received["position"]["lon"])
                     
                print("Position"+str(aux_lat) + str(aux_lon))
                      
                client.publish("sonda/batimetria",True)                     # solicitud de medida
                #client.publish("",)
                auxMuestra=True

            if "fin" in topic:
                
                print ("estoy muestrenado")


        if "sonda/batimetria/cm" in topic:
            profundidad= int(msgg)
            print("prof - aux" + str(profundidad) + str(auxMuestra))
            if auxMuestra:
                muestreo(aux_lat,aux_lon,muestras,tiempo)
                


    except KeyError as e:
        print("data not understood: ", e)


def on_disconnect(_client, _, rc=0):
    print("Disconnected result code " + str(rc))
    _client.loop_stop()

def on_message(_client, user_data, msg):
    msg_thread = threading.Thread(target=handle_mqtt_message, args=(_client, user_data, msg,))
    msg_thread.start()
  

######################################################################################################################
######## Lectura de Sensores
######################################################################################################################

def muestreo(aux_lat,aux_lon,muestras,tiempo):
    n=muestras
    
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
        
#         client.publish("sensores",
#                json.dumps(
#                    {
#                        "pos": {"lat": 1, "lng": 1},
#                        "temp": temp,
#                        "ph": PH,
#                        "do": DO,
#                        "ce": CE,
#                        "tds": TDS,
#                        "s": S
#                    }
#                )
#         )
        
        client.publish("sonda/raspberry/ph", PH)
        client.publish("sonda/raspberry/temp", temp)
        client.publish("sonda/raspberry/do", DO)
        client.publish("sonda/raspberry/opr", OPR)
        client.publish("sonda/raspberry/ce", CE)
        client.publish("sonda/raspberry/tds", TDS)
        client.publish("sonda/raspberry/s", S)
        ## Almacenamiento en BD

       # sql_insert(conn,lect)
        print("Carga Exitosa, timepo de espera: " + str(tiempo) +" [s]. ")
        time.sleep(tiempo)
        
        print ("[lat long]" + str(aux_lat) + str(aux_lon))
        print ("HOLAAAA")
        auxMuestra=False
        client.publish("sonda/muestro/fin", True)
        n -=1
        
        #client.publish("sonda/sensores",json.dumps({"pos": {"lat": 1, "lon": 1, "alt": 1},"temp": temp, "ph": PH,"do": DO,"opr": OPR,"ce": CE,"tds": TDS,"s": S}))
        client.publish("sonda/sensores",json.dumps({"lat": LAT,"lon": LON,"alt": ALT,"temp": temp,"ph": PH,"do": DO,"opr": OPR,"ce": CE,"tds": TDS, "s": S}))
    
try:
    client = mqtt.Client("SONDA_LSD")
    client.on_connect = on_connect
    client.on_message = on_message
        # client.username_pw_set("", "")
    client.on_disconnect = on_disconnect
        
    client.connect(broker_address, port=port)

    client.subscribe(topic='sonda/muestreo', qos =2)
    client.subscribe(topic='sonda/muestreo/inicio', qos =2)
    client.subscribe('sonda/status' , qos =2)
    client.subscribe("sonda/batimetria/cm",qos=2)
    client.loop_forever()

except ConnectionRefusedError as e:
    print("Could not connect to MQTT broker: ", e)
    logging.error(e)

while _running !=True:
    time.sleep(0.2)

while Messagerecieved!=True:
    time.sleep(0.2)
