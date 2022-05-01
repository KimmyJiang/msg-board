import os
import boto3
from dotenv import load_dotenv
from flask import *
from mysql.connector.pooling import MySQLConnectionPool
from werkzeug.utils import secure_filename

load_dotenv()

db_config = {
    "host" : os.getenv("mysql_host"),
    "user" : os.getenv("mysql_user"),
	"password" : os.getenv("mysql_password"),
    "auth_plugin" : "mysql_native_password",
    "database" : os.getenv("database"),
    "buffered" : True
    }


dbpool = MySQLConnectionPool(
            **db_config,
            pool_name = "my_connection_pool",
            pool_size = 5
            )


UPLOAD_FOLDER = "files"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False
app.config["SECRET_KEY"] = "3jriwdf4"


## 檢查上傳檔案是否合法的函數
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


## 檔案上傳至 s3 bucket 存放
def upload_s3(filename, file):
    domain_name = os.getenv("cloudfront")
    try:
        s3 = boto3.resource("s3", aws_access_key_id=os.getenv("aws_key"), aws_secret_access_key=os.getenv("aws_secret"))
        s3.Object("msgpicture", filename).put(Body=file)
        return f"{domain_name}{filename}"
    except:
        return f"{filename} 圖片上傳失敗！"


## 修改資料庫
def revise_db(command, data):
    try:
        mypool = dbpool.get_connection()
        cursor = mypool.cursor()
        cursor.execute(command, data)
        mypool.commit()
        result = True
    except:
        mypool.rollback()
    finally:
        cursor.close()
        mypool.close()
    return result


## 查詢資料庫
def query_db(command, data):
    try:
        mypool = dbpool.get_connection()
        cursor = mypool.cursor()
        cursor.execute(command, data)
        result = cursor.fetchall()
    finally:
        cursor.close()
        mypool.close()
    return result


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/msg", methods=["POST"])
def upload():
    if request.method == "POST":
        if "file" not in request.files:
            flash("No file part")
            return redirect(request.url)
            
        file = request.files["file"]
        text = request.form["text"]


        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)


        if text and file and allowed_file(file.filename):
            ## secure_filename 函數來檢查上傳檔案檔名
            filename = secure_filename(file.filename)
            file_url = upload_s3(filename, file)

            add_msg = '''
            INSERT INTO store_msg ( comment, picture )
            VALUES ( %s, %s);
            '''
            
            revise_result = revise_db(add_msg, [text, file_url])

            if revise_result:
                query_msg = '''
                SELECT comment, picture 
                FROM store_msg
                ORDER BY id DESC 
                LIMIT 0, 1 ;
                '''

                query_result = query_db(query_msg,[])
                return jsonify(query_result)

@app.route("/api/msglist")
def msg_list():
    msg_list = '''
    SELECT comment, picture 
            FROM store_msg
            ORDER BY id DESC;
            '''
    allmsg = query_db(msg_list,[])
    return jsonify(allmsg)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3020, debug=True)