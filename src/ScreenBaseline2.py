import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from pulse.pulsesensor import Pulsesensor
from grove.grove_gsr_sensor import GroveGSRSensor
from ScreenTask11 import *
from ScreenTask12 import *
from ScreenTask21 import *
from ScreenTask22 import *
from ScreenTask31 import *
from ScreenTask32 import *
import time as t
import csv
import random

class ScreenBaseline2(QMainWindow):
    def __init__(self, name, identifier):
        super().__init__()
        self.name = name
        self.identifier = identifier
        self.initUI()
        print(self.gsr_sensor.GSR_list)
        self.tasks = ["ScreenTask11", "ScreenTask12", "ScreenTask21", "ScreenTask22", "ScreenTask31", "ScreenTask32"]
        self.nr = "00"
    
    def initUI(self):
        self.setWindowTitle("PsyMex-2 Pilot Studie Baseline")
        self.i = 0
        
        # Labels
        self.label_info_1 = QLabel("+")
        self.label_info_1.setStyleSheet('''
        QLabel {font: bold 50px; color: white}
        ''')
        self.label_info_1.setAlignment(Qt.AlignCenter)
        
        self.label_info_2 = QLabel("Baseline Messung erfolgreich")
        self.label_info_2.setStyleSheet('''
        QLabel {font: bold 50px; color: white}
        ''')
        self.label_info_2.setAlignment(Qt.AlignCenter)
        
        # Next button
        self.next_button = QPushButton("Weiter")
        self.next_button.setStyleSheet('''
        QPushButton {margin: 20 200 50 200}
        ''')
        self.next_button.clicked.connect(self.next_page)
        
        # Layout
        self.grid = QGridLayout()
        # Left/Right/Bottom layout just used for relative size of central box
        
        # Central box where the content is stored
        self.grid.addWidget(self.label_info_1,0,1,1,3)
        
        # Central Widget
        widget = QWidget()
        widget.setLayout(self.grid)
        widget.setStyleSheet('''
        QWidget {background-color: #1c1c1c}
        ''')
        self.setCentralWidget(widget)
        self.start_measurement()
        self.showMaximized()
    
    def next_page(self):
        '''
        pic a random class name from the self.tasks list, remove it from the list then instanciate it
        '''
        i = random.randint(0, len(self.tasks) - 1)
        c = globals()[self.tasks[i]]
        del self.tasks[i]
        self.instance = c(self.name, self.identifier, self.tasks)
        self.close()        
        
    def start_measurement(self):
        '''
        starting the sensors and a QTimer which calls the timer function every second
        '''
        self.gsr_sensor = GroveGSRSensor()
        self.gsr_sensor.startAsyncGSR()
        self.gsr_x = [0]
        self.gsr_y = [0]
        self.pulse_sensor = Pulsesensor()
        self.pulse_sensor.startAsyncBPM()
        self.qt = QTimer()
        self.qt.timeout.connect(self.timer)
        self.qt.start(1000)
        return
    
    def timer(self):
        '''
        Wait for 30 seconds then save the sensor list to csv file
        '''
        self.i += 1
        if len(self.gsr_sensor.GSR_list) > 1:
            if self.gsr_y[-1] != self.gsr_sensor.GSR_list[-1][0]:
                y = self.gsr_sensor.GSR_list[-1][0] * 10**6
                self.gsr_y.append(y)
                self.gsr_x.append(self.gsr_sensor.GSR_list[-1][1])
        if self.i == 30:
            print("saving to " + "results/" + self.identifier + self.nr)
            with open("results/" + self.identifier + self.nr + "1", 'w', newline='') as myfile:
                tmp = []
                for i in range(len(self.gsr_y)):
                    tmp.append([self.gsr_y[i], self.gsr_x[i]])
                wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
                #wr.writerows(self.gsr_sensor.GSR_list)
                wr.writerows(tmp)
            with open("results/" + self.identifier + self.nr + "0", 'w', newline='') as myfile:
                wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
                #wr.writerows(self.pulse_sensor.BPM_list)
                wr.writerows(self.gsr_sensor.GSR_list)
            self.gsr_sensor.stopAsyncGSR()
            self.pulse_sensor.stopAsyncBPM()
            self.qt.stop()
            self.label_info_1.setParent(None)
            self.grid.addWidget(self.label_info_2,0,1,1,1)
            self.grid.addWidget(self.next_button,1,1,1,1)
            self.grid.addWidget(QWidget(),1,0,1,1)
            self.grid.addWidget(QWidget(),1,2,1,1)
            return

def main():
    app = QApplication(sys.argv)
    info = ScreenBaseline2("Max Mustermann", "123897")
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
