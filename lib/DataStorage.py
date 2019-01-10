from influxdb import InfluxDBClient
import config
import datetime
import logging


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class DataStorage:
    client = InfluxDBClient(config.INFLUX_DB_CONFIG['host'],
                            config.INFLUX_DB_CONFIG['port'],
                            config.INFLUX_DB_CONFIG['username'],
                            config.INFLUX_DB_CONFIG['password'],
                            config.INFLUX_DB_CONFIG['db_name'])
    client.create_database(config.INFLUX_DB_CONFIG['db_name'])

    def __init__(self):
        return

    @staticmethod
    def put(measurement_type, value):
        logging.info("Sending data for storage. %s: %s", measurement_type, value)
        DataStorage.client.write_points(DataStorage.format(measurement_type, value))

    @staticmethod
    def format(container, values):
        return [
            {
                "measurement": "docker_stats",
                "tags": {
                    "container": container,
                },
                "time": datetime.datetime.utcnow(),
                "fields": values

            }
        ]
