from flask import Flask
from flask import render_template
from flask import request, redirect, url_for

import os
import sys
import psycopg2 as dbapi2

app=Flask(__name__)

#DATABASE_URL = os.environ['DATABASE_URL']
DATABASE_URL = "postgres://yhhyfzzbazeqdp:e01c510431281ed149e9aaede179c6a8f02317a6148695c8779bf911d4c8fb9f@ec2-174-129-255-10.compute-1.amazonaws.com:5432/d5esp0qjvi5ic3"

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
        
def query(url, scale):
    if scale=="all":
        with dbapi2.connect(url) as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM conditions")
            rows = cursor.fetchall()      
            cursor.close()
            return rows
    elif scale=="daily":
        with dbapi2.connect(url) as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM conditions WHERE time >= CURRENT_DATE ")
            rows = cursor.fetchall()      
            cursor.close()
            return rows
    elif scale=="hourly":
        with dbapi2.connect(url) as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM conditions WHERE time >= date_trunc('hour', current_timestamp) ")
            rows = cursor.fetchall()      
            cursor.close()
            return rows
        
@app.route("/")
def home_page():
    return render_template("home.html")
    
@app.route("/conditions")
def conditions_page():
    #url="postgres://yhhyfzzbazeqdp:e01c510431281ed149e9aaede179c6a8f02317a6148695c8779bf911d4c8fb9f@ec2-174-129-255-10.compute-1.amazonaws.com:5432/d5esp0qjvi5ic3"
    rows = query(DATABASE_URL, "all")
    
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
        
        with dbapi2.connect(DATABASE_URL, sslmode='require') as connection:
            cursor = connection.cursor()
            for statement in STATEMENTS:
                cursor.execute(statement)
        
            cursor.close()
        
        return redirect(url_for("conditions_page"))
        
@app.route("/conditions_add_<int:temperature>_<int:humidity>", methods=["GET", "POST"])
def conditions_add_direct_page(temperature, humidity):
    form_time = "NOW()"
    form_location = "ertan"
    form_temperature = temperature
    form_humidity = humidity
    
    STATEMENTS = [ '''
                  INSERT INTO conditions VALUES
                      (%s, '%s', %s, %s); ''' % (form_time, form_location, form_temperature, form_humidity)  ]
    
    with dbapi2.connect(DATABASE_URL, sslmode='require') as connection:
        cursor = connection.cursor()
        for statement in STATEMENTS:
            cursor.execute(statement)
    
        cursor.close()
    
    return redirect(url_for("conditions_page"))
        
@app.route("/conditions_remove_<string:time>", methods=["GET", "POST"])
def conditions_remove(time):
        STATEMENTS = ['''
                         DELETE FROM conditions
                            WHERE (time='%s'); ''' % (time)]

        url= DATABASE_URL
        with dbapi2.connect(url) as connection:
            cursor = connection.cursor()
            for statement in STATEMENTS:
                cursor.execute(statement)

            cursor.close()

        return redirect(url_for("conditions_page"))
 
@app.route('/conditions_plot_<string:attribute>_<string:scale>')
def conditions_plot_page(attribute, scale):
    data = query(DATABASE_URL, scale)
    x=[]
    y=[]
    z=[]
    together=0
    if attribute=='temperature':
        attribute_i=2
    elif attribute=='humidity':
        attribute_i=3
    elif attribute=='together':
        together=1
        attribute_i1=2
        attribute_i2=3
        for i in range(0,len(data)):
            x.append(data[i][0])
            y.append(data[i][attribute_i1])
            z.append(data[i][attribute_i2])
            
        return render_template("conditions_plot.html", x=x, y=y, z=z, together=together, len_data=len(data), attribute=attribute, scale=scale)
        
    for i in range(0,len(data)):
        x.append(data[i][0])
        y.append(data[i][attribute_i])
    
    return render_template("conditions_plot.html", x=x, y=y, z=z, together=together, len_data=len(data), attribute=attribute, scale=scale)

if __name__ == "__main__":
    app.config["DEBUG"] = True
    app.run()