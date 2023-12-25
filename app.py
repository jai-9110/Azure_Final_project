from flask import Flask, render_template, request, redirect, url_for, jsonify
from azure.cosmos import CosmosClient
import random

app = Flask(__name__)

# Cosmos DB 帳戶資訊
cosmosdb_endpoint = "https://reservation-information-db.documents.azure.com:443/"
cosmosdb_key = "2czorNJsNrjvHQ7es96wSGE1MNxpGnSkUTGdXomWvfiImRs3Bbr7K2Cf1iebY75EMcjDFcrb9l8sACDbtx7eWw=="
database_name = "reservation-information-db"
container_name = "reservation-container"

client = CosmosClient(cosmosdb_endpoint, cosmosdb_key)
database = client.get_database_client(database_name)
container = database.get_container_client(container_name)

# 下次课守時間
next_consultation_time = ""
id = 0

@app.route("/")
def index():
    return render_template('index.html', next_consultation_time=next_consultation_time)

@app.route("/success", methods=['POST'])
def success():
    # 獲取表單數據
    date_value = request.form['date']
    student_id_value = request.form['studentID']
    name_value = request.form['name']

    global id 
    id += 1
    id_value = str(id)

    # 插入資料到 Cosmos DB
    item = {
        'id': id_value,
        'date': date_value,
        'studentID': student_id_value,
        'name': name_value
    }
    
    container.create_item(body=item)

    # 渲染 success.html 頁面，並傳遞表單數據
    return render_template('success.html', studentID=student_id_value, name=name_value)

@app.route("/manager")
def manager():
    # 從 Cosmos DB 中讀取預約資訊
    query = "SELECT * FROM c"
    items = list(container.query_items(query, enable_cross_partition_query=True))

    return render_template('manager.html', reservation_information=items)

@app.route("/filter_by_date", methods=['POST'])
def filter_by_date():
    selected_date = request.form['date']

    # 從 Cosmos DB 中按日期篩選預約資訊
    query = f"SELECT * FROM c WHERE c.date = '{selected_date}'"
    items = list(container.query_items(query, enable_cross_partition_query=True))

    return render_template('partials/reservation_table.html', reservation_information=items)

@app.route("/show_all_data", methods=['GET'])
def show_all_data():
    # 從 Cosmos DB 中讀取所有預約資訊
    query = "SELECT * FROM c"
    items = list(container.query_items(query, enable_cross_partition_query=True))

    return render_template('partials/reservation_table.html', reservation_information=items)

@app.route("/update_next_ta_time", methods=['POST'])
def update_next_ta_time():
    global next_consultation_time
    next_consultation_time = request.form['next_consultation']
    return redirect(url_for('index'))

@app.route("/query-appointments", methods=['GET'])
def query_appointments():
    selected_date = request.args.get('date')

    # 從 Cosmos DB 中按日期篩選預約資訊
    query = f"SELECT VALUE COUNT(1) FROM c WHERE c.date = '{selected_date}'"
    result = list(container.query_items(query, enable_cross_partition_query=True))

    return jsonify({'count': result[0]})
    

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
