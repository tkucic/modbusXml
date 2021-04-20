#Checks if modbus communication works through python
from pymodbus.client.sync import ModbusTcpClient as ModbusClient
from pymodbus.pdu import ExceptionResponse
import xml.etree.ElementTree as ET

def validateXml(file):
    """Validates given xml file and returns a enumeration
    0 - file ok
    -1 - ip address missing
    -2 - no register mappings
    -3 - duplicated ir mapping
    -4 - duplicated di mapping
    -5 - duplicated hr mapping
    -6 - duplicated co mapping"""
    tree = ET.parse(file)
    root = tree.getroot()
    try:
        if root.find('deviceData').get('ip') == None:
            return -1
    except:
        return -1

    registers = root.find('registers')
    if registers == None:
        return -2
    ir_regs = []
    di_regs = []
    hr_regs = []
    co_regs = []
    for register in registers.findall('ir/mapping'):
        if register.get('register') not in ir_regs:
            ir_regs.append(register.get('register'))
        else:
            return -3
    for register in registers.findall('di/mapping'):
        if register.get('register') not in di_regs:
            di_regs.append(register.get('register'))
        else:
            return -4
    for register in registers.findall('hr/mapping'):
        if register.get('register') not in hr_regs:
            hr_regs.append(register.get('register'))
        else:
            return -5
    for register in registers.findall('co/mapping'):
        if register.get('register') not in co_regs:
            co_regs.append(register.get('register'))
        else:
            return -6
    return 0

class reader:
    def __init__(self, xmlFile):
        """Parses the xml file and creates the reader"""
        self.xml = xmlFile
        validationInt = validateXml(self.xml)
        if validationInt == -1: raise Exception('XML File Error: IP address missing')
        elif validationInt == -2: raise Exception('XML File Error: No register mappings')
        elif validationInt == -3: raise Exception('XML File Error: Duplicated Input register mapping')
        elif validationInt == -4: raise Exception('XML File Error: Duplicated Discrete input mapping')
        elif validationInt == -5: raise Exception('XML File Error: Duplicated Holding register mapping')
        elif validationInt == -6: raise Exception('XML File Error: Duplicated Coil mapping')

        parsedData = self._parseXml()

        self.ip = parsedData.get('ip')
        self.port = parsedData.get('port')
        self.registers = parsedData.get('registers')
        self.client = ModbusClient(self.ip, self.port, timeout=1)

    def update(self):
        #Update register values
        if self.client.connect():
            #Input registers
            for ir in self.registers.get('ir'):
                #Request input register data
                try:
                    data = self.client.read_input_registers(address=ir.get('register'), count=1)
                    if not isinstance(data, ExceptionResponse):
                        ir['value'] = data.getRegister(0)
                    else:
                        ir['value'] = str(data)
                except Exception as e:
                    ir['value'] = str(e)
                #ir['str_repr'] = f"INPUT REGISTER | REGISTER: {int(ir.get('register'))} | DESCRIPTION: {ir.get('description')} | VALUE: {ir.get('value')}"

            #Holding registers
            for hr in self.registers.get('hr'):
                #Request holding register data
                try:
                    data = self.client.read_holding_registers(address=hr.get('register'), count=1)
                    if not isinstance(data, ExceptionResponse):
                        hr['value'] = data.getRegister(0)
                    else:
                        hr['value'] = str(data)
                except Exception as e:
                    hr['value'] = str(e)
                #hr['str_repr'] = f"HOLDING REGISTER | REGISTER: {int(hr.get('register'))} | DESCRIPTION: {hr.get('description')} | VALUE: {hr.get('value')}"

            #Coils
            for co in self.registers.get('co'):
                #Request coil data
                try:
                    data = self.client.read_coils(address=co.get('register'), count=1)
                    if not isinstance(data, ExceptionResponse):
                        co['value'] = data.getBit(0)
                    else:
                        co['value'] = str(data)
                except Exception as e:
                    co['value'] = str(e)
                #co['str_repr'] = f"COIL | REGISTER: {int(co.get('register'))} |DESCRIPTION: {co.get('description')} | VALUE: {co.get('value')}"

            #Discrete inputs
            for di in self.registers.get('di'):
                #Request discrete register data
                try:
                    data = self.client.read_discrete_inputs(address=di.get('register'), count=1)
                    if not isinstance(data, ExceptionResponse):
                        di['value'] = data.getBit(0)
                    else:
                        di['value'] = str(data)
                except Exception as e:
                    di['value'] = str(e)
                #di['str_repr'] = f"DISCRETE INPUT | REGISTER: {int(di.get('register'))} | DESCRIPTION: {di.get('description')} | VALUE: {di.get('value')}"

        else:
            print('Connection failed')

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
                mapDict = {
                    'register' : int(mapping.get('register')),
                    'description' : mapping.get('description', '-'),
                    'value' : 0
                }
                di.append(mapDict)

        #Input registers (analogs)
        ir = []
        irNode = registers.find('ir')
        if irNode != None:
            for mapping in irNode.findall('mapping'):
                mapDict = {
                    'register' : int(mapping.get('register')),
                    'description' : mapping.get('description', '-'),
                    'bit0' : mapping.get('bit0', '-'),
                    'bit1' : mapping.get('bit1', '-'),
                    'bit2' : mapping.get('bit2', '-'),
                    'bit3' : mapping.get('bit3', '-'),
                    'bit4' : mapping.get('bit4', '-'),
                    'bit5' : mapping.get('bit5', '-'),
                    'bit6' : mapping.get('bit6', '-'),
                    'bit7' : mapping.get('bit7', '-'),
                    'bit8' : mapping.get('bit8', '-'),
                    'bit9' : mapping.get('bit9', '-'),
                    'bit10' : mapping.get('bit10', '-'),
                    'bit11' : mapping.get('bit11', '-'),
                    'bit12' : mapping.get('bit12', '-'),
                    'bit13' : mapping.get('bit13', '-'),
                    'bit14' : mapping.get('bit14', '-'),
                    'bit15' : mapping.get('bit15', '-'),
                    'value' : 0
                }
                ir.append(mapDict)

        #Holding registers (analogs)
        hr = []
        hrNode = registers.find('hr')
        if hrNode != None:
            for mapping in hrNode.findall('mapping'):
                mapDict = {
                    'register' : int(mapping.get('register')),
                    'description' : mapping.get('description', '-'),
                    'bit0' : mapping.get('bit0', '-'),
                    'bit1' : mapping.get('bit1', '-'),
                    'bit2' : mapping.get('bit2', '-'),
                    'bit3' : mapping.get('bit3', '-'),
                    'bit4' : mapping.get('bit4', '-'),
                    'bit5' : mapping.get('bit5', '-'),
                    'bit6' : mapping.get('bit6', '-'),
                    'bit7' : mapping.get('bit7', '-'),
                    'bit8' : mapping.get('bit8', '-'),
                    'bit9' : mapping.get('bit9', '-'),
                    'bit10' : mapping.get('bit10', '-'),
                    'bit11' : mapping.get('bit11', '-'),
                    'bit12' : mapping.get('bit12', '-'),
                    'bit13' : mapping.get('bit13', '-'),
                    'bit14' : mapping.get('bit14', '-'),
                    'bit15' : mapping.get('bit15', '-'),
                    'value' : 0
                }
                hr.append(mapDict)

        #Coils (booleans)
        co = []
        coNode = registers.find('co')
        if coNode != None:
            for mapping in coNode.findall('mapping'):
                mapDict = {
                    'register' : int(mapping.get('register')),
                    'description' : mapping.get('description', '-'),
                    'value' : 0
                }
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
            return self.client.write_coil(address=register, value=value)

    def write_register(self, register, value):
        if self.connect():
            return self.client.write_register(address=register, value=value)
