from flask import Flask, render_template, request, redirect
import sys
import requests
import datetime
from bokeh.layouts import gridplot
from bokeh.models import DatetimeTicker,DaysTicker
from bokeh.plotting import figure, show, output_file
from bokeh.embed import components
import pandas as pd
from math import pi,ceil

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
        if len(ticked_boxes)==0:
            error="Please select at least one feature to be displayed."
            return render_template('index.html',error=error)
        #getPlot(stock_name,ticked_boxes)
        #check if stock ticker exists
        today = datetime.date.today()
        first = today.replace(day=1)
        lastMonthEnd = first - datetime.timedelta(days=1)
        lastMonthStart = lastMonthEnd.replace(day=1)
        sys.stderr.write(','.join(map(str, ticked_boxes)))
        r = requests.get(
            "https://www.quandl.com/api/v3/datatables/WIKI/PRICES.json?ticker=%s&date.gte=%s&date.lte=%s&qopts.columns=date,%s&api_key=yFrECJyVKjZh4z--h7xq" % (
            stock_name, lastMonthStart.strftime("%y%m%d"), lastMonthEnd.strftime("%y%m%d"),
            ','.join(map(str, ticked_boxes))))
        data = r.json()['datatable']['data']
        sys.stderr.write("DATA"+str(data))
        if len(data)==0:
            return render_template('index.html',error='Stock data for the given dates not found. Please check the spelling of the stock ticker. If it is correct, it means no data exists for the past month.')
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
    p = figure(x_axis_type="datetime", tools=TOOLS, plot_width=1000, title=stock_name + " Prices")

    p.xaxis.major_label_orientation = pi / 4
    p.xaxis.axis_label = "Date (month/day)"
    p.xaxis.axis_label_text_font_size = "14pt"
    p.xaxis.major_label_text_font = "12pt"
    p.yaxis.axis_label = "Stock Price (USD)"
    p.yaxis.axis_label_text_font_size = "14pt"
    p.yaxis.major_label_text_font = "12pt"

    if all(feature in ["low","high","close","open"] for feature in ticked_boxes) and len(ticked_boxes)==4:
        #candlestick plot
        mids = (pddata.open + pddata.close) / 2
        spans = abs(pddata.close - pddata.open)

        inc = pddata.close > pddata.open
        dec = pddata.open > pddata.close
        w = 12 * 60 * 60 * 1000  # half day in ms

        #p = figure(x_axis_type="datetime", plot_width=800, plot_height=500, title=" Candlestick")
        #p.xaxis.major_label_orientation = pi / 4
        p.grid.grid_line_alpha = 0.3

        p.segment(pddata.index, pddata.high, pddata.index, pddata.low, color='black')
        p.rect(pddata.index[inc], mids[inc], w, spans[inc], fill_color="#D5E1DD", line_color="black")
        p.rect(pddata.index[dec], mids[dec], w, spans[dec], fill_color="#F2583E", line_color="black")

        script, div = components(p)
        return (div, script)



    p.xaxis.ticker = DatetimeTicker(desired_num_ticks=6)
    #p.xaxis[0].ticker=DaysTicker(interval=3)
    colors=['blue','red','purple','black','green','orange']
    legend={'close':'Closing','open':'Opening','adj_open':'Adjusted Opening','adj_close':'Adjusted Closing','low':'Lowest','high':'Highest'}
    for index,feature in enumerate(ticked_boxes):
        p.line(pddata.index, pddata[feature], line_color=colors[index],line_width=2,legend=legend[feature])
        p.circle(pddata.index, pddata[feature], line_color=colors[index],fill_color=colors[index],size=5)
    script, div=components(p)
    return (div,script)

if __name__ == '__main__':
  app.run(port=33507,debug=True)