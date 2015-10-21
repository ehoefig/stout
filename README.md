
# Sensor Data Collection and Fusion Gateway (STOUT)

Extendable framework for collection, fusion, enrichment and dissemination of sensor data in Python 3. Used by the pervasive systems engineering group at Beuth University, Berlin. Sensor data is currently collected via ZigBee. The sensor data (currently 3-axis acceleration samples) is fused with metadata and disseminated to a cloud backend via REST.

## Dependencies

pydispatch, python-daemon, pid and (depending on the extensions): xbee
