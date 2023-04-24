from flask import Flask, render_template, request, make_response, session, redirect, url_for, flash
from dotenv import dotenv_values
import os, psycopg2
app = Flask(__name__)
app.secret_key = "Vinay"

config = dotenv_values(".env")      # config = {"USER": "foo", "EMAIL": "foo@example.org"}

# conn = psycopg2.connect(
#    host="localhost",
#    database="abcd",
#    user="postgres",
#    password="postgres"
# )

# -----------------------debug-----------------------
conn = psycopg2.connect(
    'postgres://ivinay718:19yIbwLGDAQq@ep-tiny-morning-297228.ap-southeast-1.aws.neon.tech/neondb?options=project%3Dep-tiny-morning-297228'
)

cur = conn.cursor()

# -----------------------debug-----------------------
# cur.execute("select * from login")
# rows = cur.fetchall()
# print(rows)

islogged = 0
uname = "username_when_no_user"
def updateLoginStatus():
   global islogged, uname
   if 'username' in session:
      uname = session['username']
      islogged = 1
   else:
      islogged = 0


@app.route('/', methods = ['GET', 'POST'])
def index():
   updateLoginStatus()

   print(islogged)
   # if request.method == 'POST':
   #    print(request.form["source"], request.form["destination"], request.form["date"], request.form["class"])
   #    return redirect(url_for("trains"))
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

   return render_template('login.html', error = error, islogged = islogged)


@app.route('/logout')
def logout():
   # remove the username from the session if it is there
   session.pop('username', None)
   updateLoginStatus()
   return redirect(url_for('index'))


@app.route('/signup', methods = ['GET', 'POST'])
def signup():
   if request.method == 'POST':
      print(request.form['username'], request.form['name'])

      try:
         cur.execute("insert into login values('{}', '{}')".format(request.form['username'], request.form['password']))
         
         # to persiste the changes
         conn.commit()
         flash('New account generation was successful!')
      except:
         flash("Account creation failed. Try again!")
         
      return redirect(url_for('login'))
   
   return render_template('signup.html',  islogged = islogged)


@app.route('/pnr_number', methods = ['GET', 'POST'])
def pnr_number():
   pnr_number = []
   if request.method == 'POST':
      cur.execute("select train_id, seat_no, src_station, dest_station \
                  from reserves inner join ticket using (ticket_id) \
                  inner join seat using (seat_id) where reserves.pnr = {}".format(request.form['pnr_number']))
      pnr_number = cur.fetchall()
   return render_template('pnr_number.html', islogged = islogged, pnr_number = pnr_number)

@app.route('/schedule', methods = ['GET', 'POST'])
def schedule():
   schedule = []
   train_no = None
   if request.method == 'POST':
      try:
         cur.execute("select * from train_schedule({})".format(request.form['train_no']))
         train_no = request.form['train_no']
         schedule = cur.fetchall()
      except Exception as err:
         print(err)
         flash("Something went wrong, maybe your input!")
         return redirect(url_for('index'))
   return render_template('schedule.html', train_no = train_no, route = schedule , islogged = islogged)

@app.route('/trains', methods = ['GET', 'POST'])
def trains():
   trains = []
   if request.method == 'POST':
      try:
         cur.execute("select * from availableRoute('{}', '{}', '{}', '{}')".format( request.form['date'], request.form['source'], request.form['destination'],request.form['class']))
         trains = cur.fetchall()
         for train in trains:
            print(train)
      except Exception as err:
         flash("Something went wrong, maybe your input!")
   return render_template('trains.html', trains = trains, islogged = islogged)

if __name__ == '__main__':
   app.run(debug=True)