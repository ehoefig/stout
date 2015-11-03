import logging

import gateway
from gateway import network, zigbee
from gateway.zigbee import zigbee_collector, zigbee_sensor_manager
from gateway.helper import event_log

__author__ = 'edzard'

# System config
logging.basicConfig(level=logging.DEBUG)

# Main config
gateway.working_directory = '/tmp'
gateway.logging_directory = '/tmp'
gateway.daemonize = False # Starts as a UNIX daemon if set to true
gateway.location = 'Berlin'
gateway.logger.setLevel(logging.WARNING)

# Timer
#timer.logger.setLevel(logging.WARNING)

# Network management
gateway.network.logger.setLevel(logging.INFO)

# ZigBee
zigbee.logger.setLevel(logging.DEBUG)
zigbee_collector.serial_port = "/dev/tty.usbserial-A603UIAY"
zigbee_collector.baud_rate = 9600
zigbee_sensor_manager.map['0013A20040EAEBA3'] = zigbee.BNO055
#zigbee_sensor_manager.map[ZigBeeAddress.from_hex_string('0013A20040E621B0')] = definitions.ADXL335

# Event Log
event_log.logger.setLevel(logging.WARNING)
event_log.set_filter(signal="timer|new_data|discovered_sensor|sensor_metadata_changed")   # Show all incoming data + metadata changes


