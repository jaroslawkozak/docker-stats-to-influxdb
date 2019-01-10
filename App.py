from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
from lib.DataStorage import DataStorage
import docker
import logging

app = Flask('docker-stats-to-influx')
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

total_net = dict()


def store_docker_stats():
    values = dict()
    client = docker.from_env()
    for con in client.containers.list():
        stats = con.stats(stream=False)
        container_name = stats["name"]
        cpu_usage = calculate_cpu_percent(stats)

        values.update({"cpu_usage": cpu_usage})
        if "usage" in stats["memory_stats"]:
            values.update({"mem_usage": stats["memory_stats"]["usage"]})
        if "limit" in stats["memory_stats"]:
            values.update({"mem_limit": stats["memory_stats"]["limit"]})
        out_rx, out_tx = get_current_network_usage(stats)
        values.update({"rx_bytes": out_rx})
        values.update({"tx_bytes": out_tx})
    client.close()

    print(values)
    DataStorage.put(container_name, values)

def calculate_cpu_percent(stats):
    cpu_count = len(stats["cpu_stats"]["cpu_usage"]["percpu_usage"])
    cpu_percent = 0.0
    cpu_delta = float(stats["cpu_stats"]["cpu_usage"]["total_usage"]) - \
                float(stats["precpu_stats"]["cpu_usage"]["total_usage"])
    system_delta = float(stats["cpu_stats"]["system_cpu_usage"]) - \
                   float(stats["precpu_stats"]["system_cpu_usage"])
    if system_delta > 0.0:
        cpu_percent = cpu_delta / system_delta * 100.0 * cpu_count
    return cpu_percent


def get_current_network_usage(stats):
    name = stats["name"]
    networks = stats["networks"]
    rx_bytes = 0
    tx_bytes = 0
    for network_name, params in networks.items():
        rx_bytes = rx_bytes + params["rx_bytes"]
        tx_bytes = tx_bytes + params["tx_bytes"]

    if name not in total_net:
        total_net.update({
            name: {
                "rx_bytes" : 0,
                "tx_bytes" : 0
            }
        })

    if (total_net[name]["rx_bytes"] is None) or (total_net[name]["rx_bytes"] == 0):
        out_rx = 0
    else:
        out_rx = rx_bytes - total_net[name]["rx_bytes"]
    total_net[name]["rx_bytes"] = rx_bytes

    if (total_net[name]["tx_bytes"] is None) or (total_net[name]["tx_bytes"] == 0):
        out_tx = 0
    else:
        out_tx = tx_bytes - total_net[name]["tx_bytes"]
    total_net[name]["tx_bytes"] = tx_bytes
    return out_rx, out_tx


if __name__ == "__main__":
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(store_docker_stats, 'interval', seconds=5)
    sched.start()
    app.run(host='0.0.0.0', port=5556, debug=True, threaded=True)



