# main.py
from config_provider import get_config, get_logger_name
from logger import setup_logger
from auth import IKUAIAuth
from exporter_manager import ExporterManager


def main():
    # 1. 加载配置（已由 config_provider 初始化）
    config = get_config()

    # 2. 创建 logger
    log_config = config.get_log_config()
    logger = setup_logger(log_config)
    logger.info("启动 iKuai Exporter")

    # 3. 读取设备配置并登录
    device_cfg = config.get_device_config()
    try:
        ikuai = IKUAIAuth(
            ip=device_cfg["ip"],
            port=device_cfg.get("port", 80),
            username=device_cfg["username"],
            password=device_cfg["password"],
            login_retry=device_cfg.get("login_retry", 3),
            auto_login=True
        )
    except Exception as e:
        logger.error(f"登录 iKuai 设备失败: {e}")
        return

    # 4. 启动 Exporter
    exporter_cfg = config.get_exporter_config()
    try:
        manager = ExporterManager(
            session=ikuai.session,
            call_url=ikuai.call_url,
            exporter_cfg=exporter_cfg,
            logger_name=get_logger_name()
        )
        interval = exporter_cfg.get("interval")
        manager.run_forever(interval)
    except Exception as e:
        logger.exception(f"启动 Exporter 失败: {e}")


if __name__ == "__main__":
    main()
