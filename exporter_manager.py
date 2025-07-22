import time
import logging
import importlib
import pkgutil
import inspect
import ikuai_exporter
from ikuai_exporter.base_exporter import BaseExporter
from prometheus_client import start_http_server


def load_exporters(session, call_url, logger_name):
    collectors = []
    logger = logging.getLogger(logger_name)

    for _, module_name, _ in pkgutil.iter_modules(ikuai_exporter.__path__):
        full_module_name = f"ikuai_exporter.{module_name}"
        module = importlib.import_module(full_module_name)

        for name, cls in inspect.getmembers(module, inspect.isclass):
            # 只实例化继承自 BaseExporter 的子类，但排除 BaseExporter 自身
            if issubclass(cls, BaseExporter) and cls is not BaseExporter:
                logger.info(f"加载监控器: {name} 来自 {full_module_name}")
                collectors.append(cls(session, call_url, logger_name))
    return collectors


class ExporterManager:
    def __init__(self, session, call_url, exporter_cfg, logger_name):
        self.session = session
        self.call_url = call_url
        self.logger = logging.getLogger(logger_name)
        self.exporter_cfg = exporter_cfg
        self.collectors = load_exporters(session, call_url, logger_name)

    def run_forever(self, interval):
        port = self.exporter_cfg.get("port", 8000)
        start_http_server(port)
        self.logger.info(f"Prometheus HTTP 服务启动，监听端口 {port}")

        while True:
            for collector in self.collectors:
                try:
                    collector.fetch_and_collect()
                except Exception as e:
                    self.logger.error(f"采集器 {collector.__class__.__name__} 异常: {e}")
            time.sleep(interval)
