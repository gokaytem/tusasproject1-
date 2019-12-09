from flask import Flask
from flask import render_template
from flask import request, redirect, url_for

import psycopg2 as dbapi2

app=Flask(__name__)

INIT_STATEMENTS = [
   '''CREATE TABLE IF NOT EXISTS conditions (
        time        TIMESTAMPTZ       NOT NULL,
        location    TEXT              NOT NULL,
        temperature DOUBLE PRECISION  NULL,
        humidity    DOUBLE PRECISION  NULL
      );''']

def initialize(url):
    with dbapi2.connect(url) as connection:
        cursor = connection.cursor()
        for statement in INIT_STATEMENTS:
            cursor.execute(statement)
        
        cursor.close()
        
def query(url):
    with dbapi2.connect(url) as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM conditions")
        rows = cursor.fetchall()      
        cursor.close()
        return rows

@app.route("/")
def home_page():
    return render_template("home.html")
    
@app.route("/conditions")
def conditions_page():
    rows = query("postgres://postgres:1423@localhost:5432/tutorial")
    return render_template("conditions.html", rows=sorted(rows), len=len(rows))
    
@app.route("/conditions_add", methods=["GET", "POST"])
def conditions_add_page():
    if request.method == "GET":
        return render_template(
            "conditions_add.html"
        )
    else:
        form_time = "NOW()"
        form_location = request.form["location"]
        form_temperature = request.form["temperature"]
        form_humidity = request.form["humidity"]
        
        STATEMENTS = [ '''
                      INSERT INTO conditions VALUES
                          (%s, '%s', %s, %s); ''' % (form_time, form_location, form_temperature, form_humidity)  ]
        
        url= "postgres://postgres:1423@localhost:5432/tutorial"
        with dbapi2.connect(url) as connection:
            cursor = connection.cursor()
            for statement in STATEMENTS:
                cursor.execute(statement)
        
            cursor.close()
        
        return redirect(url_for("conditions_page"))

if __name__ == "__main__":
    
    # DATABASE_URL="postgres://postgres:1423@localhost:5432/tutorial"
    
    # initialize(DATABASE_URL)
    
    app.run()