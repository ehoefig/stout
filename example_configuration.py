import logging

import gateway
from gateway import event_log, zigbee, network, sensors
from gateway.zigbee import zigbee_collector, zigbee_sensor_manager, ZigBeeAddress

__author__ = 'edzard'

# System config
logging.basicConfig(level=logging.DEBUG)

# Main config
gateway.working_directory = '/tmp'
gateway.logging_directory = '/tmp'
gateway.daemonize = False # Starts as a UNIX daemon if set to true
gateway.logger.setLevel(logging.WARNING)

# Network management
gateway.network.logger.setLevel(logging.INFO)

# ZigBee
zigbee.logger.setLevel(logging.DEBUG)
zigbee_collector.serial_port = "/dev/tty.usbserial-A603UIAY"
zigbee_collector.baud_rate = 9600
zigbee_sensor_manager.map[ZigBeeAddress.from_hex_string('0013A20040E621B0')] = sensors.ADXL335

# Event Log
event_log.logger.setLevel(logging.WARNING)
event_log.set_filter(signal="new_data|sensor_metadata_changed")   # Show all incoming data + metadata changes


