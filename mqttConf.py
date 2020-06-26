import paho.mqtt.client as mqtt # Import the MQTT library

import time # The time library is useful for delays

 

# Our "on message" event

def messageFunction (client, userdata, message):

    topic = str(message.topic)

    message = str(message.payload.decode("utf-8"))

    print(topic + message)

 

ourClient = mqtt.Client("Sonda_mqtt") # Create a MQTT client object

ourClient.connect("192.168.20.164", 1883) # Connect to the test MQTT broker

#ourClient.subscribe("sonda/raspberry") # Subscribe to the topic 

ourClient.subscribe("sonda/raspberry/ph")
ourClient.subscribe("sonda/raspberry/temp")
ourClient.subscribe("sonda/raspberry/do")
ourClient.subscribe("sonda/raspberry/opr")
ourClient.subscribe("sonda/raspberry/ce")
ourClient.subscribe("sonda/raspberry/tds")
ourClient.subscribe("sonda/raspberry/s")
ourClient.subscribe("sonda/raspverry/db")
ourClient.on_message = messageFunction # Attach the messageFunction to subscription


ourClient.loop_start() # Start the MQTT client

 

 

# Main program loop

#while(1):

  #  ourClient.publish("sonda/raspberry", "on") # Publish message to MQTT broker

  #  time.sleep(1) # Sleep for a second
  #  print("Listo")
