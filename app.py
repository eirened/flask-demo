from flask import Flask, render_template, request, redirect
import sys
import requests
import datetime
#from bokeh.layouts import gridplot
#from bokeh.plotting import figure, show, output_file
#import pandas as pd

app = Flask(__name__)

@app.route('/')
def main():
    return redirect('/index')

@app.route('/index',methods=['GET','POST'])
def index():
    error = None
    if request.method == 'POST':
        #FIXME to check if at least one checkbox was ticked
        stock_name=request.form['ticker']
        ticked_boxes=request.form.getlist('features')
        #getPlot(stock_name,ticked_boxes)
        getPlot("aapl", ticked_boxes)
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
    #pddata=pd.read_json()
    #columns = list(ticked_boxes)
    #columns.insert(0, 'date')
    #pddata = pd.DataFrame([d[1:] for d in data], [d[0] for d in data], columns=ticked_boxes)

    for d in data:
        sys.stderr.write(str(d)+"\n")

    #for elem in ticked_boxes:
    #   sys.stderr.write(elem+"\n")


if __name__ == '__main__':
  app.run(port=33507,debug=True)