import argparse
import json
import logging
import os
import threading
from time import sleep

import paho.mqtt.client as mqtt
import serial

from drone_ypacarai import Drone

# APMrover2.exe -M rover -O -25.303707,-57.353354,100,0 --base-port 5860 --defaults default_params\rover.parm
# python cormoran_auto.py --drone tcp:127.0.0.1:5760,3,0,Ypacarai

parser = argparse.ArgumentParser(description='Cormoran Auto.')
parser.add_argument('--mqtt', dest='mqttarg', default="127.0.0.1,1883,60", help='127.0.0.1,1883,60')
parser.add_argument('--id', dest='idarg', default="-1", help='id overrides drone args')
parser.add_argument('--drone', dest='dronearg', default='tcp:127.0.0.1:5760,0,1,Ypacarai',
                    help='tcp:127.0.0.1:5760,3,0,Ypacarai')
parser.add_argument('--serial', dest='serialarg', default='COM13', help='COM13')

args = parser.parse_args()

mqtt_args = args.mqttarg.split(',')
for i in range(len(mqtt_args)):
    try:
        mqtt_args[i] = int(mqtt_args[i])
    except ValueError:
        pass
client = None

drone_args = args.dronearg.split(',')
for i in range(len(drone_args)):
    try:
        drone_args[i] = int(drone_args[i])
    except ValueError:
        pass

serial_args = args.serialarg

try:
    id_arg = int(args.idarg)
    if id_arg >= 0:
        drone_args = ['tcp:127.0.0.1:{}'.format(5760 + 10 * id_arg), id_arg, 1, 'Ypacarai']
except ValueError:
    pass
print(drone_args)
logging.basicConfig(filename='database_{}.log'.format(drone_args[1]), level=logging.INFO)


def publish_whenever_whatever(topic, message):
    client.publish(topic, message)
    logging.info("PUB:{}, {}".format(topic, message))


def on_connect(_client, _, __, rc):
    global _running
    _running = True
    print("Connected with result code " + str(rc))
    _client.subscribe("+/requests")
    # _client.subscribe("cooperation/requests")
    _client.subscribe("cooperation/id" + str(database.drone_id))

    str_con2 = str(database)
    _client.publish("drone", str_con2)
    logging.info("PUB: {}".format(str_con2))


def handle_mqtt_message(_client, _, msg):
    try:
        print(str(msg.payload, 'utf-8'))
        print(msg.topic)
        if "admin" in msg.topic:
            data_received = json.loads(str(msg.payload, 'utf-8'))
            logging.log(logging.INFO, "REC: {}".format(str(msg.payload, 'utf-8')))
            if "requests" in msg.topic:
                if data_received["req_type"] == "position":
                    database.set_obligatory_goal(data_received)

        elif "cooperation" in msg.topic:
            data_received = json.loads(str(msg.payload, 'utf-8'))
            logging.log(logging.INFO, "REC: {}".format(str(msg.payload, 'utf-8')))
            if "requests" in msg.topic:
                if data_received["req_type"] == "position":

                    if data_received["id"] != database.drone_id and data_received[
                        "radius"] >= database.get_distance_metres(
                        database.home_loc,
                        
                    ):
                        logging.log(logging.INFO, "REC:close neigh, answering {}".format(json.dumps(
                            {"id": database.drone_id,
                             "position": database.obtain_position("region")
                             }
                        )))
                        my_thread = threading.Thread(target=publish_whenever_whatever,
                                                     args=("cooperation/id" + str(data_received["id"]),
                                                           json.dumps(
                                                               {"id": database.drone_id,
                                                                "position": database.obtain_position("region")
                                                                }
                                                           )))
                        my_thread.start()

                else:
                    print("how could it be not position")
            else:
                print("okay what?")

    except KeyError as e:
        print("data not understood: ", e)


def on_message(_client, user_data, msg):
    msg_thread = threading.Thread(target=handle_mqtt_message, args=(_client, user_data, msg,))
    msg_thread.start()
    msg_thread.join()


def on_disconnect(_client, _, rc=0):
    print("Disconnected result code " + str(rc))
    _client.loop_stop()


def mqtt_thread(con_string, port, timeout):
    global client
    try:
        client = mqtt.Client("id_{}".format(database.drone_id))
        client.on_connect = on_connect
        client.on_message = on_message
        # client.username_pw_set("", "")
        client.on_disconnect = on_disconnect
        client.connect(con_string, port, timeout)
        client.loop_forever()
    except ConnectionRefusedError as e:
        print("Could not connect to MQTT broker: ", e)
        logging.error(e)
        client = None


if __name__ == "__main__":
    data = dict()
    data["temp"] = 1

    database = Drone(*drone_args)
    _running = False
    base_dir = os.path.dirname(os.path.abspath(__file__))

    _mqtt_thread = threading.Thread(target=mqtt_thread, args=(*mqtt_args,))
    _mqtt_thread.start()

    serial_procedure = 0  # 0 = Wait, 1 = send start, 2 = wait finish, 3 = finished
    _serial_thread = threading.Thread(target=serial_thread, args=(serial_args,))
    _serial_thread.start()
    str_con = ""
    try:
        database.connect_and_arm()

        str_con = str(database)
        logging.info("PUB: {}".format(str_con))
        client.publish("drone", str_con)
        while not database.vehicle.armed or not _running:
            pass
        while _running:
            if database.private_state == 5:
                break
            str_con = str(database)
            print(str_con)
            if isinstance(client, mqtt.Client):
                client.publish("drone", str_con)
            logging.info("PUB: {}".format(str_con))
            if database.public_state == 0:
                # database.public_state = 3
                client.publish("cooperation/requests",
                               json.dumps({
                                   "req_type": "position",
                                   "id": database.drone_id,
                                   "position": database.obtain_position("region")
                               }))
                database.public_state = 3

            if database.private_state == 1:
                if serial_procedure == 0:
                    print('drone sensing')
                    serial_procedure = 1  # 1 = send start
                    if not _serial_thread.is_alive():
                        print(database.formal_gps2pix(database.vehicle.location.global_relative_frame))
                        print("Serial is not available, stopping for 3 seconds")
                        threading.Timer(3, serial_workaround).start()
                elif serial_procedure == 2:
                    database.private_state = 2
            if database.private_state == 2:
                if serial_procedure == 3:
                    database.update_measures(data)
                    database.private_state = 3
                    serial_procedure = 0
                    sleep(0.1)

            database.update_measures(data)
            # print("Distance to destination: ", database.get_distance_metres(
            #    database.vehicle.location.global_relative_frame, database.local_goal))
            # print("Real angle from north  : ", database.vehicle.attitude.yaw*180/3.1415)
            sleep(1)
    
    except KeyboardInterrupt:
        print('lol')
    database.vehicle.disarm()
    database.vehicle.close()
    str_con = str(database)
    client.publish("drone", str_con)
    logging.info("PUB: {}".format(str_con))
    client.disconnect()
    _running = False
    database.generate_images('map/Ypacarai/ypacarai_final.yaml')
    database.save_parameters('map/Ypacarai/ypacarai_final.yaml')
    _mqtt_thread.join()
    _serial_thread.join()