import logging


class BaseExporter:
    def __init__(self, session, call_url, logger_name):
        self.session = session
        self.call_url = call_url
        self.logger = logging.getLogger(logger_name)

    def fetch_and_collect(self):
        """
        子类必须实现：从 iKuai 获取数据并设置 Prometheus 指标
        """
        raise NotImplementedError("子类必须实现 fetch_and_collect() 方法")

    @staticmethod
    def safe_float(val, default=0.0):
        try:
            return float(val)
        except (ValueError, TypeError):
            return default
