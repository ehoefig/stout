import logging
import pid
import signal
import daemon
import argparse
import os
from pydispatch import dispatcher
from threading import Lock

__author__ = 'edzard'

CONFIG_UPDATE_SIGNAL = 'configuration-update'
START_SIGNAL = 'start'
STOP_SIGNAL = 'stop'

_name = 'gateway'
_config_filename = None
_running = False
_lock = Lock()
_log_file_handler = None

# Configuration
working_directory = '/tmp'
logging_directory = '/tmp'
daemonize = False
logger = logging.getLogger(_name)


def configure(filename):
    """
    Configures the gateway.
    A gateway can be re-configured during runtime. This will issue a 'configuration-update' event carrying the
    new configuration as named parameters.
    The following configuration parameters are valid
    name        The gateway process name
    workdir     Path to the working directory
    logdir
    daemonize   If true start as a UNIX daemon
    """
    global logger, _log_file_handler
    # Execute config file
    if filename is not None:
        try:
            with open(filename) as f:
                code = compile(f.read(), filename, 'exec')
                exec(code, globals())
        except FileNotFoundError as ex:
            logger.error("Cannot find file: {}".format(ex.filename))

    # Adding a file _handler
    logger.handlers.clear()
    logfile = os.path.join(logging_directory, _name + '.log')
    _log_file_handler = logging.FileHandler(logfile)
    logger.addHandler(_log_file_handler)

    # Inform others
    logger.info("{} configured from {}".format(_name, filename))
    dispatcher.send(CONFIG_UPDATE_SIGNAL, _name)


def start():
    global _lock, _running, logger
    dispatcher.send(START_SIGNAL, _name)
    _lock.acquire()
    _running = True
    logger.info("{} started".format(_name))


def stop():
    global _running, _lock, logger
    dispatcher.send(STOP_SIGNAL, _name)
    _running = False
    _lock.release()
    logger.info("{} stopped".format(_name))


def wait_for_end():
    global _running, _lock
    if _running:
        _lock.acquire()   # Current thread stops here until gateway thread is finished
        _lock.release()


def _interrupt(signum, frame):
    global logger
    logger.debug("received SIGINT")
    stop()


def _terminate(signum, frame):
    global logger
    logger.debug("received SIGTERM")
    stop()


def _configure(signum, frame):
    global logger, _config_filename
    logger.debug("received SIGHUP")
    configure(_config_filename)


# Configures and starts the gateway
if __name__ == "__main__":

    # Parse command line args
    parser = argparse.ArgumentParser(description='Sensor Data Collection Server and Cloud Gateway.')
    parser.add_argument('-c', '--config', type=str, metavar='CFG', help='configuration file')
    arguments = parser.parse_args()
    if hasattr(arguments, 'config'):
        _config_filename = os.path.abspath(arguments.config)

    # Process configuration
    configure(_config_filename)

    if daemonize:

        logger.info("Switching to daemon mode: current process will terminate.")

        # Make necessary arrangements for proper UNIX daemon behaviour
        context = daemon.DaemonContext(
            detach_process=daemonize,
            working_directory=working_directory,
            pidfile=pid.PidFile(piddir=working_directory, pidname=_name + '.pid'),
            files_preserve=[_log_file_handler.stream],
            signal_map={
                signal.SIGINT: _interrupt,
                signal.SIGTERM: _terminate,
                signal.SIGHUP: _configure
            }
        )

        # Start gateway
        with context:
            start()
            wait_for_end()

    else:

        # Install signal handlers
        signal.signal(signal.SIGINT, _interrupt)
        signal.signal(signal.SIGTERM, _terminate)
        signal.signal(signal.SIGHUP, _configure)

        # Start gateway, logging to stdout
        start()
        wait_for_end()