from flask import Flask, render_template, request, make_response, session, redirect, url_for, flash
from dotenv import dotenv_values
import os, psycopg2
app = Flask(__name__)
app.secret_key = "Vinay"

config = dotenv_values(".env")      # config = {"USER": "foo", "EMAIL": "foo@example.org"}

conn = psycopg2.connect(
   host=config["HOST"],
   database=config["DATABASE"],
   user=config["USER"],
   password=config["PASSWORD"]
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
   #    # print(request.form["source"], request.form["destination"], request.form["date"], request.form["class"])
   #    if 'train' in session:
   #       return redirect(url_for("trains"))
   return render_template("index.html", username = uname, islogged = islogged)


@app.route('/login', methods = ['GET', 'POST'])
def login():
   error = None
   print("ses", session)
   if request.method == 'POST':

      cur.execute("select * from checklogin('{}', '{}')".format(request.form['username'], request.form['password']))
      status = cur.fetchone()
      
      if status[0] == 0:
         session['username'] = request.form['username']
         session['password'] = request.form['password']
         flash("You were successfully logged in!")
         updateLoginStatus()
         if 'train_info' in session:
            cp_train_info = session['train_info']
            print(session['train_info'])
            session.pop('train_info', None)
            # return render_template('trains.html', trains = cp_train_info["train_no"], islogged = islogged, source = cp_train_info["source"], destination = cp_train_info["destination"], date = cp_train_info["date"], tr_class = cp_train_info["class"])
            return redirect(url_for('trains'))

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
         cur.execute("insert into user_table (name, username, password) values('{}', '{}', '{}')".format(request.form['name'], request.form['username'], request.form['password']))
         
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
         cur.execute("select * from train_class")
         classes = cur.fetchall()
         print(classes)
         cur.execute("select * from availableRoute('{}', '{}', '{}', '{}')".format( request.form['date'], request.form['source'], request.form['destination'],request.form['class']))
         data = cur.fetchall()
         print(data)
         for d in data:
            td = [d[0], d[1], d[2], d[3], d[4], [(request.form['class'], d[5], d[6])]]

            for c in classes:
               if c[0] != request.form['class']:
                  cur.execute("select * from calc_fare({}, '{}', '{}', '{}')".format(td[0], c[0], td[1], td[3]))
                  fare = cur.fetchone()
                  cur.execute("select * from countavailableseats({}, '{}', '{}', '{}', '{}')".format(td[0], request.form['date'], td[1], td[3], c[0]))
                  seats = cur.fetchone()
                  td[5].append((c[0], fare[0], seats[0]))
            trains.append(td)

         print(trains)

         if(len(trains) == 0):
            flash("No trains found!")
         
      except Exception as err:
         flash("Something went wrong, Error : ", err)
      return render_template('trains.html', trains = trains, islogged = islogged, source = request.form['source'], destination = request.form['destination'], date = request.form['date'], tr_class = request.form['class'])
   return render_template('trains.html', trains = trains, islogged = islogged)


@app.route('/passenger', methods = ['GET', 'POST'])
def passenger():
   if request.method == 'POST':
      print("sele", request.form)
      sel_info = request.form['class_select'].strip('][').split(', ')
      sel_class = sel_info[0]
      sel_fare = sel_info[1]
      sel_seat = sel_info[2]

      train_info = {"train_no": request.form['train_no'], "date": request.form['date'], "source": request.form['source'], "destination": request.form['destination'], "class": sel_class, "fare": sel_fare, "max_pax": sel_seat}
      if 'username' not in session:
         flash("You need to login first!")
         session['train_info'] = train_info
         return redirect(url_for('login'))

   return render_template("passenger.html", islogged = islogged, train_info = train_info)


@app.route('/book', methods = ['GET', 'POST'])
def book():
   if request.method == 'POST':
      try:
         booking_info = request.form
         print ("hello")
         print (request.form)
         string = request.form['train_info'].replace("\"", "")
         Dict = eval(string)
         print(Dict)
         print (type(Dict))
         print(Dict['class'], Dict['source'])
         cur.execute("select user_id from user_table where user_table.username = '{}'".format( session['username']))
         user_id = cur.fetchone()[0]
         print (user_id)
         data = cur.execute("select create_ticket({},{},'{}','{}','{}',{},'{}','{}','{}')".format( user_id, Dict['train_no'], Dict['source'], Dict['destination'],request.form['name-1'], request.form['age-1'], request.form['sex-1'], Dict['class'], Dict['date']))
         data = cur.fetchall()
         print(data)
         conn.commit()
      except Exception as err:
         flash("Something went wrong, Error : ", err)
      return render_template("book.html", islogged = islogged, booking_info = booking_info)


@app.route('/tickets', methods = ['GET', 'POST'])
def tickets():
   if request.method == 'POST':
      print("should do nothing for now")
      return redirect(url_for('index'))
   else:
      if('username' not in session):
         flash("You need to login first!")
         return redirect(url_for('login'))
      else:
         cur.execute('''select * from ticket
                        where ticket_id in (
                           select ticket_id from book
                           where pass_id in (
                              select pass_id from user_passenger
                              where user_id in (
                                 select user_id from user_table
                                 where username = '{}')));'''.format(session['username']))
         tickets = cur.fetchall()
         print(tickets)
         return render_template("tickets.html", islogged = islogged, tickets = tickets)


@app.route('/cancel', methods = ['POST'])
def cancel():
   if request.method == 'POST':
      print("hello1")
      print(request.form['ticket_id'])
      print(type(request.form['ticket_id']))
      print("hello2")
      try:
         tid = int(request.form['ticket_id'])
         print ("inside try")
         print (tid, type(tid))
         print(session)

         sql = '''call deleteTicket(86);'''
         cur.execute(sql)
         results = cur.fetchall()
         print (results)
         conn.commit()

         flash("Ticket cancelled successfully!")
      except Exception as err:
         flash("Something went wrong, Error : ", err)
   else:
      print ("hi hello")
   return redirect(url_for('tickets'))

if __name__ == '__main__':
   app.run(debug=True)