#Checks if modbus communication works through python
from pymodbus.client.sync import ModbusTcpClient, ModbusSerialClient
from pymodbus.pdu import ExceptionResponse
import xml.etree.ElementTree as ET

def validateXml(file):
    """Validates given xml file and returns a enumeration
    0 - file ok
    -1 - deviceData node missing
    -2 - modbus type not set
    -3 - ip address missing
    -4 - com port missing
    -5 - baud rate missing
    -10 - no register mappings
    -11 - duplicated ir mapping
    -12 - duplicated di mapping
    -13 - duplicated hr mapping
    -14 - duplicated co mapping"""
    tree = ET.parse(file)
    root = tree.getroot()
    #Check if deviceData exists
    try:
        deviceData = root.find('deviceData')
        if deviceData == None:
            return -1
    except:
        return -1

    #Check if modbus type is set
    mdbType = deviceData.get('modbusType')
    if mdbType == None:
        return -2
        
    #Check if tcp/ip is set
    if mdbType == 'tcp/ip':
        if deviceData.get('ip') in [None, '']:
            return -3

    #Check if rtu parameters are set
    if mdbType == 'rtu':
        if deviceData.get('com') in [None, '']:
            return -4
        if deviceData.get('baud') in [None, '']:
            return -5

    #Check for correct register nodes
    registers = root.find('registers')
    if registers == None:
        return -10
    ir_regs = []
    di_regs = []
    hr_regs = []
    co_regs = []
    for register in registers.findall('ir/mapping'):
        if register.get('register') not in ir_regs:
            ir_regs.append(register.get('register'))
        else:
            return -11
    for register in registers.findall('di/mapping'):
        if register.get('register') not in di_regs:
            di_regs.append(register.get('register'))
        else:
            return -12
    for register in registers.findall('hr/mapping'):
        if register.get('register') not in hr_regs:
            hr_regs.append(register.get('register'))
        else:
            return -13
    for register in registers.findall('co/mapping'):
        if register.get('register') not in co_regs:
            co_regs.append(register.get('register'))
        else:
            return -14
    return 0

class reader:
    def __init__(self, xmlFile):
        """Parses the xml file and creates the reader"""
        self.xml = xmlFile
        validationInt = validateXml(self.xml)
        if validationInt == -1: raise Exception('XML File Error: devicData node missing')
        elif validationInt == -2: raise Exception('XML File Error: modbus type not set')
        elif validationInt == -3: raise Exception('XML File Error: ip address missing')
        elif validationInt == -4: raise Exception('XML File Error: comm port missing')
        elif validationInt == -5: raise Exception('XML File Error: baud rate missing')
        elif validationInt == -10: raise Exception('XML File Error: No register mappings')
        elif validationInt == -11: raise Exception('XML File Error: Duplicated Input register mapping')
        elif validationInt == -12: raise Exception('XML File Error: Duplicated Discrete input mapping')
        elif validationInt == -13: raise Exception('XML File Error: Duplicated Holding register mapping')
        elif validationInt == -14: raise Exception('XML File Error: Duplicated Coil mapping')

        self.xmlData = self._parseXml()
        if self.xmlData.get('modbusType') == 'tcp/ip':
            self.client = ModbusTcpClient(self.xmlData.get('ip'), self.xmlData.get('port'), timeout=1)
        elif self.xmlData.get('modbusType') == 'rtu':
            self.client = ModbusSerialClient(method = 'rtu', 
                                            port = self.xmlData.get('com'),
                                            baudrate = self.xmlData.get('baud'),
                                            bytesize = self.xmlData.get('bytesize'),
                                            stopbits = self.xmlData.get('stopbits'),
                                            parity = self.xmlData.get('parity'),
                                            timeout = self.xmlData.get('timeout'),
                                            )

    def update_all(self):
        #Update register values
        if self.client.connect():
            #Input registers
            for ir in self.xmlData.get('registers').get('ir'):
                self.update_reg(ir)
                #ir['str_repr'] = f"INPUT REGISTER | REGISTER: {int(ir.get('register'))} | DESCRIPTION: {ir.get('description')} | VALUE: {ir.get('value')}"

            #Holding registers
            for hr in self.xmlData.get('registers').get('hr'):
                self.update_reg(hr)
                #hr['str_repr'] = f"HOLDING REGISTER | REGISTER: {int(hr.get('register'))} | DESCRIPTION: {hr.get('description')} | VALUE: {hr.get('value')}"

            #Coils
            for co in self.xmlData.get('registers').get('co'):
                self.update_reg(co)
                #co['str_repr'] = f"COIL | REGISTER: {int(co.get('register'))} |DESCRIPTION: {co.get('description')} | VALUE: {co.get('value')}"

            #Discrete inputs
            for di in self.xmlData.get('registers').get('di'):
                self.update_reg(di)
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
                    'type' : 'di',
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
                    'type' : 'ir',
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
                    'type' : 'hr',
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
                    'type' : 'co',
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
        data['modbusType'] = deviceData.get('modbusType')
        data['com'] = deviceData.get("com", None)
        data['baud'] = int(deviceData.get("baud", "9600"))
        data['stopbits'] = int(deviceData.get("stopbits", "1"))
        data['bytesize'] = int(deviceData.get("bytesize", "8"))
        data['parity'] = deviceData.get("parity", "E")
        data['ip'] = deviceData.get("ip", "localhost")
        data['port'] = int(deviceData.get("port", 502))
        data['timeout'] = int(deviceData.get('timeout', "2"))

        return data

    def connect(self):
        return self.client.connect()

    def update_reg(self, register):
        try:
            if register.get('type') == 'di':
                data = self.client.read_discrete_inputs(address=register.get('register'), count=1)
                if not isinstance(data, ExceptionResponse):
                    register['value'] =  data.getBit(0)
                else:
                    register['value'] =   str(data)
        
            elif register.get('type') == 'co':
                data = self.client.read_coils(address=register.get('register'), count=1)
                if not isinstance(data, ExceptionResponse):
                    register['value'] =   data.getBit(0)
                else:
                    register['value'] =    str(data)

            elif register.get('type') == 'ir':
                
                data = self.client.read_input_registers(address=register.get('register'), count=1)
                if not isinstance(data, ExceptionResponse):
                    register['value'] = data.getRegister(0)
                else:
                    register['value'] =  str(data)

            elif register.get('type') == 'hr':
                
                data = self.client.read_holding_registers(address=register.get('register'), count=1)
                if not isinstance(data, ExceptionResponse):
                    register['value'] = data.getRegister(0)
                else:
                    register['value'] =  str(data)
        except Exception as e:
            register['value'] =  str(e) + ' ' + str(data)
            
    def get_ir(self, register):
        #gets the value of the register, regardless if it exists
        if self.connect():
            try:
                data = self.client.read_input_registers(address=register, count=1)
                if not isinstance(data, ExceptionResponse):
                    return data.getRegister(0)
                else:
                    return  str(data)
            except Exception as e:
                return str(e) + str(data)

    def get_hr(self, register):
        #gets the value of the register, regardless if it exists
        if self.connect():
            try:
                data = self.client.read_holding_registers(address=register, count=1)
                if not isinstance(data, ExceptionResponse):
                    return data.getRegister(0)
                else:
                    return  str(data)
            except Exception as e:
                return str(e) + str(data)

    def get_di(self, register):
        #gets the value of the register, regardless if it exists
        if self.connect():
            try:
                data = self.client.read_discrete_inputs(address=register, count=1)
                if not isinstance(data, ExceptionResponse):
                    return data.getBit(0)
                else:
                    return  str(data)
            except Exception as e:
                return str(e) + ' ' + str(data)

    def get_co(self, register):
        #gets the value of the register, regardless if it exists
        if self.connect():
            try:
                data = self.client.read_coils(address=register, count=1)
                if not isinstance(data, ExceptionResponse):
                    return data.getBit(0)
                else:
                    return  str(data)
            except Exception as e:
                return str(e) + ' ' + str(data)

    def write_coil(self, register, value):
        if self.connect():
            if value > 1:
                value = 1
            return self.client.write_coil(address=register, value=value)

    def write_register(self, register, value):
        if self.connect():
            return self.client.write_register(address=register, value=value)
