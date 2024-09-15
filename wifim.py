import random
import threading
import time

from loguru import logger

from nmcli import scan_wifi, connect_wifi
import pickle
from login import *


class WifiM:
    def __init__(self):
        self.thread = None
        self.profiles = []
        self.load_profiles()
        self.current_SSID = None
        self.auto_connect = False

    def load_profiles(self):
        """
        加载配置文件
        :return:
        """
        try:
            logger.debug(f"加载配置文件")
            with open('profiles.pkl', 'rb') as f:
                self.profiles = pickle.load(f)
                logger.info(f"加载配置文件成功")
        except FileNotFoundError:
            self.profiles = []
            logger.debug(f"未找到配置文件，初始化为空")

    def save_profiles(self):
        """
        保存配置文件
        :return:
        """
        with open('profiles.pkl', 'wb') as f:
            pickle.dump(self.profiles, f)
            logger.info(f"保存配置文件成功")

    def get_profiles(self):
        return self.profiles

    def insert_profile(self, SSID, no=None, password=None, lgn=None):
        """
        插入配置，如果no为None则插入到最后
        :param SSID: 被插入文件的SSID
        :param no: 优先级
        :param password: 密码，可选
        :return:
        """

        # 参数校验
        logger.info(f'添加profile SSID: {SSID}, no: {no},lgn:{lgn}')
        if not SSID:
            return False

        len_profiles = len(self.profiles)
        if no is None or no == '':
            no = len_profiles
        no = int(no)
        if no < 0 or no > len_profiles:
            no = len_profiles

        if lgn is None or lgn == '':
            lgn = 'null'

        # 删除已存在的相同SSID的配置
        self.profiles = [profile for profile in self.profiles if profile.get('SSID') != SSID]
        profile = {'SSID': SSID, 'password': password, 'lgn': lgn}
        self.profiles.insert(no, profile)
        self.save_profiles()
        return [profile['SSID'] for profile in self.profiles]

    def remove_profile(self, SSID, no):
        """
        删除配置，需要提供匹配的SSID和no
        :param SSID: 被删除文件的SSID
        :param no: 被删除文件的优先级，从0开始
        :return:
        """
        logger.info(f'删除profile SSID: {SSID}, no: {no}')
        no = int(no)
        if self.profiles[no].get('SSID') == SSID:
            del self.profiles[no]
            self.save_profiles()
        else:
            logger.info(f'删除失败，{SSID}与{no}不匹配')
        return [profile['SSID'] for profile in self.profiles]

    # todo 修改no，password，lgn
    def update_profile(self, SSID, new_no=None, new_password=None, new_lgn=None):
        """
        修改配置优先级或密码

        :param SSID: 修改文件的SSID
        :param new_no: 新的优先级
        :param new_password: 新的密码
        :param new_lgn: 新的登录类名
        :return:
        """
        new_no = int(new_no)
        temp = {'SSID': SSID, 'password': new_password, 'lgn': 'null'}
        # 先取出原来的配置，然后删除
        for i in range(len(self.profiles)):
            if self.profiles[i].get('SSID') == SSID:
                temp = self.profiles[i]
                del self.profiles[i]
                break
        # 修改原来的配置
        if new_password:
            temp['password'] = new_password
        # 添加修改后的配置
        if temp:
            self.insert_profile(SSID, no=new_no, password=temp['password'])
            self.save_profiles()
            return True
        return False

    def scan(self):
        """
        扫描wifi，获取wifi列表
        需要sudo权限
        :return:
        """
        wifi_list = scan_wifi()
        if wifi_list[0]["In-Use"]:
            self.current_SSID = wifi_list[0]["SSID"]
        logger.trace(f"扫描到的wifi列表：\n {wifi_list}")
        return wifi_list

    def connect(self, SSID, password):
        output = connect_wifi(SSID, password)
        if 'successfully activated' in output:
            self.current_SSID = SSID
            logger.debug(f"连接成功：{output}")
            return True
        else:
            logger.debug(f"连接失败：{output}")
            return False

    def check_connect(self):
        """
        确保连接，如果未连接则尝试连接
        :return: bool 是否连接成功
        """
        # 扫描wifi
        wifi_list = self.scan()
        ssid_list = [wifi['SSID'] for wifi in wifi_list]
        for profile in self.profiles:
            ssid = profile['SSID']
            password = profile.get('password')
            # 如果wifi列表中没有这个wifi，跳过
            if ssid not in ssid_list:
                logger.debug(f"未找到{ssid}")
                continue
            # 连接wifi
            if self.current_SSID == ssid:
                # 已连接目标wifi
                logger.info(f"已连接{ssid}")
                return True
            else:
                # 未连接目标wifi
                logger.debug(f"连接{ssid}")
                res = self.connect(ssid, password)
                time.sleep(5)
                if res:
                    logger.info(f"连接{ssid}成功")
                    self.current_SSID = ssid
                    return True
                else:
                    logger.info(f"连接{ssid}失败")
                    self.current_SSID = None
                    continue
        logger.error("没有找到可用的wifi")
        return False

    def check_login(self):

        # 根据self.current_SSID获取对应的profile
        profile = None
        for p in self.profiles:
            if p['SSID'] == self.current_SSID:
                profile = p
                break
        if not profile:
            logger.error(f"未找到{self.current_SSID}的配置文件")
            return False
        lgn_str = profile.get('lgn')
        if not lgn_str:
            logger.debug(f"未配置登录类，登陆类为空")
            return False
        logger.debug(f"加载登录类{lgn_str}")
        lgn_class = class_registry[lgn_str]
        lgn = lgn_class()
        net_check = lgn.check()
        if net_check:
            logger.info("已联网")
            time.sleep(5)
            return True
        else:
            for i in range(5):
                logger.debug(f"无网络连接，尝试登录，第{i + 1}次")
                res_login = lgn.login()
                logger.debug(f"登录结果：{res_login}")
                if res_login:
                    info = lgn.info()
                    logger.info(f"登录后获取数据：{info}")
                if lgn.check():
                    logger.info("已成功切换到登录后的网络")
                    return True
                else:
                    logger.info("登录失败")
                    time.sleep(5)

    def keep_connect(self):
        logger.info("维持连接进程已启动")
        while True:
            if self.auto_connect:
                # 连接
                self.check_connect()
                # 登录
                self.check_login()
            else:
                logger.info("未开启自动连接")
            sleep_time = random.randint(60, 600)
            logger.info(f"等待{sleep_time}秒")
            time.sleep(sleep_time)

    def start_keep_connect(self):
        """
        启动keep_connect方法作为一个子线程
        """
        logger.debug("开启线程")
        self.thread = threading.Thread(target=self.keep_connect)
        self.thread.daemon = True  # 设置为守护线程，以便在主程序退出时自动结束
        self.thread.start()


if __name__ == "__main__":
    wifi = WifiM()
    res = wifi.connect("bjut_wifi2", "09877890")
    print(f"连接结果：{res}")
    time.sleep(5)
    wifi.auto_connect = True
    wifi.start_keep_connect()
    while True:
        time.sleep(1)
