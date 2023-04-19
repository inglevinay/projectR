from flask import Flask, render_template, request, make_response, session, redirect, url_for
import os, psycopg2
app = Flask(__name__)
app.secret_key = "Vinay"

conn = psycopg2.connect(
   host="localhost",
   database="flaskdb",
   user="postgres",
   password="postgres"
)

cur = conn.cursor()

cur.execute("select * from login")
rows = cur.fetchall()
print(rows)

@app.route('/')
def index():
   if 'username' in session:
      username = session['username']
      return 'Logged in as ' + username + '<br>' + \
         "<b><a href = '/logout'>click here to log out</a></b>"
   return "You are not logged in <br><a href = '/login'></b>" + \
      "click here to log in</b></a>"


@app.route('/login', methods = ['GET', 'POST'])
def login():
   if request.method == 'POST':
      session['username'] = request.form['username']
      session['password'] = request.form['password']

      cur.execute("select * from checklogin('{}', '{}')".format(session['username'], session['password']))
      status = cur.fetchall()
      print(status)

      return redirect(url_for('index'))
   # return '''
	
   # <form action = "" method = "post">
   #    <p><input type = text name = username></p>
   #    <p><input type = password name = password></p>
   #    <p><input type = submit value = Login/></p>

   # </form>
	
   # '''
   return render_template('login.html')

@app.route('/logout')
def logout():
   # remove the username from the session if it is there
   session.pop('username', None)
   return redirect(url_for('index'))


if __name__ == '__main__':
   app.run(debug=True)