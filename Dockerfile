# 建置最基礎的 image 也就是 python3.9
FROM python:3.9

# 定義當前的目錄位置
WORKDIR /message-board

# 將內容複製到工作目錄中
ADD . /message-board

# 運行 pip3 來安裝 Flask 應用程序的依賴套件
RUN pip3 install -r requirements.txt

# 執行python的指令語法
CMD ["python3","app.py"]