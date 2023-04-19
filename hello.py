from flask import Flask, render_template, request, make_response, session, redirect, url_for, flash
import os, psycopg2
app = Flask(__name__)
app.secret_key = "Vinay"

conn = psycopg2.connect(
   host="localhost",
   database="abcd",
   user="postgres",
   password="postgres"
)

# -----------------------debug-----------------------
# conn = psycopg2.connect(
#     'postgres://ivinay718:19yIbwLGDAQq@ep-tiny-morning-297228.ap-southeast-1.aws.neon.tech/neondb?options=project%3Dep-tiny-morning-297228'
# )

cur = conn.cursor()

# -----------------------debug-----------------------
# cur.execute("select * from login")
# rows = cur.fetchall()
# print(rows)

@app.route('/')
def index():
   islogged = 0
   uname = "username_when_no_user"
   if 'username' in session:
      uname = session['username']
      islogged = 1

   return render_template("index.html", username = uname, islogged = islogged)


@app.route('/login', methods = ['GET', 'POST'])
def login():
   error = None
   if request.method == 'POST':
      session['username'] = request.form['username']
      session['password'] = request.form['password']

      cur.execute("select * from checklogin('{}', '{}')".format(session['username'], session['password']))
      status = cur.fetchone()
      
      if status[0] == 0:
         flash("You were successfully logged in!")
         return redirect(url_for('index'))
      elif status[0] == 1:
         error = "incorrect password for the username"
      elif status[0] == 2:
         error = "username does not exist"
      else:
         error = "unknown error"

   return render_template('login.html', error = error)

@app.route('/logout')
def logout():
   # remove the username from the session if it is there
   session.pop('username', None)
   return redirect(url_for('index'))

@app.route('/signup', methods = ['GET', 'POST'])
def signup():
   if request.method == 'POST':
      print(request.form['username'], request.form['name'])
      flash('New account generation was successful!')
      return redirect(url_for('login'))
   return render_template('signup.html')

@app.route('/schedule', methods = ['GET', 'POST'])
def schedule():
   schedule = []
   train_no = None
   if request.method == 'POST':
      cur.execute("select * from train_schedule({})".format(request.form['train_no']))
      schedule = cur.fetchall()
   return render_template('schedule.html', train_no = train_no, route = schedule)

if __name__ == '__main__':
   app.run(debug=True)