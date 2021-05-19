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
  MQTTUser       = 'MQTTUSER'
  MQTTPassword   = 'MQTTPASS'
  debug          = 1

serverConfigOptions = serverConf()


def initConfig(filename):

  config = configparser.ConfigParser()
  config['SERVER'] = {'MQTTServer': '127.0.0.1',
                      'MQTTPort': '1883',
                      'MQTTUser': 'MQTTUSER',
                      'MQTTPassword': 'MQTTPASS',
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
  client.subscribe("home/rtl_433/TFA-Pool/72/temperature_C")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
#  print(msg.topic + " " + str(msg.payload))
  payload = msg.payload
  payload = payload.decode('utf-8')

  # Process the message
  try:
    print('[MQTT] Message received from topic \"' + msg.topic + '\": ' + str(payload) )

    conversionTopic = "home/outside/temperature"
    client.publish(conversionTopic, payload)
    print('[MQTT] Message sent to topic \"' + conversionTopic + '\": ' + str(payload) )
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
