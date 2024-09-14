import subprocess
import time
from loguru import logger


def scan_wifi():
    """
    扫描wifi，获取wifi列表
     需要sudo权限
    :return: list of {In-Use, BSSID, SSID, Mode, Channel, Rate, Signal, Bars, Security}
    """
    # 执行 nmcli 命令并捕获输出
    result0 = subprocess.run(['nmcli', 'device', 'wifi', 'rescan'], capture_output=True, text=True)
    logger.debug(f"重新扫描wifi：{result0.stdout}:::{result0.stderr}")
    time.sleep(1)
    result = subprocess.run(['nmcli', "-t", 'device', 'wifi', 'list'], capture_output=True, text=True)
    output = result.stdout

    # 用于存储wifi列表的字典列表
    wifi_list = []

    # 逐行解析输出
    lines = output.rstrip().split('\n')
    for line in lines:
        if line:  # 确保跳过空行
            line = line.replace(r"\:", "-")
            # 解析每行的数据
            parts = line.split(":")
            if len(parts) >= 3:
                # 构造字典
                wifi_dict = {
                    'In-Use': parts[0] == '*',
                    'BSSID': parts[1],
                    'SSID': parts[2],
                    'Mode': parts[3],
                    'Channel': parts[4],
                    'Rate': parts[5],
                    'Signal': parts[6],
                    'Bars': parts[7],
                    'Security': ' '.join(parts[8:])  # 将剩余的部分作为安全性信息
                }
                wifi_list.append(wifi_dict)
    return wifi_list


def connect_wifi(SSID, password, count=3):
    """
    连接wifi
    :param SSID: wifi名称
    :param password: wifi密码
    :return: shell文字输出
    """
    if count < 1:
        return "以尝试3次，连接失败"
    logger.debug(f"尝试连接{count}次")
    # 执行 nmcli 命令并捕获输出

    command = f'nmcli device wifi connect {SSID}'
    if password:
        command = command + " " + f'password {password}'
    result = subprocess.run([command],
                            capture_output=True,
                            text=True, shell=True)
    # 判断结果
    if result.stdout != '' and len(result.stdout) > 1:
        return result.stdout
    else:
        # 连接失败，尝试删除wifi配置再连接
        delete_result = subprocess.run(['nmcli', 'connection', 'delete', SSID], capture_output=True, text=True,
                                       shell=True)
        if "successfully" in delete_result.stdout:
            logger.debug(f"删除wifi配置成功：{delete_result.stdout}")
            return connect_wifi(SSID, password, count - 1)
        else:
            logger.debug(f"删除wifi配置失败：{delete_result.stderr}")
            return result.stderr
