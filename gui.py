import tkinter, os
from client import reader

class readerGui:
    def __init__(self, master):

        self.master = master
        master.title('Modbus TCP client')
        master.geometry('600x600')

        #create window
        tkinter.Grid.rowconfigure(self.master, 0, weight=0)
        tkinter.Grid.rowconfigure(self.master, 1, weight=1)
        tkinter.Grid.rowconfigure(self.master, 2, weight=0)
        tkinter.Grid.rowconfigure(self.master, 3, weight=0)
        tkinter.Grid.columnconfigure(self.master, 0, weight=1)
        tkinter.Grid.columnconfigure(self.master, 1, weight=1)
        tkinter.Grid.columnconfigure(self.master, 2, weight=1)
        tkinter.Grid.columnconfigure(self.master, 3, weight=1)
        tkinter.Grid.columnconfigure(self.master, 4, weight=0)

        #Create top description labels
        self.topInfo = tkinter.Label(self.master, anchor='w', text=f"{'Type':<36}| {'Register':<13}| {'Value':<15}| Description")
        self.topInfo.grid(row=0, column=0, columnspan=4, sticky="WE")

        #Create scrollbar
        self.scrollbar = tkinter.Scrollbar(self.master)
        self.scrollbar.grid(row=1, column=4, sticky='NSE')

        #Create the register view
        self.registerData = tkinter.StringVar()
        self.regDataListBox = tkinter.Listbox(self.master, yscrollcommand=self.scrollbar.set)
        self.regDataListBox.grid(row=1, column=0, columnspan=4, sticky="NSWE")
        self.scrollbar.config(command = self.regDataListBox.yview)

        #Command layer
        self.cmd_regType_value = tkinter.StringVar(value='Coil')
        self.cmd_dropdown = tkinter.OptionMenu(self.master, self.cmd_regType_value, "Coil", "Discrete input", "Input register", "Holding register")
        self.cmd_dropdown.grid(row=2, column=0, sticky="WE")
        self.cmd_register_value = tkinter.StringVar(value="10000")
        self.cmd_register = tkinter.Entry(self.master, textvariable=self.cmd_register_value)
        self.cmd_register.grid(row=2, column=1, sticky="WE")
        self.cmd_value_value = tkinter.StringVar(value="0")
        self.cmd_value = tkinter.Entry(self.master, textvariable=self.cmd_value_value)
        self.cmd_value.grid(row=2, column=2, sticky="WE")
        self.cmd_send_button = tkinter.Button(self.master, text="SEND", command=self.sendCmd)
        self.cmd_send_button.grid(row=2, column=3, columnspan=2, sticky="WE")

        self.statusTxt = tkinter.StringVar(value='IP Address: Not connected')
        self.StatusBar = tkinter.Label(self.master, textvariable=self.statusTxt)
        self.StatusBar.grid(row=3, column=0, columnspan=4, sticky="NSW")

    def createClient(self, xmlFile, cycleTime_ms=500):
        #Load the signals into the container
        self.cycleTime_ms=cycleTime_ms
        self.client = reader(xmlFile)
        self.master.after(100, self._update)
        return

    def sendCmd(self):
        return

    def _update(self):
        #Request new data
        if self.client.connect():
            if self.statusTxt.get()[-3:] == '(/)':
                self.statusTxt.set(f"IP Address: {self.client.ip}:{self.client.port} (\)")
            else:
                self.statusTxt.set(f"IP Address: {self.client.ip}:{self.client.port} (/)")

            self.client.update()
            vw = self.regDataListBox.yview()
            self.regDataListBox.delete(0,tkinter.END)
            for co in self.client.registers.get('co'):  
                line = f" {'COIL':<35}| {co.get('register'):<15}| {co.get('value'):<15}| {co.get('description')}"
                self.regDataListBox.insert(tkinter.END, line)
            for di in self.client.registers.get('di'):
                line = f" {'DISCRETE INPUT':<25}| {di.get('register'):<15}| {di.get('value'):<15}| {di.get('description')}"
                self.regDataListBox.insert(tkinter.END, line)
            for ir in self.client.registers.get('ir'):
                line = f" {'INPUT REGISTER':<25}| {ir.get('register'):<15}| {ir.get('value'):<15}| {ir.get('description')}"
                self.regDataListBox.insert(tkinter.END, line)
            for hr in self.client.registers.get('hr'):
                line = f" {'HOLDING REGISTER':<21}| {hr.get('register'):<15}| {hr.get('value'):<15}| {hr.get('description')}"
                self.regDataListBox.insert(tkinter.END, line)
            self.regDataListBox.yview_moveto(vw[0])

            #Refresh data every half a second
            self.master.after(self.cycleTime_ms, self._update)
        else:
            self.statusTxt.set('IP Address: Connection fail occurred, retrying in 5 sec')
            self.master.after(5000, self._update)


####MAIN APP#######
if __name__ == '__main__': 
    root = tkinter.Tk()
    gui = readerGui(root)
    gui.createClient(r'client_server_signals.xml', cycleTime_ms=1500)

    #Call main loop
    root.mainloop()

