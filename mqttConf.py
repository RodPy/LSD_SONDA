import paho.mqtt.client as mqtt # Import the MQTT library

import time # The time library is useful for delays

from  Main import *

# Our "on message" event

def on_message (client, userdata, msg):

    topic = str(message.topic)
    message = str(message.payload.decode("utf-8"))
    print(topic + message)
    
    if msg.topic == "sensor":
      message = json.loads(str(message.payload.decode("utf-8")))
      store = msg["position"]
      if msg ["muestrear"]:
        client.publish("Status/Sonda", { "muestreo": True})
        Main.muestreo(10,5)


 
def mqtt_thread(con_string, port, timeout):
    global client
    try:
        client = mqtt.Client("id_{}".format(database.drone_id))
        client.on_connect = on_connect
        client.subscribe("sensores")
        client.on_message = on_message
        # client.username_pw_set("", "")
        client.on_disconnect = on_disconnect
        client.connect(con_string, port, timeout)
        client.loop_forever()
    except ConnectionRefusedError as e:
        print("Could not connect to MQTT broker: ", e)
        logging.error(e)
        client = None

def on_message(_client, user_data, msg):
    msg_thread = threading.Thread(target=handle_mqtt_message, args=(_client, user_data, msg,))
    msg_thread.start()
    msg_thread.join()

client = mqtt.Client("Sonda_mqtt") # Create a MQTT client object

client.connect("192.168.20.20", 1883) # Connect to the MQTT broker

#ourClient.subscribe("sonda/raspberry") # Subscribe to the topic 

client.subscribe("sonda/raspberry/ph")
client.subscribe("sonda/raspberry/temp")
client.subscribe("sonda/raspberry/do")
client.subscribe("sonda/raspberry/opr")
client.subscribe("sonda/raspberry/ce")
client.subscribe("sonda/raspberry/tds")
client.subscribe("sonda/raspberry/s")
client.subscribe("sonda/raspverry/db")
client.on_message = messageFunction # Attach the messageFunction to subscription


client.loop_start() # Start the MQTT client

 

 

# Main program loop

#while(1):

  #  ourClient.publish("sonda/raspberry", "on") # Publish message to MQTT broker

  #  time.sleep(1) # Sleep for a second
  #  print("Listo")
