import pyupbit
import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import time

# UI 파일 불러오기

form_class = uic.loadUiType("golden.ui")[0]
tickers = pyupbit.get_tickers(fiat="KRW")
print(tickers)


class Worker(QThread):
    finished = pyqtSignal(dict)

    def run(self):
        while True:
            data = {}

            for ticker in tickers:
                data[ticker] = self.get_market_infos(ticker)

            self.finished.emit(data)
            self.msleep(50)

    def get_market_infos(self, ticker):
        try:

            df = pyupbit.get_ohlcv(ticker, interval="day")

            price = pyupbit.get_current_price(ticker)
            ma20 = df['close'].rolling(window=20).mean().iloc[-1]
            ma60 = df['close'].rolling(window=60).mean().iloc[-1]
            volume = df.iloc[-1]['volume']

            state = None
            if ma20 > ma60:
                state = "Golden Cross"
            else:
                state = "Dead Cross"

            return (price, volume, ma20, ma60, state)
        except:
            return None


class MyWindow(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.worker = Worker()
        self.worker.start()
        self.worker.finished.connect(self.update_table_widget)

    @pyqtSlot(dict)
    def update_table_widget(self, data):
        for ticker, info in data.items():
            try:
                index = tickers.index(ticker)
                self.tableWidget.setItem(index, 0, QTableWidgetItem(ticker))

                self.tableWidget.setItem(index, 1, QTableWidgetItem(str(info[0])))
                self.tableWidget.setItem(index, 2, QTableWidgetItem(str(info[1])))
                self.tableWidget.setItem(index, 3, QTableWidgetItem(str(info[2])))
                self.tableWidget.setItem(index, 4, QTableWidgetItem(str(info[3])))
                item = QTableWidgetItem(str(info[4]))

                self.tableWidget.setItem(index, 5, item)



            except:
                pass


app = QApplication(sys.argv)
win = MyWindow()
win.show()
app.exec_()
