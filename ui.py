import copy

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
    print(f"扫描到的wifi列表：{wifi_list}")
    return jsonify(wifi_list)


@app.route('/connect', methods=['POST'])
def connect():
    ssid = request.form['SSID']
    password = request.form['password']
    print(f"连接wifi：{ssid}，密码：{password}")
    output = wifi.connect(ssid, password)
    return jsonify({'message': output})


@app.route('/profile', methods=['GET'])
def profile():
    wifi_list_origin = wifi.get_profiles()
    wifi_list = copy.deepcopy(wifi_list_origin)
    for i in range(len(wifi_list)):
        if wifi_list[i]['password']:
            wifi_list[i].update({'password': '******'})
        else:
            wifi_list[i].update({'password': 'null'})
    return jsonify(wifi_list)


@app.route('/profile/insert', methods=['POST'])
def add_profile():
    ssid = request.form['SSID']
    password = request.form['password']
    no = request.form['No']
    lgn = request.form['lgn']
    res = wifi.insert_profile(ssid, no, password, lgn)
    return jsonify({'message': res})


@app.route('/profile/remove', methods=['POST'])
def delete_profile():
    ssid = request.form['SSID']
    no = request.form['No']
    res = wifi.remove_profile(ssid, no)
    return jsonify({'message': res})


@app.route('/profile/update', methods=['POST'])
def edit_profile():
    ssid = request.form['ssid']
    no = request.form['no']
    password = request.form['password']
    res = wifi.update_profile(ssid, new_no=no, new_password=password)
    return jsonify({'message': res})


@app.route('/keep', methods=['GET'])
def auto_connect():
    wifi.auto_connect = not wifi.auto_connect
    wifi.start_keep_connect()
    return jsonify({'message': wifi.auto_connect})


if __name__ == '__main__':
    app.run(debug=True, port=9001)
