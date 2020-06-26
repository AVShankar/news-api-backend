from flask import Flask, request, redirect, jsonify
from flaskext.mysql import MySQL
import datetime
import time
import math
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
    return jsonify({
        "Attention": "Avaiable api for the application",
        "For_Categories": "/categories",
        "To_Fetch-News": "/fetch-news?category={available-Category}&from={yyyy-mm-dd}&to={yyyy-mm-dd}",
        "To_List-News": "/list-news?category={available-Category}&from={yyyy-mm-dd}&to={yyyy-mm-dd}",
        "Z-Note": "Required params to be passed to get valid response"
    })


@app.route('/fetch-news')
def fetch_news():
    connection = mysql.connect()
    cur = connection.cursor()
    category = request.args.get('category')
    fromDate = request.args.get('from')
    toDate = request.args.get('to')
    apiKey = '2b77b1785b9d4ea6ab7eea9c12d4a9e8'
    if(category and fromDate and toDate != ""):
        newsURL = 'https://newsapi.org/v2/everything?q='+category+'&from=' + \
            fromDate+'&to='+toDate+'&sortBy=relevancy&apiKey='+apiKey
        content = requests.get(newsURL)
        content = content.json()
        for key in content['articles']:
            author = key['author']
            title = key['title']
            description = key['description']
            publishedAt = key['publishedAt']
            epochTimeStamp = time.mktime(datetime.datetime.strptime(
                publishedAt[:10], "%Y-%m-%d").timetuple())
            publishedAt = str(math.floor(epochTimeStamp))
            imgUrl = key['urlToImage']
            cur.execute("INSERT INTO news VALUES (%s, %s, %s, %s, %s, %s)",
                        (author, category, title, description, publishedAt, imgUrl))
            connection.commit()
        cur.close()
        return jsonify({
            "A-success": "News data successfully fetched",
            "content": content['articles']
        })

    else:
        return jsonify({"Error": "Something went wrong!"})


@app.route('/categories')
def categories():
    connection = mysql.connect()
    cur = connection.cursor()
    result = cur.execute('SELECT * FROM categories')
    if result > 0:
        categoryList = cur.fetchall()
        return jsonify({"availableCategories": categoryList})
    else:
        return jsonify({"Error":  "No record found"})


@app.route('/list-news')
def list_news():
    connection = mysql.connect()
    cur = connection.cursor()
    category = request.args.get('category')
    fromDate = request.args.get('from')
    toDate = request.args.get('to')

    if(category and fromDate and toDate != ""):
        fromDate = time.mktime(datetime.datetime.strptime(
            fromDate[:10], "%Y-%m-%d").timetuple())
        fromDate = str(math.floor(fromDate))
        toDate = time.mktime(datetime.datetime.strptime(
            toDate[:10], "%Y-%m-%d").timetuple())
        toDate = str(math.floor(toDate))
        result = cur.execute(
            'SELECT * FROM news WHERE Published_at BETWEEN %s AND %s AND Category = %s', (fromDate, toDate, category))
        if result > 0:
            newsData = cur.fetchall()
            return jsonify({"content": newsData})
        else:
            return jsonify({"Error": "No records found with the given constraints"})

    else:
        return jsonify({"Error": "Please match the required format"})


if __name__ == '__main__':
    app.run(debug=True)
