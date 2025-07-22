import time
import logging
import importlib
import inspect
import pkgutil
from http_handler import run_http_server

import ikuai_exporter


class ExporterManager:
    def __init__(self, session, call_url, exporter_cfg, logger_name):
        self.session = session
        self.call_url = call_url
        self.logger = logging.getLogger(logger_name)
        self.exporter_cfg = exporter_cfg
        self.logger_name = logger_name
        self.collectors = []

        self._load_exporters()

    def _load_exporters(self):
        package = ikuai_exporter
        prefix = package.__name__ + "."

        for _, modname, ispkg in pkgutil.iter_modules(package.__path__, prefix):
            if ispkg:
                continue
            try:
                module = importlib.import_module(modname)
            except Exception as e:
                self.logger.warning(f"无法导入模块 {modname}: {e}")
                continue

            for name, obj in inspect.getmembers(module, inspect.isclass):
                if name.endswith("Exporter") and callable(getattr(obj, "fetch_and_collect", None)):
                    try:
                        instance = obj(self.session, self.call_url, self.logger_name)
                        self.collectors.append(instance)
                        self.logger.info(f"加载监控器: {name} 来自 {modname}")
                    except Exception as e:
                        self.logger.error(f"实例化 {name} 失败: {e}")

    def run_forever(self, interval):
        port = self.exporter_cfg.get("port", 8000)
        run_http_server(port)
        self.logger.info(f"Prometheus HTTP 服务启动，监听端口 {port}")

        while True:
            for collector in self.collectors:
                try:
                    collector.fetch_and_collect()
                except Exception as e:
                    self.logger.error(f"采集器 {collector.__class__.__name__} 异常: {e}")
            time.sleep(interval)
