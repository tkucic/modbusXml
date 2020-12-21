#Checks if modbus communication works through python
from pymodbus.client.sync import ModbusTcpClient as ModbusClient
import xml.etree.ElementTree as ET
import tkinter, os
from tkinter import ttk, filedialog, messagebox

class DiscreteInput:
    def __init__(self, node, client):
        self.client = client
        self.Group = node.attrib.get('Group')
        self.Address = int(float(node.attrib.get('ScriptDataAdr')))
        self.Name = node.attrib.get('Signal_name')
        self.Unit = node.attrib.get('Unit')
        
    def readValue(self):
        if self.client.connect():
            data = None
            try:
                data = self.client.read_discrete_inputs(address=self.Address, count=1)
                return data.getBit(0)

            except Exception as e:
                return e
        else:
            return f'Connection failed'

    def __str__(self):
        return f"{self.Group.ljust(50 - len(self.Group), '_')}{self.Name.ljust(100 - len(self.Name), '_')}{self.Unit.ljust(15 - len(self.Unit), '_')}Value:" + f"{self.readValue()}".rjust(25, ' ')

class InputRegister:
    def __init__(self, node, client):
        self.client = client
        self.Group = node.attrib.get('Group')
        self.Address = int(float(node.attrib.get('ScriptDataAdr')))
        self.Name = node.attrib.get('Signal_name')
        self.Unit = node.attrib.get('Unit')
        self.Scale = float(node.attrib.get('Scale'))
        self.Size = int(float(node.attrib.get('Size')))

    def readValue(self):
        if self.client.connect():
            data = None
            try:
                data = self.client.read_input_registers(address=self.Address, count=self.Size)
                #Handle the read data
                if self.Size == 1:
                    return data.getRegister(0)
                else:
                    x = data.getRegister(0)
                    y = data.getRegister(1)

                    #Shift to the left by 16 bits, then add the other 16 bits there
                    return (x << 16) + y
            except Exception as e:
                return e
        else:
            return f'Connection failed'

    def __str__(self):
        return f"{self.Group.ljust(50 - len(self.Group), '_')}{self.Name.ljust(100 - len(self.Name), '_')}{self.Unit.ljust(15 - len(self.Unit), '_')}Value:" + f"{self.readValue()}".rjust(25, ' ')

class reader:
    def __init__(self, ip, xmlData):
        self.ip = ip
        self.client = ModbusClient(ip)

        #create window
        self.window = tkinter.Toplevel()
        self.window.geometry('800x600')
        tkinter.Grid.rowconfigure(self.window, 0, weight=1)
        tkinter.Grid.columnconfigure(self.window, 0, weight=1)
        tkinter.Grid.columnconfigure(self.window, 1, weight=1)
        tkinter.Grid.columnconfigure(self.window, 2, weight=1)
        tkinter.Grid.columnconfigure(self.window, 3, weight=1)
        tkinter.Grid.rowconfigure(self.window, 0, weight=0)
        tkinter.Grid.rowconfigure(self.window, 1, weight=2)
        tkinter.Grid.rowconfigure(self.window, 2, weight=0)

        #Create scrollbar
        self.scrollbar = tkinter.Scrollbar(self.window)
        self.scrollbar.grid(row=1, column=4, columnspan=3, sticky='NSE')

        col1Width = 50
        col2Width = 80
        col3Width = 50
        col4Width = 50

        #Create the filters
        self.idFilterVal = tkinter.StringVar()
        self.descFilterVal = tkinter.StringVar()
        self.unitFilterVal = tkinter.StringVar()
        self.idFilter = ttk.Entry(self.window, width=col1Width, textvariable=self.idFilterVal)
        self.descFilter = ttk.Entry(self.window, width=col2Width, textvariable=self.descFilterVal)
        self.unitFilter = ttk.Entry(self.window, width=col3Width, textvariable=self.unitFilterVal)
        self.idFilter.grid(row=0, column=0)
        self.descFilter.grid(row=0, column=1) 
        self.unitFilter.grid(row=0, column=2) 

        #parse the xml and distribute nodes
        self.mdbIO = xmlData

        self.idData = tkinter.StringVar()
        self.descData = tkinter.StringVar()
        self.unitData = tkinter.StringVar()
        self.valueData = tkinter.StringVar()
        self.idCol = tkinter.Listbox(self.window, width= col1Width, yscrollcommand=self.yscroll1, listvariable=self.idData)
        self.descCol = tkinter.Listbox(self.window, width= col2Width, yscrollcommand=self.yscroll2, listvariable=self.descData)
        self.unitCol = tkinter.Listbox(self.window, width= col3Width, yscrollcommand=self.yscroll3,listvariable=self.unitData)
        self.valueCol = tkinter.Listbox(self.window, width= col4Width, yscrollcommand=self.yscroll4,listvariable=self.valueData)
        self.scrollbar.config(command = self.yview)

        self.idCol.grid(row=1, column=0, sticky="NSWE")
        self.descCol.grid(row=1, column=1, sticky="NSWE")
        self.unitCol.grid(row=1, column=2, sticky="NSWE")
        self.valueCol.grid(row=1, column=3, sticky="NSWE")

        self.statusTxt = tkinter.StringVar()
        self.statusTxt.set('/')
        self.StatusBar = tkinter.Label(self.window, textvariable=self.statusTxt)
        self.StatusBar.grid(row=2, column=0, columnspan=4, sticky="NSW")

        #Load the signals into the container
        self.window.after(100, self._update)

    def yscroll1(self, *args):
        if self.idCol.yview() != self.descCol.yview():
            self.descCol.yview_moveto(args[0])
            self.unitCol.yview_moveto(args[0])
            self.valueCol.yview_moveto(args[0])
        self.scrollbar.set(*args)

    def yscroll2(self, *args):
        if self.descCol.yview() != self.idCol.yview():
            self.idCol.yview_moveto(args[0])
            self.unitCol.yview_moveto(args[0])
            self.valueCol.yview_moveto(args[0])
        self.scrollbar.set(*args)

    def yscroll3(self, *args):
        if self.unitCol.yview() != self.idCol.yview():
            self.idCol.yview_moveto(args[0])
            self.descCol.yview_moveto(args[0])
            self.valueCol.yview_moveto(args[0])
        self.scrollbar.set(*args)

    def yscroll4(self, *args):
        if self.valueCol.yview() != self.descCol.yview():
            self.idCol.yview_moveto(args[0])
            self.descCol.yview_moveto(args[0])
            self.unitCol.yview_moveto(args[0])
        self.scrollbar.set(*args)

    def yview(self, *args):
        self.idCol.yview(*args)
        self.descCol.yview(*args)
        self.unitCol.yview(*args)
        self.valueCol.yview(*args)

    def _update(self):
        #clear the container
        if self.statusTxt.get() == '(->)':
            self.statusTxt.set('(<-)')
        else:
            self.statusTxt.set('(->)')

        idData = []
        descData = []
        unitData = []
        valueData = []

        #Add new data
        if self.client.connect():
            for sigNode in list(self.mdbIO):
                #Apply filters
                if sigNode.get('Group').lower().startswith(self.idFilterVal.get().lower()) and sigNode.get('Signal_name').lower().startswith(self.descFilterVal.get().lower()) and sigNode.get('Unit').lower().startswith(self.unitFilterVal.get().lower()):
                    dataObj = None
                    if sigNode.get('Register_type') == 'Discrete inputs':
                        dataObj = DiscreteInput(sigNode,self.client)
                        idData.append(sigNode.get('Group'))
                        descData.append(sigNode.get('Signal_name'))
                        unitData.append(sigNode.get('Unit'))
                        valueData.append(str(dataObj.readValue()))

                    elif sigNode.get('Register_type') == 'Input register':
                        dataObj = InputRegister(sigNode,self.client)
                        idData.append(sigNode.get('Group'))
                        descData.append(sigNode.get('Signal_name'))
                        unitData.append(sigNode.get('Unit'))
                        valueData.append(str(dataObj.readValue()))

            self.idData.set(idData)
            self.descData.set(descData)
            self.unitData.set(unitData)
            self.valueData.set(valueData)

            #Refresh data every half a second
            self.window.after(500, self._update)
        else:
            self.statusTxt.set('Connection fail occurred, retrying in 5 sec')
            self.window.after(5000, self._update)
        
def runChecker1():

    if xmlValid(textLoc.get()):
        #Open the file, parse it and distribute nodes
        root = ET.parse(textLoc.get())
        mdbIO = root.find('ModbusTCP_Signals')

        readerWindow = reader(plc1Ip.get(), mdbIO)
    else:
        messagebox.showinfo("Error", "Incompatible xml file")

def runChecker2():

    if xmlValid(textLoc.get()):
        #Open the file, parse it and distribute nodes
        root = ET.parse(textLoc.get())
        mdbIO = root.find('ModbusTCP_Signals')

        readerWindow = reader(plc2Ip.get(), mdbIO)
    else:
        messagebox.showinfo("Error", "Incompatible xml file")

def xmlValid(path):
    try:
        root = ET.parse(path)
        mdbIO = root.find('ModbusTCP_Signals')
        if mdbIO != None:
            return True
        return False
    except:
        return False

def browseForXml():
        fname = filedialog.askopenfilename(initialdir =  "/", title = "Select a compatible xml file", filetype =
        (("XML files","*.xml"),("all files","*.*")) )
        if xmlValid(fname):
            textLoc.set(fname)
        else:
            messagebox.showinfo("Error", "Incompatible xml file")

####MAIN APP#######
if __name__ == '__main__': 
    win = tkinter.Tk()
    win.title('Modbus TCP checker')

    #Program configuration
    IOListPath = os.path.join(os.getcwd(), '../../../Config/IOList.xml')
    IOListPath = os.path.abspath(os.path.realpath(IOListPath))

    #Create variables
    plc1Ip = tkinter.StringVar()
    plc2Ip = tkinter.StringVar()
    textLoc = tkinter.StringVar()
    plc1Ip.set('172.16.1.101')
    plc2Ip.set('172.16.1.102')
    textLoc.set(IOListPath)

    #Create widgets
    textLocLabel = ttk.Label(win, text='Path to IO xml file: ')
    textLocEntry = ttk.Entry(win, width=100, textvariable=textLoc)
    plc1IpLabel = ttk.Label(win, text='Enter OMD1 IP: ')
    plc2IpLabel = ttk.Label(win, text='Enter OMD2 IP: ')
    plc1IpEntry = ttk.Entry(win, width=100, textvariable=plc1Ip)
    plc2IpEntry = ttk.Entry(win, width=100, textvariable=plc2Ip)
    checkPlc1Button = ttk.Button(win, text='Run checker', command=runChecker1)
    checkPlc2Button = ttk.Button(win, text='Run checker', command=runChecker2)
    txtLocButton = ttk.Button(win, text='Browse', command=browseForXml)

    #Place thw widgets on the screen
    textLocLabel.grid(row=0, column=0)
    textLocEntry.grid(row=0, column=1)
    txtLocButton.grid(row=0, column=2)
    plc1IpLabel.grid(row=1, column=0)
    plc2IpLabel.grid(row=2, column=0)
    plc1IpEntry.grid(row=1, column=1)
    plc2IpEntry.grid(row=2, column=1)
    checkPlc1Button.grid(row=1, column=2)
    checkPlc2Button.grid(row=2, column=2)

    #Call main loop
    win.mainloop()

