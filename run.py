import datetime
from loguru import logger
import argparse
from ui import app


def main():
    # 创建 ArgumentParser 对象
    parser = argparse.ArgumentParser(description="wifi management")

    # 添加参数
    parser.add_argument('--log_level', type=str, default="TRACE",
                        help='日志的等级：TRACE, DEBUG, INFO, WARNING, ERROR, CRITICAL')
    parser.add_argument('--log_file', type=str, default="./log", help='日志储存的目录')
    parser.add_argument("--no_console", type=bool, default=True, help='是否在消除控制台输出')
    parser.add_argument('--port', type=int, default=9001, help='服务的端口号')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='服务的主机地址')
    parser.add_argument('--debug', type=bool, default=False, help='是否开启flask的 debug模式')

    # 解析命令行参数
    args = parser.parse_args()
    log_level = args.log_level
    log_path = args.log_file
    print(args)

    if args.no_console:
        logger.remove()
        # 设置日志保存文件
        date = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        # 设置生成日志文件，utf-8编码，每天0点切割，zip压缩，保留3天，异步写入
        logger.add(sink=f"{log_path}/{date}", level=log_level, rotation='00:00', retention='3 days', compression='zip',
                   encoding='utf-8', enqueue=True)

    # 启动服务
    app.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == '__main__':
    main()
