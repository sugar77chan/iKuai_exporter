# iKuai Exporter for Prometheus

基于 Prometheus 的 iKuai 路由器监控导出器，支持系统状态、终端信息、接口信息等指标采集。可以根据自己需求，如果需要获取更多指标，可以在ikuai_exporter中增加新的模块，但是需继承BaseExporter.
本代码在ikuai 3.7.20上测试通过，其他版本需自行测试，

##  功能特性

- 支持从 iKuai 路由器拉取如下指标：
  - 系统状态（CPU、内存、版本等）
  - 接口信息（流量、连接数、状态）
  - 局域网终端信息（上传/下载、连接数）
- 支持 Prometheus 拉取 `/metrics` 接口
- 支持日志记录访问情况、错误请求、采集行为
- 支持模块化配置和插件式采集器扩展
- 抽取配置文件，可以在配置文件中配置ikuai路由器的连接信息、exporter使用的端口、日志相关信息


##  安装

```bash
git clone https://github.com/yourname/ikuai-exporter.git
cd ikuai-exporter
pip install -r requirements.txt
```

## 贡献
欢迎提交 Issues 和 Pull Requests。

## 许可证
MIT License