# 使用官方 Python 鏡像
FROM python:3.8

# 設定工作目錄
WORKDIR /app

# 將本地檔案複製到容器中
COPY . /app

# 安裝應用程式依賴
RUN pip install --no-cache-dir -r requirements.txt

# 指定應用程式執行的命令
CMD ["python", "app.py"]
