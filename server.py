
"""
Columbia's COMS W4111.001 Introduction to Databases
Example Webserver
To run locally:
    python server.py
Go to http://localhost:8111 in your browser.
A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""
import os
  # accessible as a variable in index.html:
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response, session, flash
from datetime import datetime, date, timedelta
import time
import random

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)
app.config['SECRET_KEY'] = "4111-55"

#
# The following is a dummy URI that does not connect to a valid database. You will need to modify it to connect to your Part 2 database in order to use the data.
#
# XXX: The URI should be in the format of: 
#
#     postgresql://USER:PASSWORD@34.73.36.248/project1
#
# For example, if you had username zy2431 and password 123123, then the following line would be:
#
#     DATABASEURI = "postgresql://zy2431:123123@34.73.36.248/project1"
#
# Modify these with your own credentials you received from TA!
DATABASE_USERNAME = "sh4332"
DATABASE_PASSWRD = "1383"
DATABASE_HOST = "34.148.107.47" # change to 34.28.53.86 if you used database 2 for part 2
DATABASEURI = f"postgresql://{DATABASE_USERNAME}:{DATABASE_PASSWRD}@{DATABASE_HOST}/project1"


#
# This line creates a database engine that knows how to connect to the URI above.
#
engine = create_engine(DATABASEURI)

#
# Example of running queries in your database
# Note that this will probably not work if you already have a table named 'test' in your database, containing meaningful data. This is only an example showing you how to run queries in your database using SQLAlchemy.
#
with engine.connect() as conn:
    create_table_command = """
    CREATE TABLE IF NOT EXISTS test (
        id serial,
        name text
    )
    """
    res = conn.execute(text(create_table_command))
    insert_table_command = """INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace')"""
    res = conn.execute(text(insert_table_command))
    # you need to commit for create, insert, update queries to reflect
    conn.commit()


@app.before_request
def before_request():
    """
    This function is run at the beginning of every web request 
    (every time you enter an address in the web browser).
    We use it to setup a database connection that can be used throughout the request.

    The variable g is globally accessible.
    """
    try:
        g.conn = engine.connect()
    except:
        print("uh oh, problem connecting to database")
        import traceback; traceback.print_exc()
        g.conn = None

@app.teardown_request
def teardown_request(exception):
    """
    At the end of the web request, this makes sure to close the database connection.
    If you don't, the database could run out of memory!
    """
    try:
        g.conn.close()
    except Exception as e:
        pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to, for example, localhost:8111/foobar/ with POST or GET then you could use:
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
# 
# see for routing: https://flask.palletsprojects.com/en/1.1.x/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route('/')
def index():
    """
    request is a special object that Flask provides to access web request information:

    request.method:   "GET" or "POST"
    request.form:     if the browser submitted a form, this contains the data in the form
    request.args:     dictionary of URL arguments, e.g., {a:1, b:2} for http://localhost?a=1&b=2

    See its API: https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data
    """

    # DEBUG: this is debugging code to see what request looks like
    print(request.args)
    #
    # example of a database query
    #
    # select_query = "SELECT name from test"
    # cursor = g.conn.execute(text(select_query))
    # names = []
    # for result in cursor:
    # 	names.append(result[0])
    # cursor.close()
    #
    # Flask uses Jinja templates, which is an extension to HTML where you can
    # pass data to a template and dynamically generate HTML based on the data
    # (you can think of it as simple PHP)
    # documentation: https://realpython.com/primer-on-jinja-templating/
    #
    # You can see an example template in templates/index.html
    #
    # context are the variables that are passed to the template.
    # for example, "data" key in the context variable defined below will be 
    # accessible as a variable in index.html:
    #
    #     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
    #     <div>{{data}}</div>
    #     
    #     # creates a <div> tag for each element in data
    #     # will print: 
    #     #
    #     #   <div>grace hopper</div>
    #     #   <div>alan turing</div>
    #     #   <div>ada lovelace</div>
    #     #
    #     {% for n in data %}
    #     <div>{{n}}</div>
    #     {% endfor %}
    #
    # context = dict(data = names)
    #
    # render_template looks in the templates/ folder for files.
    # for example, the below file reads template/index.html
    #
    return render_template("index.html") #, **context)

#
# This is an example of a different path.  You can see it at:
# 
#     localhost:8111/another
#
# Notice that the function name is another() rather than index()
# The functions for each app.route need to have different names
#
@app.route('/another')
def another():
    return render_template("another.html")


# Example of adding new data to the database
# @app.route('/add', methods=['POST'])
# def add():
# 	# accessing form inputs from user
# 	name = request.form['name']
    
# 	# passing params in for each variable into query
# 	params = {}
# 	params["new_name"] = name
# 	g.conn.execute(text('INSERT INTO test(name) VALUES (:new_name)'), params)
# 	g.conn.commit()
# 	return redirect('/')


'''@app.route('/login')
def login():
    abort(401)
    this_is_never_executed()'''

@app.route('/search', methods=['POST', 'GET'])
def search():
    if request.form.get('reset') != None:
        return redirect('/search')
    
    search_result = []
    off_result = []
    model_result = []
    office = request.form.get('office')
    model = request.form.get('model')
    start = request.form.get('start')
    startHour = request.form.get('startHour')
    endHour = request.form.get('endHour')
    end = request.form.get('end')
    rating = request.form.get('high_rate')
    today = str(date.today())
    hour = str(datetime.now().hour)#.rsplit(":", 1)[0]
    if start == '' or start == None:
        start = today
    if end == '' or end == None:
        end = today
    if startHour == '' or startHour == None:
        startHour = hour
    if endHour == '' or endHour == None:
        endHour = hour
    rated = False
    if rating == '' or rating == None:
        rating = 0
    else:
        rating = float(rating)
        rated = True

    s = 'SELECT DISTINCT office_name FROM office O'
    # if model != 'none' and model != None:
    # 	s += " WHERE EXISTS (SELECT * FROM car C WHERE C.office_name=O.office_name AND C.model='" + model + "')"
    off_cursor = g.conn.execute(text(s))
    for result in off_cursor:
        off_result.append(result[0])
    off_cursor.close()

    s = 'SELECT DISTINCT model FROM car_type CT WHERE CT.rating>=%f' % rating
    if office != 'none' and office != None:
        s += " AND EXISTS (SELECT * FROM car C WHERE C.model=CT.model AND C.office_name='" + office + "')"
    model_cursor = g.conn.execute(text(s))
    for result in model_cursor:
        model_result.append(result[0])
    model_cursor.close()
    
    params = {}
    if request.method=='POST':
        session['start'] = start
        session['end'] = end
        session['startHour'] = startHour
        session['endHour'] = endHour

        s = 'SELECT C.*, brand, function, capacity, unit_time_price, rating FROM car C, car_type CT WHERE C.model=CT.model AND CT.rating>=%f' % rating
        # constraint office
        if office != 'none' and office != None:
            params["office"] = office
            s += " AND C.office_name=(:office)"
        # constraint model
        if model != 'none' and model != None:
            params["model"] = model
            s += " AND C.model=(:model)"
        # constraint start time
        params["start"] = start+" "+startHour+":00"+time.strftime('%z')
        params["end"] = end+" "+endHour+":00"+time.strftime('%z')
        # print(start, end)
        s += " AND NOT EXISTS (SELECT * FROM reservation R WHERE C.car_id=R.car_id AND NOT (R.start_time>(:end) OR R.end_time<(:start)))"
        # s += " LIMIT 12"
        # print(s)

        cursor = g.conn.execute(text(s), params)
        for result in cursor:
            search_result.append(result)
        cursor.close()
        params["start"] = start
        params["end"] = end
    
    context = dict(results=search_result, offices=off_result, models=model_result, today=today, shour=int(startHour), ehour=int(endHour), rated=rated, **params)
    return render_template('search.html', **context)


@app.route('/book/<string:car_id>')
def book(car_id):
    # Code to retrieve car details from the database
    start = session.get('start')
    end = session.get('end')
    startHour = session.get('startHour')
    endHour = session.get('endHour')
    today = str(date.today())
    hour = str(datetime.now().hour)
    if start == None:
        start = today
    if end == None:
        end = today
    if startHour== None:
        startHour = hour
    if endHour == None:
        endHour = hour
    
    cursor = g.conn.execute(text("SELECT unit_time_price FROM car C, car_type CT WHERE C.model=CT.model AND C.car_id='" + car_id + "'"))
    rows = cursor.fetchall()
    cursor.close()
    cost = rows[0][0]*(1+(datetime.strptime(end, '%Y-%m-%d') - datetime.strptime(start, '%Y-%m-%d')).days)
    
    cursor = g.conn.execute(text("SELECT car_id, C.model, brand, capacity, mileage, color, function, unit_time_price, office_name FROM car C, car_type CT WHERE C.model=CT.model AND C.car_id='" + car_id + "'"))
    rows = cursor.fetchall()
    cursor.close()

    return render_template('book.html', car=rows[0], start=start, end=end, shour=int(startHour), ehour=int(endHour), cost=cost)


@app.route('/bookConfirmed/<string:car_id>', methods=['POST'])
def book_confirm(car_id):
    user_id = session.get('user_id')
    if user_id == None:
        return redirect('/login')
    start = request.form.get('start')
    end = request.form.get('end')
    startHour = request.form.get('startHour')
    endHour = request.form.get('endHour')
    cost = request.form.get('cost')
    if len(startHour) == 1:
        startHour = '0' + startHour
    if len(endHour) == 1:
        endHour = '0' + endHour

    params = {}
    time_split = start.split("-")
    params["start"] = start+" "+startHour+":00"+time.strftime('%z')
    params["end"] = end+" "+endHour+":00"+time.strftime('%z')
    params["car_id"] = car_id

    cursor = g.conn.execute(text("SELECT count(*) FROM reservation R WHERE R.car_id=(:car_id) AND NOT (R.start_time>(:end) OR R.end_time<(:start))"), params)
    rows = cursor.fetchall()
    cursor.close()
    print("rows[][]", rows[0][0])
    if rows[0][0] > 0:
        return render_template('error.html', message="That car is already booked for that period. Please search again for other cars.")

    params["car_id"] = car_id
    params["user_id"] = "Z9JH1D5" # for test

    id_start = time_split[0][-2:] + time_split[1]+"0000"
    id_end = time_split[0][-2:] + time_split[1]+"9999"
    cursor = g.conn.execute(text("SELECT reserve_id FROM reservation R WHERE reserve_id BETWEEN '" + id_start + "' AND '" + id_end + "' ORDER BY reserve_id DESC"))
    rows = cursor.fetchall()
    cursor.close()
    if len(rows) == 0:
        params["id"] = id_start
    else:
        params["id"] = str(int(rows[-1][0])+1)
    if params["id"][:4] != id_start[:4]:
        return render_template('error.html', message="Reservation id overflow for that month!")

    if cost == None or cost == '':
        cursor = g.conn.execute(text("SELECT unit_time_price FROM car C, car_type CT WHERE C.model=CT.model AND C.car_id='" + car_id + "'"))
        rows = cursor.fetchall()
        cursor.close()
        params["cost"] = rows[0][0]*(1+(datetime.strptime(end, '%Y-%m-%d') - datetime.strptime(start, '%Y-%m-%d')).days)
    else:
        params["cost"] = cost

    insert_table_command = """INSERT INTO reservation VALUES ((:id), (:start), (:end), (:cost), (:car_id), (:user_id))"""
    g.conn.execute(text(insert_table_command), params)
    g.conn.commit()
    return redirect('/')


#Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        if not all([email, password]):
            flash('Incomplete parameters')

        cursor = g.conn.execute(text("SELECT email, password FROM user Where users.email='email' AND users.password='password'"))

        if cursor:
            return 'Login successful!'

        else:
            return redirect('/login')

        cursor.close()
    return render_template('reservation.html', email = email)


#Signup
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        password2 = request.form.get('password2')

        # check if the email has been registered
        email_db = g.conn.execute(text('SELECT email FROM customer WHERE customer.email="email"'))
        if email_db:
            flash('This email has already been registered.')
        if not all([email, password, password2]):
            flash('Incomplete parameters')
        if password != password2:
            flash('The password entered twice is not the same, please re-enter it.')
        else:
            ID_1 = random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
            ID_2 = str(random.randint(0,9))          
            ID_3 = random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
            ID_4 = random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
            ID_5 = str(random.randint(0,9))
            ID_6 = random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
            ID_7 = str(random.randint(0,9))

            new_ID = ID_1 + ID_2 + ID_3 + ID_4 + ID_5 + ID_6 + ID_7

            #Change DB, lack of user name

            insert_table_command = """INSERT INTO customer(email, password, user_id) VALUES ('email','password2','new_ID')"""
            res = conn.execute(text(insert_table_command))

            g.conn.commit()
            return redirect('/login')

    return render_template('signup.html')


#onlineserver
@app.route('/onlineserver/<string:username>')
def onlineserver(username):
    #To match a online server for the user.
    cursor = g.conn.execute(text('SELECT name FROM online_customer_service'))
    r = cursor.fetchall()
    server_1 = r[random.randint(0,9)]
    cursor.close()

    return render_template('signup.html', server_1 = server_1 )








if __name__ == "__main__":
    import click

    @click.command()
    @click.option('--debug', is_flag=True)
    @click.option('--threaded', is_flag=True)
    @click.argument('HOST', default='0.0.0.0')
    @click.argument('PORT', default=8111, type=int)
    def run(debug, threaded, host, port):
        """
        This function handles command line parameters.
        Run the server using:

            python server.py

        Show the help text using:

            python server.py --help

        """

        HOST, PORT = host, port
        print("running on %s:%d" % (HOST, PORT))
        app.run(host=HOST, port=PORT, debug=True, threaded=threaded)

run()


