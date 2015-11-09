import logging

import gateway
from gateway import network, zigbee
from gateway.zigbee.zigbee_collector import Collector
from gateway.zigbee.zigbee_sensor_manager import SensorManager
from gateway.helper import event_log
#from gateway.output import csv

__author__ = 'edzard'

# System config
logging.basicConfig(level=logging.DEBUG)

# Main config
gateway.working_directory = '/tmp'
gateway.logging_directory = '/tmp'
gateway.daemonize = False # Starts as a UNIX daemon if set to true
gateway.location = 'Berlin'
gateway.logger.setLevel(logging.WARNING)

# ZigBee
zigbee.logger.setLevel(logging.INFO)
collector = Collector("/dev/tty.usbserial-A603UIAY", 115200)
manager = SensorManager()
manager.map['0013A20040EAEBA3'] = zigbee.BNO055
manager.map['0013A20040E621B0'] = zigbee.ADXL335

# Network management
gateway.network.logger.setLevel(logging.INFO)

# Timer
#timer.logger.setLevel(logging.WARNING)

# Event Log
event_log.logger.setLevel(logging.INFO)
event_log.set_filter(signal="timer|new_data|discovered_sensor|sensor_metadata_changed")   # Show all incoming data + metadata changes

# CSV output
#csv.logger.setLevel(logging.DEBUG)
#csv.path = '/tmp/sensor_data.csv'

