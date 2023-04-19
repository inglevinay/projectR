from flask import Flask, render_template, request, make_response, session, redirect, url_for, flash
import os, psycopg2
app = Flask(__name__)
app.secret_key = "Vinay"

# conn = psycopg2.connect(
#    host="localhost",
#    database="flaskdb",
#    user="postgres",
#    password="postgres"
# )

# cur = conn.cursor()

# cur.execute("select * from login")
# rows = cur.fetchall()
# print(rows)

@app.route('/')
def index():
   # if 'username' in session:
   #    username = session['username']
   #    return 'Logged in as ' + username + '<br>' + \
   #       "<b><a href = '/logout'>click here to log out</a></b>"
   # return "You are not logged in <br><a href = '/login'></b>" + \
   #    "click here to log in</b></a>"

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

      # cur.execute("select * from checklogin('{}', '{}')".format(session['username'], session['password']))
      # status = cur.fetchall()
      # print(status)
      if session['username'] == 'admin' and session['password'] == 'admin':
         flash("You were successfully logged in!")
         return redirect(url_for('index'))
      else:
         error = "invalid username or password"

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


if __name__ == '__main__':
   app.run(debug=True)