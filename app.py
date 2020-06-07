from flask import Flask, render_template, request, redirect, jsonify
from flaskext.mysql import MySQL
import datetime,time,math
import json
import yaml
import requests

app = Flask(__name__)

dbDetails = yaml.full_load(open('db.yaml'))

app.config['MYSQL_DATABASE_HOST'] = dbDetails['mysql_host']
app.config['MYSQL_DATABASE_USER'] = dbDetails['mysql_user']
app.config['MYSQL_DATABASE_PASSWORD'] = dbDetails['mysql_password']
app.config['MYSQL_DATABASE_DB'] = dbDetails['mysql_db']

mysql = MySQL()
mysql.init_app(app)


@app.route('/')
def api_root():
    return redirect('/categories')


@app.route('/categories', methods=["POST", "GET"])
def categories():
    connection = mysql.connect()
    if request.method == "POST":
        select = request.form
        category = str(select['category']).lower()
        fromDate = str(select['fromDate'])
        toDate = str(select['toDate'])
        apiKey = '2b77b1785b9d4ea6ab7eea9c12d4a9e8'
        newsURL = 'https://newsapi.org/v2/everything?q='+category+'&from=' + \
            fromDate+'&to='+toDate+'&sortBy=relevancy&apiKey='+apiKey
        content = requests.get(newsURL)
        content = content.json()
        cur = connection.cursor()
        for key in content['articles']:
            author = key['author']
            title = key['title']
            description = key['description']
            publishedAt = key['publishedAt']
            epochTimeStamp = time.mktime(datetime.datetime.strptime(publishedAt[:10], "%Y-%m-%d").timetuple())
            publishedAt = str(math.floor(epochTimeStamp))
            imgUrl = key['urlToImage']
            cur.execute("INSERT INTO news VALUES (%s, %s, %s, %s, %s, %s)", (author, category, title, description, publishedAt, imgUrl))
            connection.commit()
        cur.close()
        return jsonify({"content": content['articles']})
    cur = connection.cursor()
    result = cur.execute('SELECT * FROM categories')
    categoryList = ""
    if result > 0:
        categoryList = cur.fetchall()
        return render_template('index.html', categoryList=categoryList)
    return render_template('index.html', categoryList=categoryList)

@app.route('/list-news', methods=["POST", "GET"])
def list_news():
    if request.method == "POST":
        connection = mysql.connect()
        cur = connection.cursor()
        select = request.form
        category = str(select['category']).lower()
        fromDate = str(select['fromDate'])
        toDate = str(select['toDate'])
        if fromDate and toDate != "":
            fromDate = time.mktime(datetime.datetime.strptime(fromDate[:10], "%Y-%m-%d").timetuple())
            fromDate = str(math.floor(fromDate))
            toDate = time.mktime(datetime.datetime.strptime(toDate[:10], "%Y-%m-%d").timetuple())
            toDate = str(math.floor(toDate))
            result = cur.execute('SELECT * FROM news WHERE Published_at BETWEEN %s AND %s AND Category = %s', (fromDate, toDate, category))
            if result > 0:
                newsData = cur.fetchall()
                return render_template('list-news.html', newsData=newsData)

    connection = mysql.connect()
    cur = connection.cursor()
    result = cur.execute('SELECT * FROM categories')
    categoryList = ""
    if result > 0:
        categoryList = cur.fetchall()
        return render_template('list-news.html', categoryList=categoryList)
    return render_template('list-news.html', categoryList=categoryList)

if __name__ == '__main__':
    app.run(debug=True)
