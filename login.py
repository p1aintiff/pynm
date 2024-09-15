import re
import requests
from loguru import logger
from abc import ABC, abstractmethod

class_registry = {}


def register_class(class_name):
    def decorator(cls):
        class_registry[class_name] = cls
        return cls

    return decorator


class Login(ABC):
    def __init__(self):
        logger.info("init login class")
        self.check_url = "http://www.baidu.com"

    def check(self):
        """
        检查是否联网
        :return:
        """
        try:
            r = requests.get(self.check_url, timeout=2)
            return "www.baidu.com" in r.text
        except requests.exceptions.ConnectionError:
            return False
        except requests.exceptions.ReadTimeout:
            logger.info("超时")
            return False

    @abstractmethod
    def login(self):
        """
        未联网时登录
        :return:
        """
        pass

    @abstractmethod
    def info(self):
        """
        获取登陆后的信息
        :return:
        """
        pass


@register_class("null")
class Null(Login):
    def __init__(self):
        super().__init__()

    def login(self):
        return True

    def info(self):
        return "What can I say?"


@register_class("A229")
class A229(Login):
    def __init__(self):
        super().__init__()
        self.login_url = "http://20.10.21.221"
        self.info_url = "http://lgn.bjut.edu.cn/"
        self.account = "21110120"
        self.password = "Fantasies16@"

    def get_login_page(self):
        """
        get 登录页面，获取登录者基本信息
        :return:
        """
        url = "http://10.21.221.98"
        resp = requests.get(url)
        text = resp.text

        # 正则匹配
        pattern_v4serip = r"v4serip='(\d+\.\d+\.\d+\.\d+)'"
        pattern_v46ip = r"v46ip='(\d+\.\d+\.\d+\.\d+)'"

        # 尝试使用re.search()函数分别搜索匹配的IP地址
        match_v4serip = re.search(pattern_v4serip, text)
        match_v46ip = re.search(pattern_v46ip, text)

        self.v4serip = match_v4serip.group(1)
        self.v46ip = match_v46ip.group(1)
        logger.debug(f"v4serip: {self.v4serip}, v46ip: {self.v46ip}")

    def login(self):
        logger.debug("Login")
        self.get_login_page()
        url = f"http://10.21.221.98:801/eportal/portal/login?callback=dr1005&login_method=1&user_account={self.account}@campus&user_password={self.password}&wlan_user_ip={self.v46ip}&wlan_user_ipv6=&wlan_user_mac=000000000000&wlan_ac_ip=&wlan_ac_name=&jsVersion=4.2.1&terminal_type=1&lang=zh-cn&v=7012&lang=zh"
        payload = {}
        headers = {
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'DNT': '1',
            'Pragma': 'no-cache',
            'Referer': 'http://10.21.221.98/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0'
        }
        logger.debug(f"Login url: {url}")
        logger.debug(f"account: {self.account}")
        logger.debug(f"v46ip: {self.v46ip}")
        response = requests.request("GET", url, headers=headers, data=payload, timeout=2)
        # {"result":1,"msg":"Portal协议认证成功","ret_code":0}
        # {"result":0,"msg":"无法获取用户认证账号！","ret_code":1})
        # {"result": 0, "msg": "IP: 10.126.16.72 已经在线！", "ret_code": 2}

        if "成功" in response.text or "已经在线" in response.text:
            return True
        return False

    def info(self):
        print("使用数据")
        resp = requests.get(url=self.info_url)
        text = resp.text
        # 正则
        pattern_time = r"time='(\d+\s*)'"
        pattern_flow = r"flow='(\d+\s*)'"
        pattern_fee = r"fee='(\d+\s*)'"
        pattern_uid = r"uid='(\d+\s*)'"
        pattern_v4ip = r"v4ip='(\d+\.\d+\.\d+\.\d+\s*)'"

        match_time = re.search(pattern_time, text)
        match_flow = re.search(pattern_flow, text)
        match_fee = re.search(pattern_fee, text)
        match_uid = re.search(pattern_uid, text)
        match_v4ip = re.search(pattern_v4ip, text)

        if match_time:
            logger.info(f"Extracted time: {match_time.group(1)}")
            logger.info(f"Extracted flow: {match_flow.group(1)}")
            logger.info(f"Extracted fee: {match_fee.group(1)}")
            logger.info(f"Extracted uid: {match_uid.group(1)}")

            logger.info(f"Extracted v4ip: {match_v4ip.group(1)}")
            flow = match_flow.group(1)
            flow = flow.strip()
            flow = int(flow)
            flow0 = flow % 1024
            flow1 = (flow - flow0) / 1024
            readable_flow = ""
            if flow1 < 1024:
                readable_flow = str(flow1 * 1024) + " KByte"
            else:
                readable_flow = str(flow1) + " MByte"
            logger.debug(f"Readable flow: {readable_flow}")
            return {"time": match_time.group(1), "flow": readable_flow, "fee": match_fee.group(1),
                    "uid": match_uid.group(1), "v4ip": match_v4ip.group(1)}
        else:
            logger.debug("Failed to extract")
            return None


@register_class("LGN")
class Lgn(Login):
    def __init__(self):
        super().__init__()
        self.account = "21110120"
        self.passwrd = "Fantasies16@"
        self.url = "https://lgn.bjut.edu.cn/"
        self.info_url = "https://lgn.bjut.edu.cn/"

    def check_login(self):
        resp = requests.get(url=self.url)
        text = resp.text

        # 正则匹配
        pattern_v4serip = r"v4serip='(\d+\.\d+\.\d+\.\d+)'"
        pattern_v46ip = r"v46ip='(\d+\.\d+\.\d+\.\d+)'"

        # 尝试使用re.search()函数分别搜索匹配的IP地址
        match_v4serip = re.search(pattern_v4serip, text)
        match_v46ip = re.search(pattern_v46ip, text)

        self.v4serip = match_v4serip.group(1)
        self.v46ip = match_v46ip.group(1)

    def login(self):
        payload = f'DDDDD={self.account}&upass={self.passwrd}&v46s=1&v6ip=&f4serip={self.v4serip}&0MKKey='
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded',
            'DNT': '1',
            'Origin': 'https://lgn.bjut.edu.cn',
            'Pragma': 'no-cache',
            'Referer': 'https://lgn.bjut.edu.cn/',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0',
            'sec-ch-ua': '"Not)A;Brand";v="99", "Microsoft Edge";v="127", "Chromium";v="127"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"'
        }

        response = requests.request("POST", self.url, headers=headers, data=payload)

        text = response.text
        # print(text)
        # 正则匹配 结果
        if "<title>登录成功窗</title>" in text:
            print("Login successfully")
            return True
        return False

    def info(self):
        logger.debug("使用数据")
        resp = requests.get(url=self.info_url)
        text = resp.text
        # 正则
        pattern_time = r"time='(\d+\s*)'"
        pattern_flow = r"flow='(\d+\s*)'"
        pattern_fee = r"fee='(\d+\s*)'"
        pattern_uid = r"uid='(\d+\s*)'"
        pattern_v4ip = r"v4ip='(\d+\.\d+\.\d+\.\d+\s*)'"

        match_time = re.search(pattern_time, text)
        match_flow = re.search(pattern_flow, text)
        match_fee = re.search(pattern_fee, text)
        match_uid = re.search(pattern_uid, text)
        match_v4ip = re.search(pattern_v4ip, text)

        if match_time:
            logger.debug(f"Extracted time: {match_time.group(1)}")
            logger.debug(f"Extracted flow: {match_flow.group(1)}")
            logger.debug(f"Extracted fee: {match_fee.group(1)}")
            logger.debug(f"Extracted uid: {match_uid.group(1)}")

            logger.debug(f"Extracted v4ip: {match_v4ip.group(1)}")
            flow = match_flow.group(1)
            flow = flow.strip()
            flow = int(flow)
            flow0 = flow % 1024
            flow1 = (flow - flow0) / 1024
            readable_flow = ""
            if flow1 < 1024:
                readable_flow = str(flow1 * 1024) + " KByte"
            else:
                readable_flow = str(flow1) + " MByte"
            logger.debug(f"Readable flow: {readable_flow}")
            return {"time": match_time.group(1), "flow": readable_flow, "fee": match_fee.group(1),
                    "uid": match_uid.group(1), "v4ip": match_v4ip.group(1)}
        else:
            logger.debug("Failed to extract")
            return None


@register_class("Wlgn")
class Wlgn(Login):
    def __init__(self):
        super().__init__()
        self.account = "21110120"
        self.password = "Fantasies16@"

    def login(self):
        pass

    def info(self):
        pass


if __name__ == "__main__":
    lgn_class = class_registry["A229"]
    lgn = lgn_class()
    res = lgn.check()
    logger.debug(f"是否联网{res}")

    # res = lgn.login()
    # print(f"登录结果{res}")
