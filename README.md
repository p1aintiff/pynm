

### 下载代码
```bash
git clone https://github.com/p1aintiff/pynm.git && cd pynm
```

### 使用
**1 创建python环境**  
通过conda
```bash
conda create -n pynm python=3.10
conda activate pynm
pip install -r requirements.txt
```

通过venv
```bash
python -m venv pynm
source pynm/bin/activate
pip install -r requirements.txt
```

**2 运行**
直接运行
```bash
python run.py --host "0.0.0.0" --port "9001" --log_level "TRACE" --log_file "./log" --debug False --no_console True
```
后台运行
```bash
nohup python run.py --host "0.0.0.0" --port "9001" --log_level "TRACE" --log_file "./log" --debug False --no_console True > last.log 2>&1 &
```
