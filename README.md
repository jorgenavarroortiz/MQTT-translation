# MQTT-translation

© Jorge Navarro-Ortiz (jorgenavarro@ugr.es), University of Granada

Python scripts that subscribe to specific MQTT topics, modify the content of the messages (e.g. format change) and publish the messages to different topics.

This may be useful to adapt to some platforms/programs, such as e.g. https://github.com/Nilhcem/home-monitoring-grafana which utilizes a specific MQTT topic format (``home/{peripheralName}/{temperature|humidity|battery|status}``) for the bridge between MQTT and InfluxDB. Similarly, it may be useful to process the content of the message, e.g. get several measurement values sent in the same topic and publish them to separate topics (e.g. one topic for temperature, another for humidity, ...).

The ``config.ini`` file contains the credentials for the MQTT broker. The examples include MQTT translations for a Tasmota node with a power clamp, for a Tasmota node with a temperature (DHT11) sensor, and for an RTL433 to MQTT gateway (see https://github.com/mverleun/RTL433-to-mqtt). The Tasmota examples are particularly interesting since they include decoding as JSON the original MQTT messages.

If you require these scripts to be run from startup (e.g. in a Raspberry Pi), you can use ``crontab``.

**Example using a Tasmota node with a temperature sensor**

<img src="https://github.com/jorgenavarroortiz/MQTT-translation/raw/main/img/mqtt-translation-tasmota-temperature.png" width="800">
