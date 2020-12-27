#Checks if modbus communication works through python
from pymodbus.client.sync import ModbusTcpClient as ModbusClient
import xml.etree.ElementTree as ET
import tkinter, os
from tkinter import ttk, filedialog, messagebox, OptionMenu, Text

class reader:
    def __init__(self, master):

        self.master = master
        master.title('Modbus TCP client')
        master.geometry('600x600')

        #create window
        tkinter.Grid.rowconfigure(self.master, 0, weight=1)
        tkinter.Grid.rowconfigure(self.master, 1, weight=0)
        tkinter.Grid.rowconfigure(self.master, 2, weight=0)
        tkinter.Grid.columnconfigure(self.master, 0, weight=1)
        tkinter.Grid.columnconfigure(self.master, 1, weight=1)
        tkinter.Grid.columnconfigure(self.master, 2, weight=1)
        tkinter.Grid.columnconfigure(self.master, 3, weight=1)
        tkinter.Grid.columnconfigure(self.master, 4, weight=0)

        #Create scrollbar
        self.scrollbar = tkinter.Scrollbar(self.master)
        self.scrollbar.grid(row=0, column=4, sticky='NSE')

        #Create the register view
        test = ''
        for i in range(100):
            test += (str(i) + ' Description ' + str(i*10))

        self.registerData = tkinter.StringVar(value=test)
        self.regDataListBox = tkinter.Listbox(self.master, yscrollcommand=self.scrollbar.set, listvariable=self.registerData)
        self.regDataListBox.grid(row=0, column=0, columnspan=4, sticky="NSWE")
        self.scrollbar.config(command = self.regDataListBox.yview)

        #Command layer
        self.cmd_regType_value = tkinter.StringVar(value='Coil')
        self.cmd_dropdown = OptionMenu(self.master, self.cmd_regType_value, "Coil", "Discrete input", "Input register", "Holding register")
        self.cmd_dropdown.grid(row=1, column=0, sticky="WE")
        self.cmd_register_value = tkinter.StringVar(value="10000")
        self.cmd_register = tkinter.Entry(self.master, textvariable=self.cmd_register_value)
        self.cmd_register.grid(row=1, column=1, sticky="WE")
        self.cmd_value_value = tkinter.StringVar(value="0")
        self.cmd_value = tkinter.Entry(self.master, textvariable=self.cmd_value_value)
        self.cmd_value.grid(row=1, column=2, sticky="WE")
        self.cmd_send_button = tkinter.Button(self.master, text="SEND", command=self.sendCmd)
        self.cmd_send_button.grid(row=1, column=3, columnspan=2, sticky="WE")

        self.statusTxt = tkinter.StringVar(value='IP Address: Not connected')
        self.StatusBar = tkinter.Label(self.master, textvariable=self.statusTxt)
        self.StatusBar.grid(row=2, column=0, columnspan=4, sticky="NSW")

        

    def createClient(self, xmlFile, cycleTime_ms=500):
        #Load the signals into the container
        self.cycleTime_ms=cycleTime_ms

        self.master.after(100, self._update)
        return

    def sendCmd(self):
        return

    def _update(self):
        connected = False
        #Request new data
        if connected:
            if self.statusTxt.get()[-3:] == '(/)':
                self.statusTxt.set(r'IP Address: self.client.ip (\)')
            else:
                self.statusTxt.set(r'IP Address: self.client.ip (/)')

            #data = self.client.getData()
            
            #Refresh data every half a second
            self.master.after(self.cycleTime_ms, self._update)
        else:
            self.statusTxt.set('IP Address: Connection fail occurred, retrying in 5 sec')
            self.master.after(5000, self._update)


####MAIN APP#######
if __name__ == '__main__': 
    root = tkinter.Tk()
    gui = reader(root)
    gui.createClient(r'client_signals.xml', cycleTime_ms=500)

    #Call main loop
    root.mainloop()

