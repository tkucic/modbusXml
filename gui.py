import tkinter, sys, threading, time
from tkinter import ttk
from client import reader

def checkBit(x, n):
    if (x & (1<<n)):
        # n-th bit is set (1)
        return True
    else: 
        # n-th bit is not set (0)
        return False

class readerGui:
    def __init__(self, master):

        self.master = master
        master.withdraw()
        #master.overrideredirect(True)
        master.title('Modbus TCP/IP/RTU client')
        master.geometry('600x600')
        master.minsize(width=600, height=600)
        master.configure(bg='#1e1e1e')

        #Configure rows and columns 7x4 geometry
        tkinter.Grid.rowconfigure(self.master, 0, weight=1) #Content expands on all sides
        tkinter.Grid.rowconfigure(self.master, 1, weight=0) #Cmd frame
        tkinter.Grid.rowconfigure(self.master, 2, weight=0) #Status bar
        
        tkinter.Grid.columnconfigure(self.master, 0, weight=1)
        tkinter.Grid.columnconfigure(self.master, 1, weight=0)

        #Create scrollbar
        self.scrollbar = ttk.Scrollbar(self.master)
        self.scrollbar.grid(row=0, column=1, sticky='NSE')

        #Create the register view
        self.regDataListBox = ttk.Treeview(self.master, yscrollcommand=self.scrollbar.set)
        self.regDataListBox['columns'] = ('Type', 'Register', 'Value', 'Description')
        self.regDataListBox.column('#0', width=0, stretch='no')
        self.regDataListBox.column('Type', width='125', anchor='w')
        self.regDataListBox.column('Register', width='75', anchor='center')
        self.regDataListBox.column('Value', width='75', anchor='center')
        self.regDataListBox.column('Description', width='300', anchor='w')
        self.regDataListBox.heading('#0', text='')
        self.regDataListBox.heading('Type', text='Type', anchor='w')
        self.regDataListBox.heading('Register', text='Register', anchor='center')
        self.regDataListBox.heading('Value', text='Value', anchor='center')
        self.regDataListBox.heading('Description', text='Description', anchor='w')
        self.regDataListBox.state(('disabled',))
        self.regDataListBox.grid(row=0, column=0, sticky="NSWE", padx=5, pady=5)
        self.scrollbar.config(command = self.regDataListBox.yview)

        #Command layers
        cmdFrame = ttk.Frame(self.master)
        cmdFrame.grid(row=1, column=0, columnspan=2, sticky='W', padx=5, pady=2)
        for i in range(0,5):
            tkinter.Grid.rowconfigure(cmdFrame, i, weight=1)
        for i in range(0,6):
            tkinter.Grid.columnconfigure(cmdFrame, i, weight=1)
        for i, text in enumerate(['Register type', 'Register', 'Value', 'Increment', 'Send once', 'Cycle send']):
            infoLabel = ttk.Label(cmdFrame, text=text, anchor='center',relief=tkinter.RIDGE)
            infoLabel.grid(row=0, column=i, sticky="WE", pady=5)

        self.cmd_reg = [tkinter.StringVar(value='-1') for i in range(4)]
        self.cmd_value = [tkinter.StringVar(value='0') for i in range(4)]
        self.cmd_inc = [tkinter.IntVar() for i in range(4)]
        self.cmd_once = [tkinter.IntVar() for i in range(4)]
        self.cmd_cyclic = [tkinter.IntVar() for i in range(4)]
        self.cmd_regType = [ttk.Combobox(cmdFrame, state="readonly", values=["           Coil           ", "Holding register"]) for i in range(4)]
        for i in range(4):
            self.cmd_regType[i].grid(row=i+1, column=0, sticky='WE')
            self.cmd_regType[i].current(0)
        cmd_regEntry = [ttk.Entry(cmdFrame, textvariable=self.cmd_reg[i]).grid(row=i+1, column=1, sticky='W') for i in range(4)]
        cmd_regValueEntry = [ttk.Entry(cmdFrame, textvariable=self.cmd_value[i]).grid(row=i+1, column=2, sticky='WE') for i in range(4)]
        cmd_incCb = [ttk.Checkbutton(cmdFrame, variable=self.cmd_inc[i]).grid(row=i+1, column=3, sticky='WE', padx=25) for i in range(4)]
        cmd_sendOnceCb = [ttk.Checkbutton(cmdFrame, variable=self.cmd_once[i]).grid(row=i+1, column=4, sticky='WE', padx=25) for i in range(4)]
        cmd_cyclicCb = [ttk.Checkbutton(cmdFrame, variable=self.cmd_cyclic[i]).grid(row=i+1, column=5, sticky='WE', padx=25) for i in range(4)]

        #Status bar
        statusFrame = ttk.Frame(self.master)
        statusFrame.grid(row=2, column=0, columnspan=2, sticky='WE', padx=0, pady=0)
        tkinter.Grid.rowconfigure(statusFrame, 0, weight=1)
        tkinter.Grid.columnconfigure(statusFrame, 0, weight=1)
        tkinter.Grid.columnconfigure(statusFrame, 1, weight=1)

        self.statusTxt = tkinter.StringVar(value='Not connected')
        ttk.Label(statusFrame, anchor='w', textvariable=self.statusTxt,relief=tkinter.RIDGE).grid(row=0, column=0, sticky="WE")

        self.cycleTxt = tkinter.StringVar(value='Latency: xx ms')
        ttk.Label(statusFrame, anchor='e', textvariable=self.cycleTxt,relief=tkinter.RIDGE).grid(row=0, column=1, sticky="WE")

        #Configure styles
        BG2 ='#252526'
        BG ='#1e1e1e'
        FG ='#cccccc'
        HC = '#202d39'
        style = ttk.Style()
        style.theme_use('default')
        style.configure('.', font=('Verdana', 8), foreground=FG, background=BG)
        style.configure('Treeview',
            background=BG,
            foreground=FG,
            fieldbackground=BG,
            rowheight=15)
        style.configure('Treeview.Heading',
            fieldbackground=BG,
            rowheight=20,
            relief="ridge")
        style.map('Treeview',
            background=[('selected', HC)],
            foreground=[('selected', FG)])
        style.map('Treeview.Heading',
            background=[('active', BG)],
            foreground=[('active', FG)])
        style.configure('TEntry', foreground=FG, fieldbackground=BG2)
        style.map('TEntry',
            selectbackground=[('focus', HC), ('!focus', HC)])
        style.map('TCombobox',
            background=[('readonly', BG2)],
            foreground=[('readonly', FG)],
            selectbackground=[('readonly', HC)],
            fieldbackground=[('readonly', BG2)])
        style.map('TCheckbutton',
            background=[('active', BG)],
            foreground=[('selected', HC)],
            selectcolor=[('selected', HC)])
        
        self.regDataListBox.tag_configure('child', background=BG2, foreground=FG)

        master.deiconify()

    def createClient(self, xmlFile, cycleTime_ms=500):
        #Create client and commence updating and sending commands on provided cycle time
        self.cycleTime_ms=cycleTime_ms
        self.client = reader(xmlFile)
        self.connected = False
        threading.Thread(target=self._connect_and_update, daemon=True).start()
        self.master.after(100,self._update)
        self.master.after(100, self._sendCmds)
        return

    def _connect_and_update(self):
        while True:
            #Connect to the server, check if connected, check connection every second, if failed check again in 5 seconds
            if self.client.connect():
                self.connected = True
                if self.client.xmlData.get('modbusType') == 'tcp/ip':
                    msg = f"TCP/IP | {self.client.xmlData.get('ip')}:{self.client.xmlData.get('port')} |"
                elif self.client.xmlData.get('modbusType') == 'rtu':
                    msg = f"RTU | {self.client.xmlData.get('com').upper()} | {self.client.xmlData.get('baud')}bps |"
                
                if self.statusTxt.get()[-3:] == '(/)':
                    self.statusTxt.set(f"{msg} (\)")
                else:
                    self.statusTxt.set(f"{msg} (/)")
                
                #update the registers
                updateStartTime = time.perf_counter()
                self.client.update_all()

                #Calculate the latency and display it
                latency_ms = int((time.perf_counter() - updateStartTime) * 1000)
                if latency_ms > 1000:
                    self.cycleTxt.set(f'Latency: {latency_ms / 1000}s')
                else:
                    self.cycleTxt.set(f'Latency: {latency_ms}ms')
                #if cycle time is faster than latency, go to sleep to match the cycle time
                if latency_ms < self.cycleTime_ms:
                    time.sleep((self.cycleTime_ms - latency_ms) / 1000)

            else:
                self.connected = False
                self.statusTxt.set('Connection fail occurred, retrying in 5 sec')
                self.cycleTxt.set('Latency: xx ms')
                time.sleep(5)

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
                        if 'Coil' in self.cmd_regType[i].get():
                            #Coils can take only 1 or 0
                            if value < 0:
                                value = 0
                            elif value > 1:
                                if value % 2 == 0:
                                    value = 1
                                else:
                                    value = 0
                            response = self.client.write_coil(register=int(self.cmd_reg[i].get()), value=value)
                            
                        else:
                            response = self.client.write_register(register=int(self.cmd_reg[i].get()), value=value)
                        #If response was exception
                        if 'Exception' in str(response):
                            self.cmd_once[i].set(0)
                            self.cmd_cyclic[i].set(0)
                            self.cmd_value[i].set(response)

                except Exception as e:
                    self.cmd_once[i].set(0)
                    self.cmd_cyclic[i].set(0)
                    self.cmd_value[i].set(e)

        self.master.after(500, self._sendCmds)

    def _update(self):
        vw = self.regDataListBox.yview()
        #Request new data
        if self.connected:
            #Create entries if empty
            if len(self.regDataListBox.get_children()) == 0:
                for co in self.client.xmlData.get('registers').get('co'):
                    self.regDataListBox.insert(parent='', index='end', iid=co.get('register'), text='', values=('COIL', co.get('register'), co.get('value'), co.get('description')))
                for di in self.client.xmlData.get('registers').get('di'):
                    self.regDataListBox.insert(parent='', index='end', iid=di.get('register'), text='', values=('DISCRETE INPUT', di.get('register'), di.get('value'), di.get('description')))
                for ir in self.client.xmlData.get('registers').get('ir'):
                    self.regDataListBox.insert(parent='', index='end', iid=ir.get('register'), text='', values=('INPUT REGISTER', ir.get('register'), ir.get('value'), ir.get('description')))
                    for ix, i in enumerate(range(16)):
                        self.regDataListBox.insert(parent=ir.get('register'), index='end', iid=f"{ir.get('register')}.{i}", text='', values=(f"BIT {i}", f"{ir.get('register')}.{i}", checkBit(ir.get('value'), i), ir.get(f"bit{ix}")), tags = ('child',))
                for hr in self.client.xmlData.get('registers').get('hr'):
                    self.regDataListBox.insert(parent='', index='end', iid=hr.get('register'), text='', values=('HOLDING REGISTER', hr.get('register'), hr.get('value'), hr.get('description')))
                    for ix, i in enumerate(range(16)):
                        self.regDataListBox.insert(parent=hr.get('register'), index='end', iid=f"{hr.get('register')}.{i}", text='', values=(f"BIT {i}", f"{hr.get('register')}.{i}", checkBit(hr.get('value'), i), hr.get(f"bit{ix}")), tags = ('child',))
            else:
                #Update existing
                for co in self.client.xmlData.get('registers').get('co'):
                    self.regDataListBox.item(co.get('register'), text='', values=('COIL', co.get('register'), co.get('value'), co.get('description')))
                for di in self.client.xmlData.get('registers').get('di'):
                    self.regDataListBox.item(di.get('register'), text='', values=('DISCRETE INPUT', di.get('register'), di.get('value'), di.get('description')))
                for ir in self.client.xmlData.get('registers').get('ir'):
                    self.regDataListBox.item(ir.get('register'), text='', values=('INPUT REGISTER', ir.get('register'), ir.get('value'), ir.get('description')))
                    for ix, i in enumerate(range(16)):
                        self.regDataListBox.item(f"{ir.get('register')}.{i}", text='', values=(f"BIT {i}", f"{ir.get('register')}.{i}", checkBit(ir.get('value'), i), ir.get(f"bit{ix}")), tags = ('child',))
                for hr in self.client.xmlData.get('registers').get('hr'):
                    self.regDataListBox.item(hr.get('register'), text='', values=('HOLDING REGISTER', hr.get('register'), hr.get('value'), hr.get('description')))
                    for ix, i in enumerate(range(16)):
                        self.regDataListBox.item(f"{hr.get('register')}.{i}", text='', values=(f"BIT {i}", f"{hr.get('register')}.{i}", checkBit(hr.get('value'), i), hr.get(f"bit{ix}")), tags = ('child',))

        self.regDataListBox.yview_moveto(vw[0])
        self.master.after(100,self._update)

####MAIN APP#######
if __name__ == '__main__':

    #handle arguments to the script
    #Default arguments
    cycleTime_ms = 1500

    opts = [opt for opt in sys.argv[1:] if opt.startswith("-")]
    args = [arg for arg in sys.argv[1:] if not arg.startswith("-")]

    #xml file path must be first
    xmlFilePath = args[0]

    try:
        cycleTime_ms = int(args[1])
    except IndexError:
        #If cycle time not passed in then use default
        pass

    root = tkinter.Tk()
    gui = readerGui(root)
    gui.createClient(xmlFilePath, cycleTime_ms=cycleTime_ms)

    #Call main loop
    root.mainloop()