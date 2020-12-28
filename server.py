#Import pymodbus components
from pymodbus.server.sync import StartTcpServer
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSparseDataBlock
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext

#Import local scripts componenets
import xml.etree.ElementTree as ET
from threading import Thread
import time, logging

class Server:
    """Server simulator that serves on given ip and port and generates signals based on xml file"""
    def __init__(self, xmlFile):
        self.xml = xmlFile
        self.validateXml()

        parsedData = self._parseXml()
        registers = parsedData.get('registers')
        
        store = ModbusSlaveContext(
            di=ModbusSequentialDataBlock(registers.get('di').get('startAdr'), registers.get('di').get('regs')),
            ir=ModbusSequentialDataBlock(registers.get('ir').get('startAdr'), registers.get('ir').get('regs')),
            co=ModbusSequentialDataBlock(registers.get('co').get('startAdr'), registers.get('co').get('regs')),
            hr=ModbusSequentialDataBlock(registers.get('hr').get('startAdr'), registers.get('hr').get('regs')))

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

    def validateXml(self):
        """Validates given xml file for correct format before the program starts"""
        tree = ET.parse(self.xml)
        root = tree.getroot()
        registers = root.find('registers')
        deviceData = root.find('deviceData')
        if registers == None or deviceData == None:
            raise Exception('XML file is not of correct format. Nodes registers and/or deviceData missing')
        return True

    def _parseXml(self):
        """Parses xml file and validates the registers"""
        data = {}

        tree = ET.parse(self.xml)
        root = tree.getroot()
        registers = root.find('registers')

        #Discrete inputs (booleans)
        di = []
        diStartAdr = 0
        diNode = registers.find('di')
        if diNode != None:
            diStartAdr = int(diNode.get('startingRegister'))
            for mapping in diNode.findall('mapping'):
                if mapping.get('initialValue') != None:
                    di.append(int(mapping.get('initialValue')))
                else:
                    di.append(0)
        else:
            di.append(0)

        #Input registers (analogs)
        ir = []
        irStartAdr = 0
        irNode = registers.find('ir')
        if irNode != None:
            irStartAdr = int(irNode.get('startingRegister'))
            for mapping in irNode.findall('mapping'):
                if mapping.get('initialValue') != None:
                    ir.append(int(mapping.get('initialValue')))
                else:
                    ir.append(0)
        else:
            ir.append(0)

        #Holding registers (analogs)
        hr = []
        hrStartAdr = 0
        hrNode = registers.find('hr')
        if hrNode != None:
            hrStartAdr = int(hrNode.get('startingRegister'))
            for mapping in hrNode.findall('mapping'):
                if mapping.get('initialValue') != None:
                    hr.append(int(mapping.get('initialValue')))
                else:
                    hr.append(0)
        else:
            hr.append(0)

        #Coils (booleans)
        co = []
        coStartAdr = 0
        coNode = registers.find('co')
        if coNode != None:
            coStartAdr = int(coNode.get('startingRegister'))
            for mapping in coNode.findall('mapping'):
                if mapping.get('initialValue') != None:
                    co.append(int(mapping.get('initialValue')))
                else:
                    co.append(0)
        else:
            co.append(0)
        data['registers'] = {
            'di' : {
                'startAdr' : diStartAdr,
                'regs' : di},
            'ir' : {
                'startAdr' : irStartAdr,
                'regs' : ir},
            'hr' : {
                'startAdr' : hrStartAdr,
                'regs' : hr},
            'co' : {
                'startAdr' : coStartAdr,
                'regs' : co}
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
            di_values = self.context[0].getValues(2, self.registers.get('di').get('startAdr')-1, count=len(self.registers.get('di').get('regs')))
            new_values = [v - 1 if v == 1 else v + 1 for v in di_values]
            self.context[0].setValues(2, self.registers.get('di').get('startAdr')-1, new_values)

            co_values = self.context[0].getValues(1, self.registers.get('co').get('startAdr')-1, count=len(self.registers.get('co').get('regs')))
            new_values = [v - 1 if v == 1 else v + 1 for v in co_values]
            self.context[0].setValues(1, self.registers.get('co').get('startAdr')-1, new_values)

            hr_values = self.context[0].getValues(3, self.registers.get('hr').get('startAdr')-1, count=len(self.registers.get('hr').get('regs')))
            new_values = [v + 1 for v in hr_values]
            self.context[0].setValues(3, self.registers.get('hr').get('startAdr')-1, new_values)

            ir_values = self.context[0].getValues(4, self.registers.get('ir').get('startAdr')-1, count=len(self.registers.get('ir').get('regs')))
            new_values = [v + 1 for v in ir_values]
            self.context[0].setValues(4, self.registers.get('ir').get('startAdr')-1, new_values)

            #print(self.registers.get('di').get('startAdr'))
            #print(self.context[0].getValues(1, self.registers.get('di').get('startAdr'), count=len(self.registers.get('di').get('regs'))))
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

        if increment:
            thread = Thread(target=self.incRegValues, args=(cycle_s,), daemon=True)
            thread.start()

        print(f"Running server on IP: {self.ip} and port {self.port}")
        StartTcpServer(self.context, identity=self.deviceIdentity, address=(self.ip, self.port))

if __name__ == "__main__":
    
    sim = Server(r'client_server_signals.xml')
    sim.run_server(increment=True, cycle_s = 1)
