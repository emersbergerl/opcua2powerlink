# opcua2powerlink

opcua2powerlink is an open source gateway using OPC UA (OPC Unified Architecture) and the industrial real-time fieldbus protocol POWERLINK for data communication from OT (operation technology) to IT (information technology)
The program is usable with all major compilers and provides necessary tools for a fast development process. Currently it is planned that the tool will support both Windows and Linux operation systems.
In the first version only the Windows version is available, the linux version will be available within the next 2 weeks.

opcua2powerlink is based on the open source free implementation of the OPC UA open62541 library (http://open62541.org) and the open source implementation of POWERLINK (http://openpowerlink.sourceforge.net/web/).

## Project Information

### Dependencies

- [open62541](http://open62541.org) OPC UA library
- [openPOWERLINK](http://openpowerlink.sourceforge.net/web/) stack
- Building and Code Generation: The build environment is generated via CMake. Some code and files are auot-generated. The code generation scripts run with both Python 2 and 3.

### Features

- Out of the Box dynamic OPC UA to POWERLINK gateway solution, Creates the required configuration and source files based on the POWERLINK device description file (xdd) during CMake
* Automatically creation of OPC UA nodeset.xml file based on POWERLINK device description file (xdd) during CMake
* Automatically creation of POWERLINK objdict.h file based on xdd file during CMake
* Automatically creation of source files for creating the OPC UA Server with tags from the xdd file during CMake
* Fully functional openPOWERLINK Slave (CN) device

### Requirements

* An POWERLINK master ([openPOWERLINK](http://openpowerlink.sourceforge.net/web/), [B&R](https://www.br-automation.com/),...) is required for controlling the  opcua2powerlink slave device
* An OPC UA Client program is required for connecting to the OPC UA Server

### Documentation and Support

A general introduction to OPC UA and the open62541 documentation can be found at http://open62541.org/doc/current also the general introduction to POWERLINK and the stack documentation can be found at http://openpowerlink.sourceforge.net/web/

For discussion and support the following channel is available:

- the [issues](https://github.com/emersbergerl/opcua2powerlink/issues)

	
## Building

### Building Application

The following section describes how the delivered application can be built. The demo application is located inside the __<src>/opcua2powerlink/ directory.
The default binary installation path is: <opcua2powerlink>/bin/<platform>/<ARCH>

#### Building on Linux

```
> cd <opcua2powerlink>/build/linux
> cmake ../..
> make
> make install
```

#### Build on Windows

Open a Visual Studio command line and enter the following commands:

```
> cd <opcua2powerlink>\build\windows
> cmake -G"NMake Makefiles" ..\..
> nmake
> nmake install
```

__NOTE:__ You can also generate a Visual Studio Solution and compile the libraries in Visual Studio. Please refer to the CMAKE documentation for generating Visual Studio solution files.

#### Configuration Options

##### Generic Options

* __CFG_DEBUG_LVL__

	Debug level to be used for openPOWERLINK debugging functions.

* __CMAKE_INSTALL_PREFIX__

	Specifies the installation directory where your files will be installed. Default directory is: <opcua2powerlink>/bin/<platform>/<ARCH>

* __CMAKE_BUILD_TYPE__

	Specifies your build type. Valid build types are: Debug, Release
	If the build type Debug is specified, the code is compiled with debugging options.

* __CFG_BUILD_KERNEL_STACK__

	Determines how to build the kernel stack. Depending on your system and architecture different options may be available. Please refer to the platform specific options.

* __OPCUA_NAMESPACE__

	Defines the OPC UA namespace name which the gateway should use. Default name is 
	(http://opcua2powerlink.org/demo/)

* __XDD__
	
	Select the POWERLINK device description file (xdd) which should be used. The xdd file describes the Input's and Output's which are available for the device via POWERLINK.
	The project contains the [default xdd file](https://github.com/emersbergerl/opcua2powerlink/master/common/objdicts/CiA401_CN/00000000_POWERLINK_CiA401_CN.xdd) used by the openPOWERLINK stack. 
	
* __PYTHON_EXECUTABLE__
	
	Path to the python executable which should be used for the project.
	
##### Linux Specific Options

* __CFG_BUILD_KERNEL_STACK__

	Determines how to build the kernel stack. The following options are available:

	* __Link to Application__
	
		The openPOWERLINK kernel part will be directly linked to the user part and application. libpcap will be used as Ethernet driver.

	* __Linux Userspace Daemon__
	
		The library __liboplkappXn-userintf.a__ will be used. It contains the interface to a Linux user space daemon. The kernel part of the openPOWERLINK stack is located in the separate user space daemon driver.
		
	* __Linux Kernel Module__
	
		The library __liboplkappXn-kernelintf.a__ will be used. It contains the interface to a Linux kernel module. The kernel part of the openPOWERLINK stack is located in the separate kernel module driver.

### Building Drivers

For highest performance in linux systems with the POWERLINK Slave (CN) the option to build a seperate driver using kernel and PCAP User Space Daemon is possible.
The drivers are located in the directory __drivers__. To build a driver, the following steps are required.
	
__NOTE:__ You don't need to compile a driver if you are using a single process solution. (e.q. Linux/Windows "Link to Application")
	
#### Building a Linux PCAP User Space Daemon

To build an user space daemon:
	
```
> cd <opcua2powerlink_dir>/drivers/linux/drv_daemon_pcap/build
> cmake ..
> make
> make install
```

Sucessfull installation will create an executable inside the <opcua2powerlink_dir>/bin/<platform>/<ARCH>/oplk-pcap.

#### Building a Linux Edrv Kernel Drivers

To build the kernel driver(e.g for a CN using the intel 82753 network interface):

```
> cd <opcua2powerlink_dir>/drivers/linux/drv_kernelmod_edrv/build
> cmake -DCFG_POWERLINK_EDRV_82573=TRUE ..
> make
> make install
```

Sucessfull installation will create an executable inside the <opcua2powerlink_dir>/bin/<platform>/<ARCH>/oplk-edrv.

##### CMake Configuration Options

* __CFG_POWERLINK_EDRV_<driver name>__

	Selects the Ethernet driver used for the kernel-based application. Valid options are:
	* __8139:__ Realtek 8139-based network interface cards (100 MBit/s)
	* __8111:__ Realtek 8111/8168 network interface cards (1 GBit/s)
	* __8255x:__ Intel 8255x-based network interface cards (100 MBit/s)
	* __82573:__ Intel Gigabit network interface cards (1 GBit/s) (supported chipsets: 82573L, 82567V, 82583V, 82567LM, 82574L, 82540EM)
	* __i210:__ Intel I210-based network interface cards (1 GBit/s)

## InProgress
* __Improve Documentation__
* __Enhance functionality__

## Examples

Overview of the default tags available via OPC UA from the opcua2powerlink tool.
Some of the values are written by an POWERLINK master and forwarded to the OPC UA Server.

![image](tools/pictures/UaExpert.png)

