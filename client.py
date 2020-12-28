#Checks if modbus communication works through python
from pymodbus.client.sync import ModbusTcpClient as ModbusClient
from pymodbus.pdu import ExceptionResponse
import xml.etree.ElementTree as ET

class reader:
    def __init__(self, xmlFile):
        """Parses the xml file and creates the reader"""
        self.xml = xmlFile
        self.validateXml()

        parsedData = self._parseXml()

        self.ip = parsedData.get('ip')
        self.port = parsedData.get('port')
        self.registers = parsedData.get('registers')
        self.client = ModbusClient(self.ip, self.port)

    def update(self):
        #Update register values
        if self.client.connect():
            #Input registers
            for ir in self.registers.get('ir'):
                #Request input register data
                try:
                    data = self.client.read_input_registers(address=int(ir.get('register'))-1, count=1)
                    if not isinstance(data, ExceptionResponse):
                        ir['value'] = data.getRegister(0)
                    else:
                        ir['value'] = str(data)
                except Exception as e:
                    ir['value'] = str(e)
                ir['str_repr'] = f"INPUT REGISTER | REGISTER: {int(ir.get('register'))} | DESCRIPTION: {ir.get('description')} | VALUE: {ir.get('value')}"

            #Holding registers
            for hr in self.registers.get('hr'):
                #Request holding register data
                try:
                    data = self.client.read_holding_registers(address=int(hr.get('register'))-1, count=1)
                    if not isinstance(data, ExceptionResponse):
                        hr['value'] = data.getRegister(0)
                    else:
                        hr['value'] = str(data)
                except Exception as e:
                    hr['value'] = str(e)
                hr['str_repr'] = f"HOLDING REGISTER | REGISTER: {int(hr.get('register'))} | DESCRIPTION: {hr.get('description')} | VALUE: {hr.get('value')}"

            #Coils
            for co in self.registers.get('co'):
                #Request coil data
                try:
                    data = self.client.read_coils(address=int(co.get('register'))-1, count=1)
                    if not isinstance(data, ExceptionResponse):
                        co['value'] = data.getBit(0)
                    else:
                        co['value'] = str(data)
                except Exception as e:
                    co['value'] = str(e)
                co['str_repr'] = f"COIL | REGISTER: {int(co.get('register'))} |DESCRIPTION: {co.get('description')} | VALUE: {co.get('value')}"

            #Discrete inputs
            for di in self.registers.get('di'):
                #Request discrete register data
                try:
                    data = self.client.read_discrete_inputs(address=int(di.get('register'))-1, count=1)
                    if not isinstance(data, ExceptionResponse):
                        di['value'] = data.getBit(0)
                    else:
                        di['value'] = str(data)
                except Exception as e:
                    di['value'] = str(e)
                di['str_repr'] = f"DISCRETE INPUT | REGISTER: {int(di.get('register'))} | DESCRIPTION: {di.get('description')} | VALUE: {di.get('value')}"

        else:
            print('Connection failed')

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
        diNode = registers.find('di')
        if diNode != None:
            for mapping in diNode.findall('mapping'):
                mapDict = mapping.attrib
                mapDict['value'] = 0
                di.append(mapDict)

        #Input registers (analogs)
        ir = []
        irNode = registers.find('ir')
        if irNode != None:
            for mapping in irNode.findall('mapping'):
                mapDict = mapping.attrib
                mapDict['value'] = 0
                ir.append(mapDict)

        #Holding registers (analogs)
        hr = []
        hrNode = registers.find('hr')
        if hrNode != None:
            for mapping in hrNode.findall('mapping'):
                mapDict = mapping.attrib
                mapDict['value'] = 0
                hr.append(mapDict)

        #Coils (booleans)
        co = []
        coNode = registers.find('co')
        if coNode != None:
            for mapping in coNode.findall('mapping'):
                mapDict = mapping.attrib
                mapDict['value'] = 0
                co.append(mapDict)

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

    def connect(self):
        return self.client.connect()

    def write_coil(self, register, value):
        if self.connect():
            if value > 1:
                value = 1
            self.client.write_coil(address=register-1, value=value)
    
    def write_register(self, register, value):
        if self.connect():
            self.client.write_register(address=register-1, value=value)


####MAIN APP#######
if __name__ == '__main__': 
    reader = reader(r'client_server_signals.xml')
    reader.update()

    import json
    data = reader.registers
    with open(r'testdata.json', 'w') as f:
        f.write(json.dumps(data, indent=4))


