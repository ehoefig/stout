import logging
import gateway
from gateway import event_log
from gateway import zigbee_collector

__author__ = 'edzard'

# System config
logging.basicConfig(level=logging.DEBUG)

# Main config
gateway.working_directory = '/tmp'
gateway.logging_directory = '/tmp'
gateway.daemonize = False # Starts as a UNIX daemon if set to true
gateway.logger.setLevel(logging.WARNING)

# Event Log
event_log.logger.setLevel(logging.DEBUG)

# ZigBee Collector
zigbee_collector.logger.setLevel(logging.INFO)
zigbee_collector.serial_port = "/dev/tty.usbserial-A603UIAY"
zigbee_collector.baud_rate = 9600