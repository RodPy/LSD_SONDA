import os
import threading
import paho.mqtt.client as mqtt     # Import the MQTT library
import time                         # The time library is useful for delays
import argparse
import json
import logging
import kk
from time import sleep

###################################################################
connected       =   False
Messagerecieved =   False
auxMuestra      =   False
_running        =   False
broker_address  =  "127.0.0.1"
port            =   1883
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
  
def muestreo (aux_lat,aux_lon,muestras,tiempo):
    print ("[lat long]" +str(aux_lat) + str(aux_lon))
    print ("HOLAAAA")
    auxMuestra=False
    for x in range(10):
        client.publish("sensores",str(x))
    client.publish("sonda/muestro/fin", True)
    
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
