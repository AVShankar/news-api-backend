from flask import Flask, render_template, request, redirect
from flaskext.mysql import MySQL
import yaml

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


@app.route('/categories')
def categories():
    cur = mysql.get_db().cursor()
    result = cur.execute('SELECT * FROM categories')
    if result > 0:
        categoryList = cur.fetchall()
        return render_template('index.html', categoryList = categoryList)

if __name__ == '__main__':
    app.run(debug=True)