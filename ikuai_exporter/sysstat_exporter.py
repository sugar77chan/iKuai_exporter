import logging
from prometheus_client import Gauge


class SystemMetricsExporter:
    def __init__(self, session, call_url, logger_name):
        self.session = session
        self.call_url = call_url
        self.logger = logging.getLogger(logger_name)

        self.cpu_metric = Gauge(
            "ikuai_cpu_usage_percent", "CPU usage percent", labelnames=["core", "unit"]
        )
        self.memory_metric = Gauge(
            "ikuai_memory_kb", "Memory metrics from iKuai (except used percent)", labelnames=["type", "unit"]
        )
        self.memory_used_percent_metric = Gauge(
            "ikuai_memory_used_percent", "Memory used percent from iKuai", labelnames=["type", "unit"]
        )
        self.stream_metric = Gauge(
            "ikuai_stream_info", "Stream info from iKuai", labelnames=["type", "unit"]
        )
        self.version_metric = Gauge(
            "ikuai_version_info", "Version info from iKuai",
            labelnames=["version", "build_date", "arch", "sysbit"]
        )
        self.version_set = False

    def fetch_and_collect(self):
        self.logger.info(f"[采集] 开始从 iKuai 路由器拉取 sysstat 数据")
        try:
            payload = {
                "func_name": "sysstat",
                "action": "show",
                "param": {"TYPE": "verinfo,cpu,memory,stream,cputemp"}
            }
            resp = self.session.post(self.call_url, json=payload)
            resp.raise_for_status()
            data = resp.json()

            if data.get("ErrMsg") != "Success":
                self.logger.error(f"Sysstat采集失败: {data.get('ErrMsg')}")
                return

            sys_data = data.get("Data", {})

            # CPU
            cpu_list = sys_data.get("cpu", [])
            for i, value in enumerate(cpu_list):
                try:
                    usage = float(value.strip('%')) if isinstance(value, str) else float(value)
                except Exception:
                    usage = 0.0
                core_label = "all" if i == 0 else f"core{i - 1}"
                self.cpu_metric.labels(core=core_label, unit="percent").set(usage)

            # Memory
            memory = sys_data.get("memory", {})
            for key, value in memory.items():
                if key == "used":
                    try:
                        used_percent = float(value.strip('%')) if isinstance(value, str) else float(value)
                    except Exception:
                        used_percent = 0.0
                    self.memory_used_percent_metric.labels(type=key, unit="percent").set(used_percent)
                else:
                    try:
                        self.memory_metric.labels(type=key, unit="KB").set(float(value))
                    except Exception:
                        self.memory_metric.labels(type=key, unit="KB").set(0)

            # Stream
            stream = sys_data.get("stream", {})
            for key, value in stream.items():
                unit = "count" if key == "connect_num" else "bytes"
                try:
                    self.stream_metric.labels(type=key, unit=unit).set(float(value))
                except Exception:
                    self.stream_metric.labels(type=key, unit=unit).set(0)

            # Version
            if not self.version_set and "verinfo" in sys_data:
                verinfo = sys_data["verinfo"]
                self.version_metric.labels(
                    version=verinfo.get("verstring", ""),
                    build_date=str(verinfo.get("build_date", "")),
                    arch=verinfo.get("arch", ""),
                    sysbit=verinfo.get("sysbit", "")
                ).set(1)
                self.version_set = True

        except Exception as e:
            self.logger.exception(f"SystemMetricsExporter异常: {e}")
