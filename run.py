import datetime
from loguru import logger
import argparse
from ui import app


def main():
    # 创建 ArgumentParser 对象
    parser = argparse.ArgumentParser(description="wifi management")

    # 添加参数
    parser.add_argument('--log_level', type=int, default=0,
                        help='日志的等级：0-TRACE, 1-DEBUG, 2-INFO, 3-WARNING, 4-ERROR, 5-CRITICAL')
    parser.add_argument('--log_file', type=str, default="./log", help='日志储存的目录')
    parser.add_argument('--port', type=int, default=9001, help='服务的端口号')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='服务的主机地址')
    parser.add_argument('--debug', type=bool, default=False, help='是否开启flask的 debug模式')

    # 解析命令行参数
    args = parser.parse_args()

    log_level = args.log_level
    log_path = args.log_file

    # 设置日志等级
    logger.remove()
    date = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    logger.add(f"{log_path}/+{date}", level=log_level)

    # 启动服务
    app.run(host=args.host, port=args.port, debug=args.debug)

    if __name__ == '__main__':
        main()
