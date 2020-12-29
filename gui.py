import tkinter, os
from client import reader

class readerGui:
    def __init__(self, master):

        self.master = master
        master.title('Modbus TCP client')
        master.geometry('600x600')

        #cConfigure rows and columns 7x4 geometry
        tkinter.Grid.rowconfigure(self.master, 0, weight=0) #Label
        tkinter.Grid.rowconfigure(self.master, 1, weight=1) #Content expands on all sides
        tkinter.Grid.rowconfigure(self.master, 2, weight=0) #Cmd frame
        tkinter.Grid.rowconfigure(self.master, 3, weight=0) #Status bar
        
        tkinter.Grid.columnconfigure(self.master, 0, weight=1)
        tkinter.Grid.columnconfigure(self.master, 1, weight=0)

        #Create top description labels
        topInfo = tkinter.Label(self.master, anchor='w', text=f"{'Type':<36}| {'Register':<13}| {'Value':<15}| Description")
        topInfo.grid(row=0, column=0, columnspan=2, sticky="WE")

        #Create scrollbar
        self.scrollbar = tkinter.Scrollbar(self.master)
        self.scrollbar.grid(row=1, column=1, sticky='NSE')

        #Create the register view
        self.regDataListBox = tkinter.Listbox(self.master, yscrollcommand=self.scrollbar.set)
        self.regDataListBox.grid(row=1, column=0, sticky="NSWE")
        self.scrollbar.config(command = self.regDataListBox.yview)

        #Command layers
        cmdFrame = tkinter.Frame(self.master)
        cmdFrame.grid(row=2, column=0, columnspan=2, sticky='WE')
        for i in range(0,5):
            tkinter.Grid.rowconfigure(cmdFrame, i, weight=1)
        for i in range(0,6):
            tkinter.Grid.columnconfigure(cmdFrame, i, weight=1)
        for i, text in enumerate(['Register type', 'Register', 'Value', 'Increment', 'Send once', 'Cycle send']):
            infoLabel = tkinter.Label(cmdFrame, text=text)
            infoLabel.grid(row=0, column=i, sticky="WE")

        self.cmd_regType = [tkinter.StringVar(value='Coil') for i in range(4)]
        self.cmd_reg = [tkinter.StringVar(value='10000') for i in range(4)]
        self.cmd_value = [tkinter.StringVar(value='0') for i in range(4)]
        self.cmd_inc = [tkinter.IntVar() for i in range(4)]
        self.cmd_once = [tkinter.IntVar() for i in range(4)]
        self.cmd_cyclic = [tkinter.IntVar() for i in range(4)]
        cmd_dropdown = [tkinter.OptionMenu(cmdFrame, self.cmd_regType[i], "Coil", "Holding register").grid(row=i+1, column=0, sticky='WE') for i in range(4)]
        cmd_regEntry = [tkinter.Entry(cmdFrame, textvariable=self.cmd_reg[i]).grid(row=i+1, column=1, sticky='WE') for i in range(4)]
        cmd_regValueEntry = [tkinter.Entry(cmdFrame, textvariable=self.cmd_value[i]).grid(row=i+1, column=2, sticky='WE') for i in range(4)]
        cmd_incCb = [tkinter.Checkbutton(cmdFrame, variable=self.cmd_inc[i]).grid(row=i+1, column=3, sticky='WE') for i in range(4)]
        cmd_sendOnceCb = [tkinter.Checkbutton(cmdFrame, variable=self.cmd_once[i]).grid(row=i+1, column=4, sticky='WE') for i in range(4)]
        cmd_cyclicCb = [tkinter.Checkbutton(cmdFrame, variable=self.cmd_cyclic[i]).grid(row=i+1, column=5, sticky='WE') for i in range(4)]

        self.statusTxt = tkinter.StringVar(value='IP Address: Not connected')
        statusBar = tkinter.Label(self.master, anchor='w', textvariable=self.statusTxt)
        statusBar.grid(row=3, column=0, columnspan=2, sticky="SWE")

    def createClient(self, xmlFile, cycleTime_ms=500):
        #Create client and commence updating and sending commands on provided cycle time
        self.cycleTime_ms=cycleTime_ms
        self.client = reader(xmlFile)
        self.master.after(100, self._connect)
        self.master.after(100, self._update)
        self.master.after(100, self._sendCmds)
        return

    def _connect(self):
        #Connect to the server, check if connected, check connection every second, if failed check again in 5 seconds
        if self.client.connect():
            self.connected = True
            if self.statusTxt.get()[-3:] == '(/)':
                self.statusTxt.set(f"IP Address: {self.client.ip}:{self.client.port} (\)")
            else:
                self.statusTxt.set(f"IP Address: {self.client.ip}:{self.client.port} (/)")
            self.master.after(1000, self._connect)
        else:
            self.connected = False
            self.statusTxt.set('IP Address: Connection fail occurred, retrying in 5 sec')
            self.master.after(5000, self._connect)

    def _sendCmds(self):
        #Go through the command layers
        if self.connected:
            for i in range(4):
                try:
                    #Dont do anything if command for send once or cyclic is not active
                    
                    if self.cmd_once[i].get() == 1 or self.cmd_cyclic[i].get() == 1:
                        #Turn off the send once command
                        self.cmd_once[i].set(0)
                        #If increment is on, increment
                        if self.cmd_inc[i].get() == 1:
                            value = int(self.cmd_value[i].get())
                            self.cmd_value[i].set(str(value + 1))
                        #Write the actual register
                        value = int(self.cmd_value[i].get())
                        if self.cmd_regType[i].get() == 'Coil':
                            #Coils can take only 1 or 0
                            if value < 0:
                                value = 0
                            elif value > 1:
                                if value % 2 == 0:
                                    value = 1
                                else:
                                    value = 0
                            self.client.write_coil(register=int(self.cmd_reg[i].get()), value=value)
                        else:
                            self.client.write_register(register=int(self.cmd_reg[i].get()), value=value)
                except Exception as e:
                    self.cmd_once[i].set(0)
                    self.cmd_cyclic[i].set(0)
                    self.cmd_value[i].set(e)
        self.master.after(500, self._sendCmds)

    def _update(self):
        #Request new data
        if self.connected:
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

        self.master.after(self.cycleTime_ms, self._update)

####MAIN APP#######
if __name__ == '__main__': 
    root = tkinter.Tk()
    gui = readerGui(root)
    gui.createClient(r'client_server_signals.xml', cycleTime_ms=1500)

    #Call main loop
    root.mainloop()

