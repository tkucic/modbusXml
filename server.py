#Import pymodbus components
from pymodbus.server.sync import StartTcpServer
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSparseDataBlock
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext

#Import local scripts componenets
import xml.etree.ElementTree as ET
from threading import Thread
import time, logging, sys
from client import validateXml

class Server:
    """Server simulator that serves on given ip and port and generates signals based on xml file"""
    def __init__(self, xmlFile):
        self.xml = xmlFile
        validationInt = validateXml(self.xml)
        if validationInt == -1: raise Exception('XML File Error: IP address missing')
        elif validationInt == -2: raise Exception('XML File Error: No register mappings')
        elif validationInt == -3: raise Exception('XML File Error: Duplicated Input register mapping')
        elif validationInt == -4: raise Exception('XML File Error: Duplicated Discrete input mapping')
        elif validationInt == -5: raise Exception('XML File Error: Duplicated Holding register mapping')
        elif validationInt == -6: raise Exception('XML File Error: Duplicated Coil mapping')

        parsedData = self._parseXml()
        registers = parsedData.get('registers')
        
        store = ModbusSlaveContext(
            di=ModbusSequentialDataBlock(0, registers.get('di')),
            ir=ModbusSequentialDataBlock(0, registers.get('ir')),
            co=ModbusSequentialDataBlock(0, registers.get('co')),
            hr=ModbusSequentialDataBlock(0, registers.get('hr')))

        self.context = ModbusServerContext(slaves=store, single=True)
        self.registers = registers
        self.ip = parsedData.get('ip')
        self.port = parsedData.get('port')
        self.deviceIdentity = ModbusDeviceIdentification()
        self.deviceIdentity.VendorName = parsedData.get("vendorName")
        self.deviceIdentity.ProductCode = parsedData.get("productCode")
        self.deviceIdentity.VendorUrl = parsedData.get("vendorUrl")
        self.deviceIdentity.ProductName = parsedData.get("productName")
        self.deviceIdentity.ModelName = parsedData.get("modelName")
        self.deviceIdentity.MajorMinorRevision = parsedData.get("Version")

    def _parseXml(self):
        """Parses xml file and validates the registers"""
        data = {}

        tree = ET.parse(self.xml)
        root = tree.getroot()
        registers = root.find('registers')

        #Discrete inputs (booleans)
        diNode = registers.find('di')
        if diNode != None:
            di = [0]*65535
            for mapping in diNode.findall('mapping'):
                ix = int(mapping.get('register')) 
                if mapping.get('initialValue') != None:
                    di[ix] = int(mapping.get('initialValue'))
        else:
            di = [0]

        #Input registers (analogs)
        irNode = registers.find('ir')
        if irNode != None:
            ir = [0]*65535
            for mapping in irNode.findall('mapping'):
                ix = int(mapping.get('register')) 
                if mapping.get('initialValue') != None:
                    ir[ix] = int(mapping.get('initialValue'))
        else:
            ir = [0]

        #Holding registers (analogs)
        hrNode = registers.find('hr')
        if hrNode != None:
            hr = [0]*65535
            for mapping in hrNode.findall('mapping'):
                ix = int(mapping.get('register')) 
                if mapping.get('initialValue') != None:
                    hr[ix] = int(mapping.get('initialValue'))
        else:
            hr = [0]

        #Coils (booleans)
        coNode = registers.find('co')
        if coNode != None:
            co = [0]*65535
            for mapping in coNode.findall('mapping'):
                ix = int(mapping.get('register')) 
                if mapping.get('initialValue') != None:
                    co[ix] = int(mapping.get('initialValue'))
        else:
            co = [0]
        
        data['registers'] = {
            'di' : di,
            'ir' : ir,
            'hr' : hr,
            'co' : co
        }

        #Parse device data
        deviceData = root.find('deviceData')
        data['vendorName'] = deviceData.get("vendorName", '')
        data['productCode'] = deviceData.get("productCode", '')
        data['vendorUrl'] = deviceData.get("vendorUrl", '')
        data['productName'] = deviceData.get("productName", '')
        data['modelName'] = deviceData.get("modelName", '')
        data['version'] = deviceData.get("version", '0.0-1')
        data['ip'] = deviceData.get("ip")
        data['port'] = int(deviceData.get("port", 502))

        return data

    def incRegValues(self, cycle_s):
        """ A worker process that runs on a given cycle and
        updates live values of the context.
        """
        while True:

            #Get values from only the first slave/ multiple slaves unsupported
            #Toggle values of coils and digital inputs
            di_values = self.context[0].getValues(2, -1, count=len(self.registers.get('di')))
            new_values = [v - 1 if v == 1 else v + 1 for v in di_values]
            self.context[0].setValues(2, -1, new_values)

            co_values = self.context[0].getValues(1, -1, count=len(self.registers.get('co')))
            new_values = [v - 1 if v == 1 else v + 1 for v in co_values]
            self.context[0].setValues(1, -1, new_values)

            hr_values = self.context[0].getValues(3, -1, count=len(self.registers.get('hr')))
            new_values = [v + 1 for v in hr_values]
            self.context[0].setValues(3, -1, new_values)

            ir_values = self.context[0].getValues(4, -1, count=len(self.registers.get('ir')))
            new_values = [v + 1 for v in ir_values]
            self.context[0].setValues(4, -1, new_values)

            #print(self.context[0].getValues(1, 0, count=len(self.registers.get('di'))))
            #print(self.context[0].getValues(2, 0, count=65535))
            #print(self.context[0].getValues(3, 0, count=65535))
            #print(self.context[0].getValues(4, 0, count=65535))
            
            time.sleep(cycle_s)

    def run_server(self, increment = True, cycle_s = 5, debug = True):
        """Runs the modbus tcp server with given register information. if increment is true, the register values are dynamic and incrementing by one
        every interval provided in cycle_s argument"""
        if debug:
            logging.basicConfig()
            log = logging.getLogger()
            log.setLevel(logging.DEBUG)

        try:
            if increment:
                thread = Thread(target=self.incRegValues, args=(cycle_s,), daemon=True)
                thread.start()

            print(f"Running server on IP: {self.ip} and port {self.port}")
            StartTcpServer(self.context, identity=self.deviceIdentity, address=(self.ip, self.port))
        except KeyboardInterrupt:
            print('Server stopped')

####MAIN APP#######
if __name__ == '__main__':

    #handle arguments to the script
    #Default arguments
    increment = False
    cycleTime_s = 1

    opts = [opt for opt in sys.argv[1:] if opt.startswith("-")]
    args = [arg for arg in sys.argv[1:] if not arg.startswith("-")]
    #xml file path must be first
    xmlFilePath = args[0]

    try:
        cycleTime_s = int(int(args[1]) / 1000)
    except IndexError:
        #If cycle time not passed in then use default
        pass

    if '-i' in opts:
        increment = True
    if '--increment' in opts:
        increment = True

    sim = Server(xmlFilePath)
    sim.run_server(increment=increment, cycle_s = cycleTime_s)
