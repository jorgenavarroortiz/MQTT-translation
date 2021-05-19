import argparse
import configparser
import os.path
import sys
import datetime
import json
from io import BytesIO
import paho.mqtt.client as mqtt

##################################################
################ GLOBAL VARIABLES ################
##################################################


##################################################
############### CONFIGURATION FILE ###############
##################################################

class serverConf:
  MQTTServer     = '127.0.0.1'
  MQTTPort       = '1883'
  MQTTUser       = 'MyHomeJoMerMQTT'
  MQTTPassword   = 'EvaySara2513mq'
# If there is a '|' character is because there is a field within an array similar to {"field1":value1, "field2", "value2", ...}
# Typical of fields used in Tasmota for e.g. power:
# Topic: gBridge/u1/tele/sonoff-1487/SENSOR
# Payload: {"Time":"2020-06-07T11:25:33","ANALOG":{"Energy":54.647,"Power":474,"Voltage":230,"Current":2.060}}
# MQTTConversion = {'gBridge/u1/tele/sonoff-1487/SENSOR|Power', 'home/general/power'} 
  debug          = 1

serverConfigOptions = serverConf()


def initConfig(filename):

  config = configparser.ConfigParser()
  config['SERVER'] = {'MQTTServer': '127.0.0.1',
                      'MQTTPort': '1883',
                      'MQTTUser': 'MyHomeJoMerMQTT',
                      'MQTTPassword': 'EvaySara2513mq',
                      'debug': '1'}

  with open(filename, 'w') as configfile:
    config.write(configfile)


def parseConfig(filename):

  config = configparser.ConfigParser()
  config.read(filename)

  SERVER = config['SERVER']
  serverConfigOptions.MQTTServer     = SERVER['MQTTServer']
  serverConfigOptions.MQTTPort       = SERVER['MQTTPort']
  serverConfigOptions.MQTTUser       = SERVER['MQTTUser']
  serverConfigOptions.MQTTPassword   = SERVER['MQTTPassword']
  serverConfigOptions.debug          = SERVER['debug']

  print ('[INFO] Read configuration options')


##################################################
###################### MQTT ######################
##################################################

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
  print("[INFO] Connected to MQTT server")

  # Subscribing in on_connect() means that if we lose the connection and reconnect then subscriptions will be renewed.
  client.subscribe("gBridge/u1/tele/sonoff-1487/SENSOR")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
#  print(msg.topic + " " + str(msg.payload))
  payload = msg.payload
  payload = payload.decode('utf-8')

  # Process the message
  try:
    json_data = json.loads(payload)
    data1 = json_data['ANALOG']
    data2 = data1['Power']
    print('[MQTT] Message received from topic \"' + msg.topic + '\": ' + str(data2) )

    conversionTopic = "home/general/power"
    client.publish(conversionTopic, data2)
    print('[MQTT] Message sent to topic \"' + conversionTopic + '\": ' + str(data2) )
  except Exception as e:
    print ("Error: " + str(e))


##################################################
################## MAIN PROGRAM ##################
##################################################

def Start():

  ## Parsing parameters
  config = configparser.ConfigParser()
  parser = argparse.ArgumentParser()
  parser.add_argument('--config', dest='filename', default='config.ini', help='configuration file')
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

  ## Connect to MQTT server
  mqttClient = mqtt.Client()
  mqttClient.on_connect = on_connect
  mqttClient.on_message = on_message
  mqttClient.username_pw_set(username=serverConfigOptions.MQTTUser ,password=serverConfigOptions.MQTTPassword)
  mqttServer=serverConfigOptions.MQTTServer
  mqttClient.connect(mqttServer, int(serverConfigOptions.MQTTPort), 60)

  ## Main loop
  # Blocking call that processes network traffic, dispatches callbacks and handles reconnecting.
  # Other loop*() functions are available that give a threaded interface and a manual interface.
  mqttClient.loop_forever()


## Calling the Start function
Start()
