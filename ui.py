import copy
from loguru import logger
from flask import Flask, render_template, jsonify, request

from wifim import WifiM
wifi = WifiM()
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/scan', methods=['GET'])
def scan():
    wifi_list = wifi.scan()
    logger.info(f"扫描到的wifi数量：{len(wifi_list)}")
    return jsonify(wifi_list)


@app.route('/connect', methods=['POST'])
def connect():
    ssid = request.form['SSID']
    password = request.form['password']
    logger.info(f"连接wifi：{ssid}")
    output = wifi.connect(ssid, password)
    return jsonify({'message': output})


@app.route('/profile', methods=['GET'])
def profile():
    profile_list_origin = wifi.get_profiles()
    profile_list = copy.deepcopy(profile_list_origin)
    logger.info(f"获取到profile数量：{len(profile_list)}")
    for i in range(len(profile_list)):
        if profile_list[i]['password']:
            profile_list[i].update({'password': '******'})
        else:
            profile_list[i].update({'password': 'null'})
    return jsonify(profile_list)


@app.route('/profile/insert', methods=['POST'])
def add_profile():
    ssid = request.form['SSID']
    password = request.form['password']
    no = request.form['No']
    lgn = request.form['lgn']
    logger.info(f"添加profile：{ssid}")
    res = wifi.insert_profile(ssid, no, password, lgn)
    logger.debug(f"添加profile结果：{res}")
    return jsonify({'message': res})


@app.route('/profile/remove', methods=['POST'])
def delete_profile():
    ssid = request.form['SSID']
    no = request.form['No']
    logger.info(f"删除profile：{ssid}")
    res = wifi.remove_profile(ssid, no)
    logger.debug(f"删除profile结果：{res}")
    return jsonify({'message': res})


@app.route('/profile/update', methods=['POST'])
def edit_profile():
    ssid = request.form['ssid']
    no = request.form['no']
    password = request.form['password']
    logger.info(f"更新profile：{ssid}")
    res = wifi.update_profile(ssid, new_no=no, new_password=password)
    logger.debug(f"更新profile结果：{res}")
    return jsonify({'message': res})


@app.route('/keep', methods=['GET'])
def auto_connect():
    logger.info(f"自动连接状态：{wifi.auto_connect}")
    wifi.auto_connect = not wifi.auto_connect
    wifi.start_keep_connect()
    return jsonify({'message': wifi.auto_connect})

if __name__ == '__main__':
    app.run(debug=True, port=9001)
