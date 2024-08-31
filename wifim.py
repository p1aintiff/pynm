import random
import threading
import time

from nmcli import scan_wifi, connect_wifi
import pickle
from login import *


class WifiM:
    def __init__(self):
        self.profiles = []
        self.load_profiles()
        self.current_SSID = None
        self.auto_connect = False

    def load_profiles(self):
        try:
            with open('profiles.pkl', 'rb') as f:
                self.profiles = pickle.load(f)
        except FileNotFoundError:
            self.profiles = []

    def save_profiles(self):
        with open('profiles.pkl', 'wb') as f:
            pickle.dump(self.profiles, f)

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
        print(f'添加profile SSID: {SSID}, no: {no}, password: {password}')
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
        :param no: 被删除文件的优先级
        :return:
        """
        no = int(no)
        if self.profiles[no].get('SSID') == SSID:
            del self.profiles[no]
            self.save_profiles()
        else:
            print(f'删除失败，{SSID}与{no}不匹配')
        return [profile['SSID'] for profile in self.profiles]

    def update_profile(self, SSID, new_no=None, new_password=None):
        """
        修改配置优先级

        :param SSID: 修改文件的SSID
        :param new_no: 新的优先级
        :param new_password: 新的密码
        :return:
        """
        new_no = int(new_no)
        temp = None
        for i in range(len(self.profiles)):
            if self.profiles[i].get('SSID') == SSID:
                temp = self.profiles[i]
                del self.profiles[i]
                break
        # 修改密码
        if new_password:
            temp['password'] = new_password
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
        return wifi_list

    def connect(self, SSID, password):
        output = connect_wifi(SSID, password)
        if 'successfully activated' in output:
            self.current_SSID = SSID
            return True
        else:
            print(f"连接失败：{output}")
            return False

    def keep_connect(self):
        print("开始维护连接")
        while True:
            if self.auto_connect:
                # 扫描wifi
                wifi_list = self.scan()
                for profile in self.profiles:
                    ssid = profile['SSID']
                    password = profile.get('password')
                    # 如果wifi列表中没有这个wifi，跳过
                    if ssid not in [wifi['SSID'] for wifi in wifi_list]:
                        print(f"未找到{ssid}")
                        continue
                    # 检查是否已经连接这个wifi
                    if self.current_SSID == ssid:
                        print(f"已连接{ssid}")
                        lgn_class = class_registry["null"]
                        lgn = lgn_class()
                        if lgn.check():
                            print(f"保持连接")
                        else:
                            print("当前连接无网络，尝试下一个网络")
                            break
                    else:
                        # 连接wifi
                        print(f"连接{ssid}，密码{password}")
                        res = self.connect(ssid, password)
                        time.sleep(5)
                        if not res:
                            print(f"连接{ssid}失败")
                            continue
                        else:
                            print(f"连接{ssid}成功")
                    # 登录
                    lgn_str = profile.get('lgn')
                    if lgn_str:
                        print(f"加载登录类{lgn_str}")
                        lgn_class = class_registry[lgn_str]
                        lgn = lgn_class()
                        net_check = lgn.check()
                        if net_check:
                            print("已联网")
                            time.sleep(5)
                            break
                        else:
                            count = 0
                        while count < 5:
                            count += 1
                            print(f"无网络连接，尝试登录，第{count}次")
                            res_login = lgn.login()
                            print(f"登录结果：{res_login}")
                            if res_login:
                                info = lgn.info()
                                print(f"登录后获取数据：{info}")
                                break
            else:
                print("未开启")
            sleep_time = random.randint(60, 600)
            print(f"等待{sleep_time}秒")
            time.sleep(sleep_time)

    def start_keep_connect(self):
        """
        启动keep_connect方法作为一个子线程
        """
        print("开启线程")
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
