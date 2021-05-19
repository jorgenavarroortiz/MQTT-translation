import argparse
import configparser
import os.path
import sys
import datetime
import json
from io import BytesIO
import paho.mqtt.client as mqtt
import base64
import time

##################################################
################ GLOBAL VARIABLES ################
##################################################

# Topic: application/1/device/+/rx
# Payload: {"applicationID":"1","applicationName":"wimunet-app","deviceName":"wimunet-pycom05-otaa","devEUI":"70b3d5499012e936","rxInfo":[{"gatewayID":"b827ebfffe09d416","uplinkID":"968c1add-0e4a-45cf-a855-02008833e741","name":"wimunet-gw01","time":"2021-05-19T19:08:26.434795Z","rssi":-63,"loRaSNR":7.8,"location":{"latitude":37.197,"longitude":-3.624,"altitude":659}}],"txInfo":{"frequency":868500000,"dr":5},"adr":false,"fCnt":0,"fPort":2,"data":"MC4wMCAyNS41OCA0Mi4zNCA5MzM5NS41MA=="}

##################################################
############### CONFIGURATION FILE ###############
##################################################

class serversConf:
  MQTTServer1     = '127.0.0.1'
  MQTTPort1       = '1883'
  MQTTUser1       = ''
  MQTTPassword1   = ''
  MQTTServer2     = '127.0.0.1'
  MQTTPort2       = '1883'
  MQTTUser2       = ''
  MQTTPassword2   = ''
  debug          = 1

serversConfigOptions = serversConf()

connectedToServer2 = False
client2 = None

def initConfig(filename):

  config = configparser.ConfigParser()
  config['SERVERS'] = {'MQTTServer1': '127.0.0.1',
                      'MQTTPort1': '1883',
                      'MQTTUser1': '',
                      'MQTTPassword1': '',
                      'MQTTServer2': '127.0.0.1',
                      'MQTTPort2': '1883',
                      'MQTTUser2': '',
                      'MQTTPassword2': '',
                      'debug': '1'}

  with open(filename, 'w') as configfile:
    config.write(configfile)


def parseConfig(filename):

  config = configparser.ConfigParser()
  config.read(filename)

  SERVERS = config['SERVERS']
  serversConfigOptions.MQTTServer1     = SERVERS['MQTTServer1']
  serversConfigOptions.MQTTPort1       = SERVERS['MQTTPort1']
  serversConfigOptions.MQTTUser1       = SERVERS['MQTTUser1']
  serversConfigOptions.MQTTPassword1   = SERVERS['MQTTPassword1']
  serversConfigOptions.MQTTServer2     = SERVERS['MQTTServer2']
  serversConfigOptions.MQTTPort2       = SERVERS['MQTTPort2']
  serversConfigOptions.MQTTUser2       = SERVERS['MQTTUser2']
  serversConfigOptions.MQTTPassword2   = SERVERS['MQTTPassword2']
  serversConfigOptions.debug           = SERVERS['debug']

  print ('[INFO] Read configuration options')


##################################################
###################### MQTT ######################
##################################################

# The callback for when the client receives a CONNACK response from the server.
def on_connect1(client, userdata, flags, rc):
  print("[INFO] Connected to MQTT server #1")

  # Subscribing in on_connect() means that if we lose the connection and reconnect then subscriptions will be renewed.
  # *** CHANGE THIS TOPIC AS REQUIRED ***
  client.subscribe("application/1/device/+/rx")

# The callback for when a PUBLISH message is received from the server.
def on_message1(client, userdata, msg):
#  print(msg.topic + " " + str(msg.payload))
  payload = msg.payload
  payload = payload.decode('utf-8')

  # Process the message received from server #1
  try:
    json_data = json.loads(payload)
#    print("json_data: " + str(json_data))
    data_b64 = json_data['data']
    base64_bytes = data_b64.encode('ascii')
    data_bytes = base64.b64decode(base64_bytes)
    data = data_bytes.decode('ascii')
    print('[MQTT] Message received from topic \"' + msg.topic + '\": ' + str(data))

    data_array = data.split()

    data1 = data_array[0] # Lux
    data2 = data_array[1] # Temperature
    data3 = data_array[2] # Humidity
    data4 = data_array[3] # Barometric pressure

    # Publishing to server #2
    if connectedToServer2:
        conversionTopic = "home/pysense/light"
        client2.publish(conversionTopic, data1)
        print('[MQTT] Message sent to topic \"' + conversionTopic + '\": ' + str(data1) )
        conversionTopic = "home/pysense/temperature"
        client2.publish(conversionTopic, data2)
        print('[MQTT] Message sent to topic \"' + conversionTopic + '\": ' + str(data2) )
        conversionTopic = "home/pysense/humidity"
        client2.publish(conversionTopic, data3)
        print('[MQTT] Message sent to topic \"' + conversionTopic + '\": ' + str(data3) )
        conversionTopic = "home/pysense/pressure"
        client2.publish(conversionTopic, data4)
        print('[MQTT] Message sent to topic \"' + conversionTopic + '\": ' + str(data4) )
  except Exception as e:
    print ("Error: " + str(e))

# The callback for when the client receives a CONNACK response from the server.
def on_connect2(client, userdata, flags, rc):
  global connectedToServer2, client2

  print("[INFO] Connected to MQTT server #2")
  connectedToServer2 = True
  client2 = client


##################################################
################## MAIN PROGRAM ##################
##################################################

def Start():

  ## Parsing parameters
  config = configparser.ConfigParser()
  parser = argparse.ArgumentParser()
  parser.add_argument('--config', dest='filename', default='config_gw.ini', help='configuration file')
  args = parser.parse_args()

  ## Reading (or creating) the configuration file
  configfilename = args.filename
  if os.path.exists(configfilename):
    print ('[INFO] ' + configfilename + ' file exists')
    parseConfig(configfilename)

  else:
    print ('[INFO] ' + configfilename + ' file does not exist, creating...')
    initConfig(configfilename)
    sys.exit()

  ## Connect to MQTT server #1
  mqttClient1 = mqtt.Client()
  mqttClient1.on_connect = on_connect1
  mqttClient1.on_message = on_message1
  mqttClient1.username_pw_set(username=serversConfigOptions.MQTTUser1 ,password=serversConfigOptions.MQTTPassword1)
  mqttServer1=serversConfigOptions.MQTTServer1
  mqttClient1.connect(mqttServer1, int(serversConfigOptions.MQTTPort1), 60)

  ## Connect to MQTT server #2
  mqttClient2 = mqtt.Client()
  mqttClient2.on_connect = on_connect2
  mqttClient2.username_pw_set(username=serversConfigOptions.MQTTUser2 ,password=serversConfigOptions.MQTTPassword2)
  mqttServer2=serversConfigOptions.MQTTServer2
  mqttClient2.connect(mqttServer2, int(serversConfigOptions.MQTTPort2), 60)

  ## Main loop
  # Blocking call that processes network traffic, dispatches callbacks and handles reconnecting.
  # Other loop*() functions are available that give a threaded interface and a manual interface.
#  mqttClient1.loop_forever()
  mqttClient1.loop_start()
  mqttClient2.loop_start()
  while True:
    time.sleep(1)

## Calling the Start function
Start()
