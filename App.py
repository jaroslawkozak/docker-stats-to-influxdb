from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
from lib.DataStorage import DataStorage
from lib.StatUtils import StatUtils
import docker
import logging

app = Flask('docker-stats-to-influx')
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def store_docker_stats():
    client = docker.from_env()
    for con in client.containers.list():
        stats = con.stats(stream=False)
        container_name = stats["name"]
        DataStorage.put(container_name, StatUtils.get_stat_values(stats))
    client.close()

if __name__ == "__main__":
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(store_docker_stats, 'interval', seconds=5)
    sched.start()
    app.run(host='0.0.0.0', port=5556, debug=True, threaded=True)



