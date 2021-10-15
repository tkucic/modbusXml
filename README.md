# Modbus XML

![alt text][screen]

These programs use pyModbus package to implement a Modbus client class, GUI for that client and a server. Configuration of client and the server can be done from the register and device configuration xml. The user of the program just needs to modify the xml file and run the server and GUI.

## Problem that is being solved

In R&D we often need to develop interfaces for our devices and controllers. If we are integrating existing devices into our control system we also need to communicate with those devices. Often, Modbus gets chosen to be the working interface for its reliability and overall experience of the service engineers and developers. Modbus is also quite a defined interface which means we do not necessarilly need a PLC or an embedded device to acomplish this interface. We can use our regular laptops and PCs. With the power of Python and PyModbus library we can run a Modbus client and/or a server independent on what OS we are running. Python runs on Windows, MacOS and Linux and this program was even tested on a Raspbian running on Raspberry PI 3B+.

In Modbus, we have a client(master)/server(slave) architecture which means we need two computers running either a client or a server. Some of the example configurations that we can test with this program are described in the headings below.

Usually to implement a modbus interface we need a mapping file. This mapping file can come in many formats but its contents are simple. Registers thatare available and their location in the modbus memory address. This program is using XML technology to standardize these various formats. As a user of this program you are required to build that XML file from the modbus interface list.

### PLC running a client - local PC/Laptop/Raspberry running a server

![alt text][plc-pc]

If we are developing a client that interfaces with a server, we often do not have the actual device present which makes the development process a kind of a black box process. The developer must trust the modbus interface list to implement the interface and it usually tested the first time that real device is connected. Which often means during commissionings. During development we can initialize this program with the interface list of that device and run the server simulator. This way we can continuously test our interface. So, our real PLC will implement the client interface we are developing and it will poll our simulated server.

### PC/Laptop/Raspberry running a client - PLC running a server

![alt text][pc-plc]

Similarly to the PLC Client - Simulator server example above, we can implement a client with this program. Our PLC is implementing the Modbus server and this program is polling the PLC to get the wanted data. We can even send commands from the client to the real PLC.

### PC/Laptop/Raspberry running the client and server

If we do not have any embedded device, we can still develop the modbus interfaces. For example if the interface developer is making the both interfaces, we can run the client and server on the same machine, modify easily the registers and the descriptions, check for usability of the interface and easily export the xml file to the developers of those embedded devices. Sometimes it is hard to change these interfaces on two embedded machines that have reached production status. In order to prove the benefits of the new interface or the interface changes, this program can be used just for that.

### Multi server configurations

![alt text][manyPc]

If we run multiple servers on the PC, the same or multiple devices, those devices will answer if a client is polling them. In this way we can test whole systems before we reach commissioning or lab testing.

## Installation

Clone/download this repository

Install pyModbus with command "python pip install pymodbus"

## Requirements

- Python 3+
- pymodbus

## Description of configuration xml file

```xml
<?xml version="1.0" encoding="utf-8"?>
<project>
    <deviceData 
        vendorName = "TkAutomation"
        productCode = ""
        vendorUrl = "https://github.com/tkucic/autoClientServer_modbusTcp"
        productName = "EASY CLIENT/SERVER SIMULATOR FOR MODBUS TCP/RTU"
        modelName = "SERVER SIMULATOR FOR MODBUS TCP/RTU"
        version = "1.0-0"
        modbusType = "tcp/ip"
        timeout = "2"
        ip = "localhost"
        port = "502"
        com = "COM2"
        baud = "19200"
        stopbits = "1"
        bytesize = "8"
        parity = "E"
        log = "partial"
    />
    <!-- GUIDE ON XML SCHEMA
    If server simulator is parsing this file:
        register.xx.mapping register attribute must be present
        register.xx.mapping initialValue attribuite is optional and will initialize the register if present
        all number values must be integer 0-65535
    If client is parsing this file:
        register.xx.mapping description attribute is optional but if missing the GUI will show None for the description
        register.xx.mapping register attribuite must be present and match servers address of this value. It also must be unique, cant have co and di have same register number
        all number values must be integer 0-65535-->
    <registers>
        <!--Coils-->
        <co>
            <mapping description="Coil #1" register="100" initialValue="0" log="True" />
            .
            .
        </co>
        <!--Discrete inputs-->
        <di>
            <mapping description="Discrete input #1" register="1000" initialValue="0" log="True" />
            .
            .
        </di>
        <!--Input registers-->
        <ir>
            <mapping description="Input register #1" register="10000" initialValue="1000" log="True" />
            .
            .
        </ir>-->
        <!--Holding registers-->
        <hr>
            .
            .<mapping description="Holding register #1" register="20000" initialValue="100" log="True" />
        </hr>
    </registers>
</project>
```

## TCP/IP or RTU selection

The scripts have RTU and TCP/IP transportation protocols available and can be used by parametrizing the deviceData xml node. Please not that RTU requires a serial com port to be opened and a serial device correctly configured for this to work. To simulate RTU in the same way as TCP/IP for example, a virtual serial com port is needed. Check online to find a suitable virtual com port simulator.

## Client

Client will read the given xml file, validate it and create internal model for each register mapped in the xml file. If the parsing has been completed succesfully the user has the ability to update the register values by using the update method. From there, the user can iterate over the returned array and find the wanted registers.
The client can be ran from the interactive python shell with the example below. The client can be also imported into other python programs.

```python

    >> from client.py import reader
    >> client = reader('path_to_xml_file.xml')
    >> client.connect()
    >> 'True'
    >> client.update_all()
    >> client.xmlData.get('registers').get('di')[0]
    f"DISCRETE INPUT | REGISTER: {int(di.get('register'))} | DESCRIPTION: {di.get('description')} | VALUE: {di.get('value')}"

    >> client.registers.get('hr')
    >> client.registers.get('ir')

```

## Session logging

Client class has the capability to log everything it reads in csv format. To set it up, in the deviceData xml node, if the log="all" or log="partial" atribute should be passed. log="all" attribute logs all mapped register and the log="partial" will log only the register with the log="True" attribute.
The log file is created in the current working directory.

## Server

Server will read the given xml file, validate it and create and internal model for each register mapped in the xml file. If the parsing has been completed succesfullt the server will start serving automatically. The server is designed to be run from a terminal/command line. PyModbus debugging logger has been turned on so the server will print out to the terminal each operation it recieves.

### Options

-i or --increment - Server will increment all of its number registers by 1 and flip bits every cycle
-d or --debug - Server will print out to the terminal every single operation

If the number argument is ommitted then the server uses default cycle time of 1500 ms.

```shell

    python server.py -i -d client_server_signals.xml 1500
    <pyhon> <server.py> <-i> | <--increment> <-d> | <--debug> <path to xml file> <cycle time in ms>

```

## GUI

GUI automates a lot of the features to provide a consistant and simple usage.

### Automatic refresh of the data

Based on the configured registers it will automatically refresh the data and display the register values in the GUI.  
Register information available:  

- Type - Coil, Discrete input, Input register, Holding register  

- Register - Actual register being read 0-65535  

- Value - unsigned integer value of the register  

- Description - Optional register description read from the xml file  

For integer registers like input register and holding register, if the user double clicks on the register line, it will expand to show the 16 bits. This can be used for testing the packed integers.

### Writing to the server

The GUI provides four slots for writing either a coil or a holding register with data. The operator can write to a register only once or cyclically. On top of that, if the increment checkbox is selected, the GUI will increment the register value by 1 every cycle. If a wrong register or data is inputted, the GUI will write the exception message to the register value field so the user knows the write didnt go through.

### Status bar

Status bar is showing the modbus interface type and the used parameters like baud rate and ip address. The latency calculation on the right size is showing how much time is necessary to get all of the defined register value. In translation, how often the data changes.

### Running the GUI

The GUI can be ran from the command line with the example below. If the number argument is ommitted then the server uses default cycle time of 1500 ms.

```shell
    python gui.py client_server_signals.xml 1000
    <python> <gui.py> <path to xml file> <cycle time in ms>
```

## Contributing

Just fork the repo and raise your PR against master branch.

## License Information

These python scripts are built on top of Pymodbus package released under BSD Licence  
[PyModbus License](https://github.com/riptideio/pymodbus/blob/master/LICENSE)  
[PyModbus Homepage](https://github.com/riptideio/pymodbus)  

These scripts are released under the MIT License

[screen]: img/screenshot.png "Client and server screen shot"
[pc-plc]: img/pc-plc.png "Representation of pc communicating with plc over modbus"
[plc-pc]: img/plc-pc.png "Representation of plc communicating with pc over modbus"
[manyPc]: img/manyPc.png "Representation of plc communicating with many pc servers over modbus"
