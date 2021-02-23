#!/usr/bin/env python
# Display a runtext with double-buffering.
from samplebase import SampleBase
from rgbmatrix import graphics
import time
import datetime
import multiprocessing
from threading import Thread
# import stock_info module from yahoo_fin
from yahoo_fin import stock_info as si
from yahoo_fin.stock_info import get_data
import pandas as pd
#today = date.today()

# stocks = ['C']

def getTickerData(stocks):

    tickerData = {}


    for c in stocks:
        #td[c]=si.get_quote_table(c, dict_result=False)
        price = si.get_quote_table(c)["Quote Price"]
        pc = si.get_quote_table(c)["Previous Close"]
        pct_ch = "%.2f" % ((price / pc - 1) * 100) + '%'
        tickerData[c] = {'price': "{:.0f}".format(price), 'pct_ch': pct_ch}
       


    return tickerData



class RunText(SampleBase):
    def __init__(self, *args, **kwargs):
        super(RunText, self).__init__(*args, **kwargs)
        self.parser.add_argument("-t", "--text", help="The text to scroll on the RGB LED panel", default="Hello world!")

        self.stockData = {}
        # Place your stocks here
        self.stocks = ['SNOW', '^GSPC', '^DJI', '^IXIC']
        self.blueColor = graphics.Color(4, 66, 165)
        self.greenColor = graphics.Color(0, 168, 36)
        self.redColor = graphics.Color(153, 6, 1)



    def updatestockData(self, i):
        data = getTickerData(self.stocks)
        self.stockData = data
        print ("Stock Data Updated", self.stockData)


    def run(self):
        print("Run")
        self.stockData = getTickerData(self.stocks)


        # To turn off when sleeping

        start_time = datetime.time(hour=7)
        end_time = datetime.time(hour=22, minute=30)
        now = (datetime.datetime.now() - datetime.timedelta(hours=8)).time()

        while start_time < now < end_time:
            print("Started")
            offscreen_canvas = self.matrix.CreateFrameCanvas()
            font = graphics.Font()
            font.LoadFont("fonts/7x13B.bdf")
            textColor = graphics.Color(255, 255, 0)
            pos = offscreen_canvas.width

            for x, c in enumerate(self.stockData):
                # Towards end of ticker tape, begin creating new tape async
                if x == (len(self.stockData) - 2):
                    p = Thread(target=self.updatestockData, args=(1,))
                    p.start()

                pct_ch = self.stockData[c]['pct_ch']
                # makes pct_ch green if positive return
                if float(pct_ch[:-1]) > 0:
                    color = self.greenColor
                else:
                    color = self.redColor

                while True:
                    offscreen_canvas.Clear()
                    # Draw ticker (on what, font, where, size, color, say what)
                    # Draw ticker, price, pct_ch placing each after the last position. ex. pos + ticker + 5 + price + 5
                    ticker = graphics.DrawText(offscreen_canvas, font, pos, 12, textColor, c)
                    price = graphics.DrawText(offscreen_canvas, font, pos + ticker + 5, 12, self.blueColor, str(self.stockData[c]['price']))
                    pct_ch_len = graphics.DrawText(offscreen_canvas, font, pos + price + 5 + ticker + 5, 12, color, str(pct_ch))
                    # Slide text one position to the left
                    pos -= 1

                    # If ticker tape reaches end, clear and start over
                    if (pos + ticker + price + pct_ch_len < 0):
                        pos = offscreen_canvas.width
                        offscreen_canvas.Clear()

                        # self.stockData = self.return_dict['data']
                        break

                    # This adjusts speed of ticker tape
                    time.sleep(0.05)
                    offscreen_canvas = self.matrix.SwapOnVSync(offscreen_canvas)

# Main function
if __name__ == "__main__":
    run_text = RunText()
    if (not run_text.process()):
        run_text.print_help()