import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class StatUtils:
    total_net = dict()

    def __init__(self):
        return

    @staticmethod
    def get_stat_values(stats):
        values = dict()
        cpu_usage = StatUtils.__calculate_cpu_percent(stats)

        values.update({"cpu_usage": cpu_usage})
        if "usage" in stats["memory_stats"]:
            values.update({"mem_usage": stats["memory_stats"]["usage"]})
        if "limit" in stats["memory_stats"]:
            values.update({"mem_limit": stats["memory_stats"]["limit"]})
        out_rx, out_tx = StatUtils.__get_current_network_usage(stats)
        values.update({"rx_bytes": out_rx})
        values.update({"tx_bytes": out_tx})
        return values

    @staticmethod
    def __calculate_cpu_percent(stats):
        cpu_count = len(stats["cpu_stats"]["cpu_usage"]["percpu_usage"])
        cpu_percent = 0.0
        cpu_delta = float(stats["cpu_stats"]["cpu_usage"]["total_usage"]) - \
                    float(stats["precpu_stats"]["cpu_usage"]["total_usage"])
        system_delta = float(stats["cpu_stats"]["system_cpu_usage"]) - \
                       float(stats["precpu_stats"]["system_cpu_usage"])
        if system_delta > 0.0:
            cpu_percent = cpu_delta / system_delta * 100.0 * cpu_count
        return cpu_percent

    @staticmethod
    def __get_current_network_usage(stats):
        name = stats["name"]
        networks = stats["networks"]
        rx_bytes = 0
        tx_bytes = 0
        for network_name, params in networks.items():
            rx_bytes = rx_bytes + params["rx_bytes"]
            tx_bytes = tx_bytes + params["tx_bytes"]

        if name not in StatUtils.total_net:
            StatUtils.total_net.update({
                name: {
                    "rx_bytes" : 0,
                    "tx_bytes" : 0
                }
            })

        if (StatUtils.total_net[name]["rx_bytes"] is None) or (StatUtils.total_net[name]["rx_bytes"] == 0):
            out_rx = 0
        else:
            out_rx = rx_bytes - StatUtils.total_net[name]["rx_bytes"]
        StatUtils.total_net[name]["rx_bytes"] = rx_bytes

        if (StatUtils.total_net[name]["tx_bytes"] is None) or (StatUtils.total_net[name]["tx_bytes"] == 0):
            out_tx = 0
        else:
            out_tx = tx_bytes - StatUtils.total_net[name]["tx_bytes"]
        StatUtils.total_net[name]["tx_bytes"] = tx_bytes
        return out_rx, out_tx