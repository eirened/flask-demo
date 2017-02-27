from flask import Flask, render_template, request, redirect
import sys
import requests
import datetime
from bokeh.layouts import gridplot
from bokeh.plotting import figure, show, output_file
from bokeh.embed import components
import pandas as pd
from math import pi

app = Flask(__name__)

@app.route('/')
def main():
    return redirect('/index')

@app.route('/index',methods=['GET','POST'])
def index():
    error = None
    if request.method == 'POST':
        #FIXME to check if at least one checkbox was ticked
        stock_name=request.form['ticker'].upper()
        ticked_boxes=request.form.getlist('features')
        #getPlot(stock_name,ticked_boxes)
        (div,script)=getPlot(stock_name, ticked_boxes)
        return render_template('graph.html',stock_name=stock_name,div=div,script=script)
        #else:
        #error = 'Invalid username/password'
    # the code below is executed if the request method
    # was GET or the credentials were invalid
    #return render_template('login.html', error=error)

    return render_template('index.html')



def getPlot(stock_name,ticked_boxes):
    #lookup stock name; if not found, go to error page
    #presume previous calendar month
    today = datetime.date.today()
    first = today.replace(day=1)
    lastMonthEnd = first - datetime.timedelta(days=1)
    lastMonthStart = lastMonthEnd.replace(day=1)
    sys.stderr.write(','.join(map(str,ticked_boxes)))
    r=requests.get("https://www.quandl.com/api/v3/datatables/WIKI/PRICES.json?ticker=%s&date.gte=%s&date.lte=%s&qopts.columns=date,%s&api_key=yFrECJyVKjZh4z--h7xq"%(stock_name,lastMonthStart.strftime("%y%m%d"),lastMonthEnd.strftime("%y%m%d"),','.join(map(str,ticked_boxes))))
    data=r.json()['datatable']['data']

    columns = list(ticked_boxes)
    columns.insert(0, 'date')
    pddata = pd.DataFrame([d[1:] for d in data], [pd.to_datetime(d[0]) for d in data], columns=ticked_boxes)

    TOOLS = "pan,wheel_zoom,box_zoom,reset,save"
    p = figure(x_axis_type="datetime", tools=TOOLS, plot_width=1000, title=stock_name + " values")
    p.xaxis.major_label_orientation = pi / 4
    p.xaxis.axis_label = "Date"
    p.yaxis.axis_label = "Opening stock price"

    p.line(pddata.index, pddata.open, color="#D5E1DD", line_color="darkblue")
    script, div=components(p)
    return (div,script)

if __name__ == '__main__':
  app.run(port=33507,debug=True)