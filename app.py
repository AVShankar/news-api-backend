from flask import Flask, render_template, request, redirect, jsonify
from flaskext.mysql import MySQL
import json
import yaml
import requests

app = Flask(__name__)

dbDetails = yaml.full_load(open('db.yaml'))

app.config['MYSQL_DATABASE_HOST']=dbDetails['mysql_host']
app.config['MYSQL_DATABASE_USER']=dbDetails['mysql_user']
app.config['MYSQL_DATABASE_PASSWORD']=dbDetails['mysql_password']
app.config['MYSQL_DATABASE_DB']=dbDetails['mysql_db']

mysql = MySQL()
mysql.init_app(app)


@app.route('/')
def api_root():
    return redirect('/categories')


@app.route('/categories', methods=["POST", "GET"])
def categories():
    if request.method == "POST":
        select = request.form
        category = str(select['category']).lower()
        fromDate = str(select['fromDate'])
        toDate = str(select['toDate'])
        apiKey = '2b77b1785b9d4ea6ab7eea9c12d4a9e8'
        newsURL = 'https://newsapi.org/v2/everything?q='+category+'&from='+fromDate+'&to='+toDate+'&sortBy=relevancy&apiKey='+apiKey
        content = requests.get(newsURL)
        content = content.json()
        print(content)
        return jsonify({"content": content})
    cur = mysql.get_db().cursor()
    result = cur.execute('SELECT * FROM categories')
    if result > 0:
        categoryList = cur.fetchall()
        return render_template('index.html', categoryList = categoryList)

if __name__ == '__main__':
    app.run(debug=True)