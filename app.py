from flask import Flask, render_template, request
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv
import pymysql
import os

load_dotenv()

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':

        nama = request.form['nama']
        email = request.form['email']
        file = request.files['gambar']

        # Upload ke Azure Blob Storage
        blob_service_client = BlobServiceClient(
            account_url=f"https://{os.getenv('AZURE_STORAGE_ACCOUNT')}.blob.core.windows.net",
            credential=os.getenv('AZURE_STORAGE_KEY')
        )

        blob_client = blob_service_client.get_blob_client(
            container=os.getenv('AZURE_CONTAINER'),
            blob=file.filename
        )

        blob_client.upload_blob(file)

        # URL file
        file_url = f"https://{os.getenv('AZURE_STORAGE_ACCOUNT')}.blob.core.windows.net/{os.getenv('AZURE_CONTAINER')}/{file.filename}"

        # Connect MySQL Azure
        conn = pymysql.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME'),
            port=int(os.getenv('DB_PORT')),
            ssl={'ssl': {}}
        )

        cursor = conn.cursor()

        sql = "INSERT INTO pelamar (nama, email, ktp_url) VALUES (%s, %s, %s)"
        cursor.execute(sql, (nama, email, file_url))

        conn.commit()

        cursor.close()
        conn.close()

        return "Data berhasil disimpan!"

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
