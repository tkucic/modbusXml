# AUTO CLIENT SERVER FOR MODBUS TCP

![alt text][screen]

This program uses pyModbus package to implement a Modbus TCP client class, gui for that client and a server. Configuration of client and the server can be done from the register and device configuration xml. The user of the program just needs to modify the xml file and run the server and gui.

## Problem that is being solved


## Description of configuration xml file

```xml
<?xml version="1.0" encoding="utf-8"?>
<project>
    <deviceData 
        vendorName = "TkAutomation"
        productCode = ""
        vendorUrl = "https://github.com/tkucic/autoClientServer_modbusTcp"
        productName = "CLIENT/SERVER SIMULATOR FOR MODBUS TCP"
        modelName = "SERVER SIMULATOR FOR MODBUS TCP"
        version = "0.0-1"
        ip = "localhost"
        port = "502"
    />
    <!-- GUIDE ON XML SCHEMA
    If server simulator is parsing this file:
        register.xx startingRegister attribute must be present
        register.xx.mapping initialValue attribuite is optional and will initialize the register if present
    If client is parsing this file:
        register.xx.mapping description attribute must be present
        register.xx.mapping register attribuite must be present and match servers address of this value. It also must be unique, cant have co and di have same register number-->
    <registers>
        <!--Coils-->
        <co startingRegister="100">
            <mapping description="Coil #1" register="100" initialValue="0" />
            .
            .
        </co>
        <!--Discrete inputs-->
        <di startingRegister="1000">
            <mapping description="Discrete input #1" register="1000" initialValue="0" />
            .
            .
        </di>
        <!--Input registers-->
        <ir startingRegister="10000">
            <mapping description="Input register #1" register="10000" initialValue="1000" />
            .
            .
        </ir>-->
        <!--Holding registers-->
        <hr startingRegister="20000" >
            .
            .<mapping description="Holding register #1" register="20000" initialValue="100" />
        </hr>
    </registers>
</project>
```

## Client

Client will read the given xml file, validate it and create internal model for each register mapped in the xml file. If the parsing has been completed succesfully the user has the ability to update the register values by using the update method. From there, the user can iterate over the returned array and find the wanted registers.

## Server

Server will read the given xml file, validate it and create and internal model for each register mapped in the xml file. If the parsing has been completed succesfullt the server will start serving automatically. The server is designed to be run from a terminal. PyModbus debugging logger has been turned on so the server will print out to the terminal each operation it recieves.
If the increment option has been enabled in the server, all of the registers will increment on the given cycle.

## GUI

GUI automates a lot of the features to provide a consistant and simple usage.

### Automatic refresh of the data

Based on the configured registers it will automatically refresh the data and display the register values in the GUI. Cycle time can be modified in the gui.py file at the bottom.
Register information available:
Type - Coil, Discrete input, Input register, Holding register
Register - Actual register being read 0-65535
Value - unsigned integer value of the register
Description - Optional register description read from the xml file

### Writing to the server

The GUI provides four slots for writing either a coil or a holding register with data. The operator can write to a register only once or cyclically. On top of that, if the increment checkbox is selected, the GUI will increment the register value by 1 every cycle. If a wrong register or data is inputted, the GUI will write the exception message to the register value field so the user knows the write didnt go through.

## Requirements

- pymodbus

[screen]: https://github.com/tkucic/autoClientServer_modbusTcp/screenshot.png "Client and server screen shot"
