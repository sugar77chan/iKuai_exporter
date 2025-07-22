from prometheus_client import Gauge
from ikuai_exporter.base_exporter import BaseExporter


class IfaceMetricsExporter(BaseExporter):
    def __init__(self, session, call_url, logger_name):
        super().__init__(session, call_url, logger_name)

        self.iface_check_status = Gauge(
            "ikuai_iface_check_status",
            "Interface check status (1=success, 0=fail)",
            labelnames=["interface", "parent_interface"]
        )
        self.iface_stream_upload = Gauge(
            "ikuai_iface_stream_upload_bytes",
            "Interface stream upload bytes",
            labelnames=["interface", "unit"]
        )
        self.iface_stream_download = Gauge(
            "ikuai_iface_stream_download_bytes",
            "Interface stream download bytes",
            labelnames=["interface", "unit"]
        )
        self.iface_stream_total_up = Gauge(
            "ikuai_iface_stream_total_upload_bytes",
            "Interface total upload bytes",
            labelnames=["interface", "unit"]
        )
        self.iface_stream_total_down = Gauge(
            "ikuai_iface_stream_total_download_bytes",
            "Interface total download bytes",
            labelnames=["interface", "unit"]
        )
        self.iface_stream_connect_num = Gauge(
            "ikuai_iface_stream_connect_num",
            "Interface stream connect number",
            labelnames=["interface", "unit"]
        )

    def fetch_and_collect(self):
        try:
            payload = {
                "func_name": "monitor_iface",
                "action": "show",
                "param": {"TYPE": "iface_check,iface_stream"}
            }
            resp = self.session.post(self.call_url, json=payload)
            resp.raise_for_status()
            data = resp.json()

            if data.get("ErrMsg") != "Success":
                self.logger.error(f"Iface采集失败: {data.get('ErrMsg')}")
                return

            iface_data = data.get("Data", {})

            for item in iface_data.get("iface_check", []):
                status = 0 if item.get("result") == "fail" else 1
                self.iface_check_status.labels(
                    interface=item.get("interface", ""),
                    parent_interface=item.get("parent_interface", "")
                ).set(status)

            for item in iface_data.get("iface_stream", []):
                iface = item.get("interface", "")
                self.iface_stream_upload.labels(interface=iface, unit="bytes").set(
                    self.safe_float(item.get("upload", 0)))
                self.iface_stream_download.labels(interface=iface, unit="bytes").set(
                    self.safe_float(item.get("download", 0)))
                self.iface_stream_total_up.labels(interface=iface, unit="bytes").set(
                    self.safe_float(item.get("total_up", 0)))
                self.iface_stream_total_down.labels(interface=iface, unit="bytes").set(
                    self.safe_float(item.get("total_down", 0)))

                connect_num_val = item.get("connect_num", "0")
                connect_num = self.safe_float(connect_num_val, 0.0) if connect_num_val != "--" else 0.0
                self.iface_stream_connect_num.labels(interface=iface, unit="count").set(connect_num)

        except Exception as e:
            self.logger.exception(f"IfaceMetricsExporter异常: {e}")
