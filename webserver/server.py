#!/usr/bin/env python2.7

"""
Columbia W4111 Intro to databases
Example webserver

To run locally

    python server.py

Go to http://localhost:8111 in your browser


A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""

import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response, session

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)



# XXX: The Database URI should be in the format of:
#
#     postgresql://USER:PASSWORD@<IP_OF_POSTGRE_SQL_SERVER>/<DB_NAME>
#
# For example, if you had username ewu2493, password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://ewu2493:foobar@<IP_OF_POSTGRE_SQL_SERVER>/postgres"
#
# For your convenience, we already set it to the class database

# Use the DB credentials you received by e-mail
DB_USER = "cy2472"
DB_PASSWORD = "g7cu7643"

DB_SERVER = "w4111.cisxo09blonu.us-east-1.rds.amazonaws.com"

DATABASEURI = "postgresql://"+DB_USER+":"+DB_PASSWORD+"@"+"w4111.cisxo09blonu.us-east-1.rds.amazonaws.com"+"/w4111"


#
# This line creates a database engine that knows how to connect to the URI above
#
engine = create_engine(DATABASEURI)


# Here we create a test table and insert some values in it
engine.execute("""DROP TABLE IF EXISTS test;""")
engine.execute("""CREATE TABLE IF NOT EXISTS test (
  id serial,
  name text
);""")
engine.execute("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace'), ('Boaty McBoatface');""")



@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request

  The variable g is globally accessible
  """
  try:
    g.conn = engine.connect()
  except:
    print ("uh oh, problem connecting to database")
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to e.g., localhost:8111/foobar/ with POST or GET then you could use
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
#
# see for routing: http://flask.pocoo.org/docs/0.10/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route('/')
def redir():
  
  #
  # render_template looks in the templates/ folder for files.
  # for example, the below file reads template/index.html
  #
  return redirect("/login")

#
# This is an example of a different path.  You can see it at
#
#     localhost:8111/another
#
# notice that the functio name is another() rather than index()
# the functions for each app.route needs to have different names
#
@app.route('/another')
def another():
  return render_template("anotherfile.html")

@app.route('/user/<trackAcc>')
def tracking_accounts(trackAcc):
  trackAcc = trackAcc
  context = dict(trackAcc = trackAcc)
  return render_template("tracking_accounts.html", **context)


@app.route('/user', methods =['GET','POST'])
def user():
  """
  request is a special object that Flask provides to access web request information:

  request.method:   "GET" or "POST"
  request.form:     if the browser submitted a form, this contains the data in the form
  request.args:     dictionary of URL arguments e.g., {a:1, b:2} for http://localhost?a=1&b=2

  See its API: http://flask.pocoo.org/docs/0.10/api/#incoming-request-data
  """

  # DEBUG: this is debugging code to see what request looks like
  print (request.args)
  



  if request.method == "POST":
    #session['username'] = request.form['user']
    #username = session['username']
    username = request.form['user']

    #Query to show the user's name
    qName = "SELECT name from users where username = %s;"
    cursor = g.conn.execute(qName, (username,))
    welcomeName = []
    for result in cursor:
      welcomeName.append(result['name'])
    cursor.close()
   
    #Query to show the user's tracking account
    qTrack = "SELECT T.aname as name from tracking_accounts T, users U where U.uid = T.uid and U.username = %s;"
    cursor = g.conn.execute(qTrack, (username,))
    trackAcc = []
    for result in cursor:
        trackAcc.append(result['name'])
    cursor.close()

    #Query to show the user's payment options
    qPay = "SELECT pdo.oname as name from payment_deposit_options pdo, users U where U.uid = pdo.uid and U.username = %s;"
    cursor = g.conn.execute(qPay, (username,))
    payOpt = []
    for result in cursor:
      payOpt.append(result['name'])
    cursor.close()

    qTest = "SELECT * from payment_deposit_options pdo, users U where U.uid = pdo.uid and U.username = %s;"
    cursor = g.conn.execute(qTest, (username,))
    test = []
    cursorKeys = cursor.keys()
    for result in cursor:
      test.append(result)

      #test.append(d)
    cursor.close()


    #
    # Flask uses Jinja templates, which is an extension to HTML where you can
    # pass data to a template and dynamically generate HTML based on the data
    # (you can think of it as simple PHP)
    # documentation: https://realpython.com/blog/python/primer-on-jinja-templating/
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
    context = dict(welcomeName = welcomeName, trackAcc = trackAcc, payOpt = payOpt, cursorKeys = cursorKeys, test = test)







    return render_template("userPage.html", **context)
  return redirect('/')

#@app.route('/user/<username>')
#def 

# Example of adding new data to the database
@app.route('/add', methods=['POST'])
def add():
  name = request.form['name']
  print (name)
  cmd = 'INSERT INTO test(name) VALUES (:name1), (:name2)';
  g.conn.execute(text(cmd), name1 = name, name2 = name);
  return redirect('/')

#TEST A RENDER OF A HTML DOCUMENT
#@app.route('/test')
#def test():
#  return render_template("login.html")

#Login page
@app.route('/login', methods=['GET','POST'])
def login():
  return render_template("login.html")

#404 page
@app.errorhandler(404)
def the_bad_place(error):
  return render_template('404.html')

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
    Run the server using

        python server.py

    Show the help text using

        python server.py --help

    """

    HOST, PORT = host, port
    print ("running on %s:%d" % (HOST, PORT))
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)


  run()
