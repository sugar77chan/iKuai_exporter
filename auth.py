# auth.py
import requests
import hashlib
import base64
import json
import threading
import logging
from config_provider import get_logger_name

class IKUAIAuth:
    def __init__(self, ip, username, password, login_retry=3, port=80, auto_login=False):
        self.ip = ip
        self.username = username
        self.password = password
        self.port = port
        self.base_url = f"http://{self.ip}:{self.port}"
        self.login_url = f"{self.base_url}/Action/login"
        self.call_url = f"{self.base_url}/Action/call"
        self.session = requests.Session()
        self.login_retry = login_retry
        self.lock = threading.Lock()
        self.logged_in = False
        self.logger = logging.getLogger(get_logger_name())
        if auto_login:
            self.login()

    def _encode_password_md5(self):
        return hashlib.md5(self.password.encode()).hexdigest()

    def _encode_pass_base64(self):
        raw = ("salt_11" + self.password).encode("ASCII")
        return base64.b64encode(raw).decode()

    def login(self):
        with self.lock:
            payload = {
                "username": self.username,
                "passwd": self._encode_password_md5(),
                "pass": self._encode_pass_base64(),
                "remember_password": ""
            }
            headers = {
                "Content-Type": "application/json;charset=utf-8",
                "Accept": "application/json"
            }
            try:
                resp = self.session.post(self.login_url, data=json.dumps(payload), headers=headers)
                resp.raise_for_status()
                result = resp.json()
                if result.get("Result") != 10000:
                    raise Exception(f"登录失败: {result.get('ErrMsg')}")
                self.logged_in = True
                self.logger.info(f"成功登录到设备 {self.ip}")
            except Exception as e:
                self.logged_in = False
                raise e

    def safe_post(self, payload):
        """
        安全调用接口，如 session 失效自动重新登录并重试
        """
        attempt = 0
        while attempt <= self.login_retry:
            try:
                resp = self.session.post(self.call_url, data=json.dumps(payload))
                resp.raise_for_status()
                result = resp.json()

                # 会话失效，Result = 30000
                if result.get("Result") == 30000:
                    attempt += 1
                    self.logger.warning(f"[{self.ip}] 会话失效，尝试重新登录 ({attempt}/{self.login_retry})")
                    self.logged_in = False
                    self.login()
                    continue  # retry
                return resp
            except requests.RequestException as e:
                raise Exception(f"网络请求失败: {e}")
            except ValueError:
                raise Exception("返回非 JSON 格式")
            except Exception as e:
                raise e
