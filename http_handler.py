from http.server import HTTPServer, BaseHTTPRequestHandler
from prometheus_client import generate_latest, REGISTRY, CONTENT_TYPE_LATEST
import logging


class LoggingHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        logger = logging.getLogger("ikuai")
        client_ip = self.client_address[0]

        if self.path == "/metrics":
            logger.info(f"[访问] {client_ip} 请求 /metrics")
            try:
                metrics_data = generate_latest(REGISTRY)
                self.send_response(200)
                self.send_header("Content-Type", CONTENT_TYPE_LATEST)
                self.end_headers()
                self.wfile.write(metrics_data)
            except Exception as e:
                logger.exception(f"[错误] {client_ip} 访问 /metrics 出错: {e}")
                self.send_response(500)
                self.end_headers()
        else:
            logger.warning(f"[非法访问] {client_ip} 请求未知路径: {self.path}")
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        client_ip = self.client_address[0]
        logger = logging.getLogger("ikuai")
        logger.warning(f"[非法方法] {client_ip} 尝试以 POST 请求: {self.path}")
        self.send_response(405)
        self.end_headers()

    def log_message(self, format, *args):
        # 禁止 BaseHTTPRequestHandler 默认的 stdout 打印
        return


def run_http_server(port):
    server = HTTPServer(("0.0.0.0", port), LoggingHandler)
    import threading
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
