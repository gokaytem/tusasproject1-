from flask import Flask
from flask import render_template
from flask import request, redirect, url_for

import os
import sys
import psycopg2 as dbapi2

import numpy as np
import matplotlib
import random
from threading import Lock
lock = Lock()
import mpld3
from mpld3 import plugins
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.ioff()

app=Flask(__name__)

DATABASE_URL = os.environ['DATABASE_URL']

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
        
def draw_fig(fig_type,x,y):
    """Returns html equivalent of matplotlib figure
    Parameters
    ----------
    fig_type: string, type of figure
            one of following:
                    * line
                    * bar
    Returns
    --------
    d3 representation of figure
    """
    #x=np.arange(0,4)
    pie_fracs = [20, 30, 40, 10]
    pie_labels = ["A", "B", "C", "D"]
    
    with lock:
        fig, ax = plt.subplots()
        if fig_type == "line":
            ax.plot(x, y)
        elif fig_type == "bar":
            ax.bar(x, y)
        elif fig_type == "pie":
            ax.pie(pie_fracs, labels=pie_labels)
        elif fig_type == "scatter":
            ax.scatter(x, y)
        elif fig_type == "hist":
            ax.hist(y, 10, normed=1)
        elif fig_type == "area":
            ax.plot(x, y)
            ax.fill_between(x, 0, y, alpha=0.2)

    return mpld3.fig_to_html(fig,template_type='simple')

@app.route("/")
def home_page():
    return render_template("home.html")
    
@app.route("/conditions")
def conditions_page():
    #url="postgres://yhhyfzzbazeqdp:e01c510431281ed149e9aaede179c6a8f02317a6148695c8779bf911d4c8fb9f@ec2-174-129-255-10.compute-1.amazonaws.com:5432/d5esp0qjvi5ic3"
    rows = query(DATABASE_URL)
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
        
        #url="postgres://yhhyfzzbazeqdp:e01c510431281ed149e9aaede179c6a8f02317a6148695c8779bf911d4c8fb9f@ec2-174-129-255-10.compute-1.amazonaws.com:5432/d5esp0qjvi5ic3"
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
 
@app.route('/conditions_plot')
def conditions_plot_page():
    data = query(DATABASE_URL)
    x=[]
    y=[]
    for i in range(0,len(data)):
        x.append(data[i][0])
        y.append(data[i][2])
    
    return draw_fig("line",x,y)

if __name__ == "__main__":
    
    # url = os.getenv("DATABASE_URL")
    # if url is None:
        # print("Usage: DATABASE_URL=url python dbinit.py", file=sys.stderr)
        # sys.exit(1)
    
    app.run()