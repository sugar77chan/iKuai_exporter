import logging
from prometheus_client import Gauge


class TerminalMetricsExporter:
    def __init__(self, session, call_url, logger_name):
        self.session = session
        self.call_url = call_url
        self.logger = logging.getLogger(logger_name)

        self.upload_metric = Gauge(
            "ikuai_terminal_upload_bytes",
            "Upload bytes of terminal device",
            labelnames=["ip", "unit"]
        )
        self.download_metric = Gauge(
            "ikuai_terminal_download_bytes",
            "Download bytes of terminal device",
            labelnames=["ip", "unit"]
        )
        self.connect_num_metric = Gauge(
            "ikuai_terminal_connect_num",
            "Number of connections from terminal device",
            labelnames=["ip", "unit"]
        )
        self.terminal_total_metric = Gauge(
            "ikuai_terminal_total_count",
            "Total number of terminal devices",
            labelnames=[]
        )

    def fetch_and_collect(self):
        self.logger.info(f"[采集] 开始从 iKuai 路由器拉取 terminal 数据")
        try:
            payload = {
                "func_name": "monitor_lanip",
                "action": "show",
                "param": {
                    "FILTER1": "frequencies,=,",
                    "ORDER": "",
                    "ORDER_BY": "ip_addr_int",
                    "TYPE": "data,total",
                    "limit": "0,20",
                    "orderType": "IP"
                }
            }
            resp = self.session.post(self.call_url, json=payload)
            resp.raise_for_status()
            data = resp.json()

            if data.get("ErrMsg") != "Success":
                self.logger.error(f"终端信息采集失败: {data.get('ErrMsg')}")
                return

            terminals = data.get("Data", {}).get("data", [])
            self.terminal_total_metric.set(len(terminals))

            for terminal in terminals:
                ip = terminal.get("ip_addr", "")
                if not ip:
                    continue
                try:
                    upload = float(terminal.get("upload", 0))
                except Exception:
                    upload = 0.0
                try:
                    download = float(terminal.get("download", 0))
                except Exception:
                    download = 0.0
                try:
                    connect_num = float(terminal.get("connect_num", 0))
                except Exception:
                    connect_num = 0.0

                self.upload_metric.labels(ip=ip, unit="bytes").set(upload)
                self.download_metric.labels(ip=ip, unit="bytes").set(download)
                self.connect_num_metric.labels(ip=ip, unit="count").set(connect_num)

        except Exception as e:
            self.logger.exception(f"TerminalMetricsExporter异常: {e}")
