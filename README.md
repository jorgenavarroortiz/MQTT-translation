# MQTT-translation

© Jorge Navarro-Ortiz (jorgenavarro@ugr.es), University of Granada

Python scripts that subscribe to specific MQTT topics, modify the content of the messages (e.g. format change) and publish the messages to different topics. Python3 is required.

This may be useful to adapt to some platforms/programs, such as e.g. https://github.com/Nilhcem/home-monitoring-grafana which utilizes a specific MQTT topic format (``home/{peripheralName}/{temperature|humidity|battery|status}``) for the bridge between MQTT and InfluxDB. Similarly, it may be useful to process the content of the message, e.g. get several measurement values sent in the same topic and publish them to separate topics (e.g. one topic for temperature, another for humidity, ...).

## Same broker to subscribe and publish messages

The ``config_1broker.ini`` file contains the credentials for the MQTT broker. By default, the scripts will search for a ``config.ini`` file and will generate one if not found. You can specify a specific file using the ``--config`` parameter. The examples include MQTT translations for a Tasmota node with a power clamp (``mqtt_translation_power.py``), for a Tasmota node with a temperature (DHT11) sensor (``mqtt_translation_tasmota_temperature.py``), and for an RTL433 to MQTT gateway (``mqtt_translation_rtl433_temperature.py``) (see https://github.com/mverleun/RTL433-to-mqtt). The Tasmota examples are particularly interesting since they include decoding as JSON the original MQTT messages.

**Example using a Tasmota node with a temperature sensor**

<img src="https://github.com/jorgenavarroortiz/MQTT-translation/raw/main/img/mqtt-translation-tasmota-temperature.png" width="800">

## Different broker to subscribe and publish messages

The ``config_2brokers.ini`` file contains the credentials for two MQTT brokers. The first one is used to subscribe to a specific topic, and the second one is used to publish the processed data to the "translation" topic. The example (``mqtt_translation_pysense_measurements.py``) subscribes to the MQTT broker from a LoRaWAN network, translating the topic and processing one string to publish 4 different data (light, temperature, humidity and barometric pressure) to a second MQTT broker. This broker is, in turn, connected to a InfluxDB database whose data are used in a Grafana dashboard.

**Example using a FiPy node with a Pysense expansion board, taking data (over MQTT) from a LoRaWAN application server and sending its translation to a different MQTT broker**

<img src="https://github.com/jorgenavarroortiz/MQTT-translation/raw/main/img/mqtt-translation-lorawan-pysense.png" width="800">

If you require these scripts to be run from startup (e.g. in a Raspberry Pi), you can use ``crontab``.
