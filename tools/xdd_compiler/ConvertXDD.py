#!/usr/bin/env python
# -*- coding: utf-8 -*-

###
### Authors:
### - Lukas Emersberger (lukas.emersberger@gmail.com)
###
### This program was created for automatically creating
### source files from the input xdd file.
###
### This program is not meant to be used in a production environment. The
### author is not liable for any complications arising due to the use of
### this program.
###

import os
import sys
import xml.etree.ElementTree as ET
import logging

class ConvertXDD:

    #Create logger
    logging.basicConfig(level=logging.ERROR)
    logger = logging.getLogger(__name__)

    # Type defines
    object_dict_types = {
        '0001': ['kObdTypeBool', 'tObdBoolean', '0x00'],
        '0002': ['kObdTypeInt8', 'tObdInteger8', '0x00'],
        '0003': ['kObdTypeInt16', 'tObdInteger16', '0x0000'],
        '0004': ['kObdTypeInt32', 'tObdInteger32', '0x00000000'],
        '0005': ['kObdTypeUInt8', 'tObdUnsigned8', '0x00'],
        '0006': ['kObdTypeUInt16', 'tObdUnsigned16', '0x0000'],
        '0007': ['kObdTypeUInt32', 'tObdUnsigned32', '0x00000000'],
        '0008': ['kObdTypeReal32', 'tObdReal32', '0x00000000'],
        '0009': ['kObdTypeVString', 'tObdVString', '0x00'],
        '000A': ['kObdTypeOString', 'tObdOString', '0x00']
    }

    # POWERLINK data types
    oplk_types = {
        '0001': 'BOOLEAN',
        '0002': 'INT8',
        '0003': 'INT16',
        '0004': 'INT32',
        '0005': 'UINT8',
        '0006': 'UINT16',
        '0007': 'UINT32',
        '0008': 'DOUBLE',
        '0009': 'STRING',
        '000A': 'STRING',
    }

    # POWERLINK data types reversed
    oplk_types_reverse = {
        'BOOLEAN': '0001',
        'INT8': '0002',
        'INT16': '0003',
        'INT32': '0004',
        'UINT8': '0005',
        'UINT16': '0006',
        'UINT32': '0007',
        'DOUBLE': '0008',
        'STRING': '0009',
        'STRING': '000A',
    }

    # OPC UA data types
    opcua_types = {
        '0001': ['Boolean', '1'],
        '0002': ['SByte', '2'],
        '0003': ['Int16', '4'],
        '0004': ['Int32', '6'],
        '0005': ['Byte', '3'],
        '0006': ['UInt16', '5'],
        '0007': ['UInt32', '7'],
        '0008': ['Float', '10'],
        '0009': ['String', '12'],
        '000A': ['String', '12']
    }

    # OPC UA data types reversed
    opcua_data_types = {
        '0001': ['UA_Boolean', 'UA_TYPES_BOOLEAN'],
        '0002': ['UA_SByte', 'UA_TYPES_SBYTE'],
        '0003': ['UA_Int16', 'UA_TYPES_INT16'],
        '0004': ['UA_Int32', 'UA_TYPES_INT32'],
        '0005': ['UA_Byte', 'UA_TYPES_BYTE'],
        '0006': ['UA_UInt16', 'UA_TYPES_UINT16'],
        '0007': ['UA_UInt32', 'UA_TYPES_UINT32'],
        '0008': ['UA_Float', 'UA_TYPES_FLOAT'],
        '0009': ['UA_String', 'UA_TYPES_STRING'],
        '000A': ['UA_String', 'UA_TYPES_STRING'],
    }

    # Initialize the Class
    def __init__(self, directory, link, xdd):
        # Check if the xdd file exists
        if not os.path.isfile(xdd):
            self.logger.error("No xdd file was found!")
            sys.exit(-1)
        # Parse the .xdd file
        self.tree = ET.parse(xdd)
        # Get the root of the .xdd file
        self.root = self.tree.getroot()
        # Check if the namespace link was defined
        if link == "":
            self.logger.error("No opc ua namespace link defined!")
            sys.exit(-1)
        self.link = link
        self.oplk_elements = None
        self.oplk_tags = None
        # Check if the cmake root directory was defined
        if directory == "":
            self.logger.error("No cmake root directory defined!")
            sys.exit(-1)
        self.directory = directory
        self.standardised = list()
        self.manufacturer = list()

    # Get the List with all the defined Objects from the .xdd files
    def create_oplk_elements(self):
        for item in self.root[1]:
            if "ProfileBody" in str(item):
                for layer in item:
                    if "ApplicationLayers" in str(layer):
                        for object_list in layer:
                            if "ObjectList" in str(object_list):
                                self.oplk_elements = object_list
                                break

    # Get the defined and Standardized Input and Output values
    def create_oplk_tags(self):

        manufacturer_obj = list()
        standardized_obj = list()

        if self.oplk_elements is None:
            if not self.root:
                self.logger.error('There is no xml root defined!')
                sys.exit(-1)
            else:
                self.logger.info('Creating POWERLINK elements!')
                self.create_oplk_elements()

        for obj in self.oplk_elements:
            if int('0x' + obj.attrib['index'], 0) >= 8192 and int('0x' + obj.attrib['index'], 0) <= 24575:
                manufacturer_obj.append(obj)
            elif int('0x' + obj.attrib['index'], 0) >= 24576 and int('0x' + obj.attrib['index'], 0) <= 40959:
                standardized_obj.append(obj)

        objects = {'Manufacturer': manufacturer_obj, 'Standardised': standardized_obj}
        self.oplk_tags = objects

    # Create a list with all the available variables
    def create_variables(self):

        self.standardised = list()
        self.manufacturer = list()

        if not self.oplk_tags:
            if self.root is None:
                self.logger.error("There is no xml root defined!")
                return -1
            if not self.oplk_elements:
                self.create_oplk_elements()
                self.create_oplk_tags()
                self.logger.info("The POWERLINK elements and tags were not created. Creating tags!")
            else:
                if not self.oplk_tags:
                    self.create_oplk_tags()
                    self.logger.info("The POWERLINK tags were not created. Creating tags!")

        for item in iter(self.oplk_tags['Manufacturer']):
            # Get the length of the object
            length = len(item.attrib)
            item_name = item.attrib['name']
            # Array type
            if length < 5:
                index = item.attrib['index']
                obj_nr = 0
                for element in item:
                    tmp = {}
                    # Check if it's the 'NumberOfEntries' object
                    if element.attrib['name'] == 'NumberOfEntries':
                        obj_nr = int(element.attrib['defaultValue'])
                    else:
                        tmp.update({'index': index})
                        tmp.update({'ObjectName': item_name})
                        tmp.update({'Objects': obj_nr})
                        tmp.update({'type': 1})
                        tmp.update({'subIndex': element.attrib['subIndex']})
                        tmp.update({'name': element.attrib['name']})
                        tmp.update({'dataType': element.attrib['dataType']})
                        tmp.update({'accessType': element.attrib['accessType']})
                        self.manufacturer.append(tmp)
            else:
                index = item.attrib['index']
                tmp = {}
                tmp.update({'index': index})
                tmp.update({'type': 0})
                tmp.update({'name': item.attrib['name']})
                tmp.update({'dataType': item.attrib['dataType']})
                tmp.update({'accessType': item.attrib['accessType']})
                self.manufacturer.append(tmp)

        for item in iter(self.oplk_tags['Standardised']):
            # Get the length of the object
            length = len(item.attrib)
            item_name = item.attrib['name']
            # Array type
            if length < 5:
                index = item.attrib['index']
                obj_nr = 0
                for element in item:
                    tmp = {}
                    # Check if it's the 'NumberOfEntries' object
                    if element.attrib['name'] == 'NumberOfEntries':
                        obj_nr = int(element.attrib['defaultValue'])
                    else:
                        tmp.update({'index': index})
                        tmp.update({'ObjectName': item_name})
                        tmp.update({'Objects': obj_nr})
                        tmp.update({'type': 1})
                        tmp.update({'subIndex': element.attrib['subIndex']})
                        tmp.update({'name': element.attrib['name']})
                        tmp.update({'dataType': element.attrib['dataType']})
                        tmp.update({'accessType': element.attrib['accessType']})
                        self.standardised.append(tmp)
            else:
                index = item.attrib['index']
                tmp = {}
                tmp.update({'index': index})
                tmp.update({'type': 0})
                tmp.update({'name': item.attrib['name']})
                tmp.update({'dataType': item.attrib['dataType']})
                tmp.update({'accessType': item.attrib['accessType']})
                self.standardised.append(tmp)

    # Creates the objdict.h file inside the /common/objdicts/CiA401_CN folder
    def create_objdict(self):

        if not self.oplk_tags:
            if self.root is None:
                self.logger.error("There is no xml root defined!")
                sys.exit(-1)
            if not self.oplk_elements:
                self.create_oplk_elements()
            self.create_oplk_tags()
            self.logger.info("Creating POWERLINK tags!")

        header_file = self.directory + "/tools/schema/objdict.h"

        if not os.path.isfile(header_file):
            self.logger.info("The file doesn't exist")
            return -1

        with open(header_file, 'r') as f:
            header = f.readlines()

        # Manufacturer data
        header.append("\n")
        header.append("    /*************************************************************************\n")
        header.append("     * Manufacturer Specific Profile Area (0x2000 - 0x5FFF)\n")
        header.append("     *************************************************************************/\n")
        header.append("    OBD_BEGIN_PART_MANUFACTURER()\n")
        header.append("\n")

        self.create_variables()

        if not self.manufacturer:
            pass
        else:
            last_index = '0'
            first_index = 1
            for item in iter(self.manufacturer):
                # Array Type
                if item['type'] == 1:
                    if last_index != item['index']:
                        if first_index:
                            first_index = 0

                            header.append("\n")
                            header.append("        OBD_BEGIN_INDEX_RAM(0x%s" % item['index'] +
                                          ", 0x{0:02x}, FALSE)\n".format(int(item['Objects']) + 1))
                            header.append("            OBD_SUBINDEX_RAM_VAR(0x%s, 0x00, kObdTypeUInt8," % item['index'] +
                                          "kObdAccConst, tObdUnsigned8, NumberOfEntries" +
                                          ", 0x{0:02x})\n".format(int(item['Objects'])) % ())
                            last_index = item['index']
                        else:
                            header.append("        OBD_END_INDEX(0x%s)\n" % last_index)
                            header.append("\n")
                            header.append("        OBD_BEGIN_INDEX_RAM(0x%s" % item['index'] +
                                          ", 0x{0:02x}, FALSE)\n".format(int(item['Objects'])))
                            header.append("            OBD_SUBINDEX_RAM_VAR(0x%s, 0x00, kObdTypeUInt8," % (item['index']) +
                                          " kObdAccConst, tObdUnsigned8, NumberOfEntries" +
                                          ", 0x{0:02x})\n".format(int(item['Objects'])))
                            last_index = item['index']

                    odb_type = self.object_dict_types[item['dataType']]
                    odb_acc = 'kObdAccVPR' if item['accessType'] == 'ro' else 'kObdAccVPRW'

                    header.append("            OBD_SUBINDEX_RAM_USERDEF(0x%s" % item['index'] +
                                  ", 0x{0:02x}".format(int(item['subIndex'])) +
                                  ", %s, %s, %s, %s, %s)\n" % (
                                odb_type[0], odb_acc, odb_type[1], item['name'], odb_type[2]))

                # Single Type
                else:
                    if last_index != item['index']:
                        if first_index:
                            first_index = 0

                            header.append("\n")
                            header.append("        OBD_BEGIN_INDEX_RAM(0x%s, 0x01, FALSE)\n" % item['index'])
                            last_index = item['index']
                        else:
                            header.append("        OBD_END_INDEX(0x%s)\n" % last_index)
                            header.append("\n")
                            header.append("        OBD_BEGIN_INDEX_RAM(0x%s, 0x01, FALSE)\n" % item['index'])
                            last_index = item['index']

                        odb_type = self.object_dict_types[item['dataType']]
                        odb_acc = 'kObdAccVPR' if item['accessType'] == 'ro' else 'kObdAccVPRW'

                        header.append("            OBD_SUBINDEX_RAM_VAR(0x%s, 0x00, %s, %s, %s, %s, %s)\n" % (
                                    item['index'], odb_type[0], odb_acc, odb_type[1], item['name'], odb_type[2]))

                header.append("        OBD_END_INDEX(0x%s)\n" % last_index)
                header.append("\n")
        header.append("    OBD_END_PART()\n")

        # Standardized devices header
        header.append("    /*************************************************************************\n")
        header.append("     * Standardised Device Profile Area (0x6000 - 0x9FFF)\n")
        header.append("     *************************************************************************/\n")
        header.append("    OBD_BEGIN_PART_DEVICE()\n")

        if not self.standardised:
            pass
        else:
            last_index = '0'
            first_index = 1
            for item in iter(self.standardised):
                # Array Type
                if item['type'] == 1:
                    if last_index != item['index']:
                        if first_index:
                            first_index = 0

                            header.append("\n")
                            header.append("        OBD_BEGIN_INDEX_RAM(0x%s," % (item['index']) +
                                          " 0x{0:02x}, FALSE)\n".format(int(item['Objects'])+1))
                            header.append("            OBD_SUBINDEX_RAM_VAR(0x%s, 0x00, kObdTypeUInt8, kObdAccConst," % (
                                        item['index']) +
                                          "tObdUnsigned8, NumberOfEntries, 0x{0:02x})\n".format(int(item['Objects'])))
                            last_index = item['index']
                        else:
                            header.append("        OBD_END_INDEX(0x%s)\n" % last_index)
                            header.append("\n")
                            header.append("        OBD_BEGIN_INDEX_RAM(0x%s," % (item['index']) +
                                          " 0x{0:02x}, FALSE)\n".format(int(item['Objects'])+1))
                            header.append("            OBD_SUBINDEX_RAM_VAR(0x%s, 0x00, kObdTypeUInt8, kObdAccConst," % (
                                        item['index']) +
                                          "tObdUnsigned8, NumberOfEntries, 0x{0:02x})\n".format(int(item['Objects'])))
                            last_index = item['index']

                    odb_type = self.object_dict_types[item['dataType']]
                    odb_acc = 'kObdAccVPR' if item['accessType'] == 'ro' else 'kObdAccVPRW'

                    header.append("            OBD_SUBINDEX_RAM_USERDEF(0x%s, " % item['index'] +
                                  "0x{0:02x}, ".format(int(item['subIndex'])) +
                                  "%s, %s, %s, %s, %s)\n" % (
                                odb_type[0], odb_acc, odb_type[1], item['name'], odb_type[2]))
                # Single Type
                else:
                    if last_index != item['index']:
                        if first_index:
                            first_index = 0

                            header.append("\n")
                            header.append("        OBD_BEGIN_INDEX_RAM(0x%s, 0x01, FALSE)\n" % item['index'])
                            last_index = item['index']
                        else:
                            header.append("        OBD_END_INDEX(0x%s)\n" % last_index)
                            header.append("\n")
                            header.append("        OBD_BEGIN_INDEX_RAM(0x%s, 0x01, FALSE)\n" % item['index'])
                            last_index = item['index']

                        odb_type = self.object_dict_types[item['dataType']]
                        odb_acc = 'kObdAccVPR' if item['accessType'] == 'ro' else 'kObdAccVPRW'

                        header.append("            OBD_SUBINDEX_RAM_VAR(0x%s, 0x00, %s, %s, %s, %s, %s, %s)\n" % (
                                    item['index'], odb_type[0], odb_acc, odb_type[1], item['name'], odb_type[2]))
            header.append("        OBD_END_INDEX(0x%s)\n" % last_index)
            header.append("\n")
        header.append("    OBD_END_PART()\n")
        header.append("\n")
        header.append("OBD_END()\n")
        header.append("\n")
        header.append("#define OBD_UNDEFINE_MACRO\n")
        header.append("    #include <obdcreate/obdmacro.h>\n")
        header.append("#undef OBD_UNDEFINE_MACRO\n")

        if os.path.isfile(self.directory + "/common/objdicts/CiA401_CN/objdict.h"):
            os.remove(self.directory + "/common/objdicts/CiA401_CN/objdict.h")

        with open(self.directory + "/common/objdicts/CiA401_CN/objdict.h", 'w') as f:
            f.writelines(header)

    # Create the opc ua nodeset.xml file
    def create_nodeset(self):

        if not self.oplk_tags:
            if self.root is None:
                self.logger.error("There is no xml root defined!")
                sys.exit(-1)
            if not self.oplk_elements:
                self.create_oplk_elements()
            self.create_oplk_tags()
            self.logger.info("Creating POWERLINK tags!")

        header = list()
        header.append('<UANodeSet xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" ' +
                      'xmlns:uax="http://opcfoundation.org/UA/2008/02/Types.xsd"' +
                      ' xmlns="http://opcfoundation.org/UA/2011/03/UANodeSet.xsd"' +
                      ' xmlns:s1="%s"' % self.link + ' xmlns:xsd="http://www.w3.org/2001/XMLSchema">\n')
        header.append('    <NamespaceUris>\n')
        header.append('        <Uri>%s</Uri>\n' % self.link)
        header.append('    </NamespaceUris>\n')

        unique_datatype = list()
        self.create_variables()

        for item in iter(self.manufacturer):
            if not self.opcua_types[item['dataType']] in unique_datatype:
                unique_datatype.append(self.opcua_types[item['dataType']])

        for item in iter(self.standardised):
            if not self.opcua_types[item['dataType']] in unique_datatype:
                unique_datatype.append(self.opcua_types[item['dataType']])

        # Add variable types
        header.append('    <Aliases>\n')
        for unique in iter(unique_datatype):
            header.append('        <Alias Alias="')
            header.append('%s">i=%s</Alias>\n' % (unique[0], unique[1]))

        header.append('        <Alias Alias="Organizes">i=35</Alias>\n')
        header.append('        <Alias Alias="HasModellingRule">i=37</Alias>\n')
        header.append('        <Alias Alias="HasTypeDefinition">i=40</Alias>\n')
        header.append('        <Alias Alias="HasSubtype">i=45</Alias>\n')
        header.append('        <Alias Alias="HasComponent">i=47</Alias>\n')
        header.append('    </Aliases>\n')

        # POWERLINK Folder
        header.append('    <UAObject NodeId="ns=1;i=1000" BrowseName="1:POWERLINK">\n')
        header.append('        <DisplayName>POWERLINK</DisplayName>\n')
        header.append('        <References>\n')
        header.append('            <Reference ReferenceType="Organizes" IsForward="false">i=85</Reference>\n')
        header.append('            <Reference ReferenceType="HasTypeDefinition">i=61</Reference>\n')
        header.append('        </References>\n')
        header.append('    </UAObject>\n')

        # Manufacturer Folder
        header.append('    <UAObject NodeId="ns=1;i=200" BrowseName="1:Manufacturer">\n')
        header.append('        <DisplayName>Manufacturer</DisplayName>\n')
        header.append('        <References>\n')
        header.append('            <Reference ReferenceType="Organizes" IsForward="false">ns=1;i=1000</Reference>\n')
        header.append('            <Reference ReferenceType="HasTypeDefinition">i=61</Reference>\n')
        header.append('        </References>\n')
        header.append('    </UAObject>\n')

        # Standardised Folder
        header.append('    <UAObject NodeId="ns=1;i=600" BrowseName="1:Standardised">\n')
        header.append('        <DisplayName>Standardised</DisplayName>\n')
        header.append('        <References>\n')
        header.append('            <Reference ReferenceType="Organizes" IsForward="false">ns=1;i=1000</Reference>\n')
        header.append('            <Reference ReferenceType="HasTypeDefinition">i=61</Reference>\n')
        header.append('        </References>\n')
        header.append('    </UAObject>\n')

        last_index = '0'
        for item in iter(self.manufacturer):
            if item['type'] == 1:
                if last_index != item['index']:
                    # Create Instance
                    header.append(
                        '    <UAObject NodeId="ns=1;i=%s" BrowseName="1:%s">\n' % (item['index'], item['ObjectName']))
                    header.append('        <DisplayName>%s</DisplayName>\n' % (item['ObjectName']))
                    header.append('        <References>\n')
                    header.append(
                        '            <Reference ReferenceType="Organizes" IsForward="false">ns=1;i=600</Reference>\n')
                    header.append('            <Reference ReferenceType="HasTypeDefinition">i=58</Reference>\n')
                    for obj in range(0, item['Objects']):
                        header.append('            <Reference ReferenceType="HasComponent">ns=1;i=%s</Reference>\n' % (
                                    item['index'] + "{0:02x}".format(obj+1)))
                    header.append('        </References>\n')
                    header.append('    </UAObject>\n')
                    last_index = item['index']

                data_type = self.opcua_types.get(item['dataType'])
                access = '3' if item['accessType'] == 'ro' else '1'
                header.append('    <UAVariable ParentNodeId="ns=1;i=%s" NodeId="ns=1;i=%s" ' % (
                            item['index'], item['index'] + item['subIndex']) +
                              'BrowseName="1:%s" DataType="i=%s" UserAccessLevel="%s" AccessLevel="%s">\n' % (
                            item['name'], data_type[1], access, access))
                header.append('        <DisplayName>%s</DisplayName>\n' % item['name'])
                header.append('        <References>\n')
                header.append('            <Reference ReferenceType="HasTypeDefinition">i=63</Reference>\n')
                header.append(
                    '            <Reference ReferenceType="HasComponent" IsForward="false">ns=1;i=%s</Reference>\n' % item[
                        'index'])
                header.append('        </References>\n')
                header.append('        <Value>\n')
                header.append('            <uax:%s>0</uax:%s>\n' % (data_type[0], data_type[0]))
                header.append('        </Value>\n')
                header.append('    </UAVariable>\n')

            else:
                data_type = self.opcua_types.get(item['dataType'])
                access = '3' if item['accessType'] == 'ro' else '1'
                header.append('    <UAVariable ParentNodeId="ns=1;i=%s" NodeId="ns=1;i=%s" ' % (
                            item['index'], item['index'] + item['subIndex']) +
                              'BrowseName="1:%s" DataType="i=%s" UserAccessLevel="%s" AccessLevel="%s">\n' % (
                            item['name'], data_type[1], access, access))
                header.append('        <DisplayName>%s</DisplayName>\n' % item['name'])
                header.append('        <References>\n')
                header.append('            <Reference ReferenceType="HasTypeDefinition">i=63</Reference>\n')
                header.append(
                    '            <Reference ReferenceType="HasComponent" IsForward="false">ns=1;i=600</Reference>\n')
                header.append('        </References>\n')
                header.append('        <Value>\n')
                header.append('            <uax:%s>0</uax:%s>\n' % (data_type[0], data_type[0]))
                header.append('        </Value>\n')
                header.append('    </UAVariable>\n')

        last_index = '0'
        for item in iter(self.standardised):
            if item['type'] == 1:
                if last_index != item['index']:
                    # Create Instance
                    header.append('    <UAObject NodeId="ns=1;i=%s" BrowseName="1:%s">\n' % (
                                item['index'], item['ObjectName']))
                    header.append('        <DisplayName>%s</DisplayName>\n' % (item['ObjectName']))
                    header.append('        <References>\n')
                    header.append('            <Reference ReferenceType="Organizes" IsForward="false">' +
                                  'ns=1;i=600</Reference>\n')
                    header.append('            <Reference ReferenceType="HasTypeDefinition">i=58</Reference>\n')
                    for obj in range(0, item['Objects']):
                        header.append('            <Reference ReferenceType="HasComponent">ns=1;i=%s</Reference>\n' % (
                                    item['index'] + "{0:02x}".format(obj+1)))
                    header.append('        </References>\n')
                    header.append('    </UAObject>\n')
                    last_index = item['index']

                data_type = self.opcua_types.get(item['dataType'])
                access = '3' if item['accessType'] == 'ro' else '1'
                header.append('    <UAVariable ParentNodeId="ns=1;i=%s" NodeId="ns=1;i=%s" ' % (
                            item['index'], item['index'] + item['subIndex']) +
                              'BrowseName="1:%s" DataType="i=%s" UserAccessLevel="%s" AccessLevel="%s">\n' % (
                            item['name'], data_type[1], access, access))
                header.append('        <DisplayName>%s</DisplayName>\n' % item['name'])
                header.append('        <References>\n')
                header.append('            <Reference ReferenceType="HasTypeDefinition">i=63</Reference>\n')
                header.append('            <Reference ReferenceType="HasComponent" IsForward="false">' +
                              'ns=1;i=%s</Reference>\n' % item['index'])
                header.append('        </References>\n')
                header.append('        <Value>\n')
                header.append('            <uax:%s>0</uax:%s>\n' % (data_type[0], data_type[0]))
                header.append('        </Value>\n')
                header.append('    </UAVariable>\n')

            else:
                data_type = self.opcua_types.get(item['dataType'])
                access = '3' if item['accessType'] == 'ro' else '1'
                header.append('    <UAVariable ParentNodeId="ns=1;i=%s" NodeId="ns=1;i=%s" ' % (
                            item['index'], item['index'] + item['subIndex']) +
                              'BrowseName="1:%s" DataType="i=%s" UserAccessLevel="%s" AccessLevel="%s">\n' % (
                            item['name'], data_type[1], access, access))
                header.append('        <DisplayName>%s</DisplayName>\n' % item['name'])
                header.append('        <References>\n')
                header.append('            <Reference ReferenceType="HasTypeDefinition">i=63</Reference>\n')
                header.append('            <Reference ReferenceType="HasComponent" IsForward="false">' +
                              'ns=1;i=600</Reference>\n')
                header.append('        </References>\n')
                header.append('        <Value>\n')
                header.append('            <uax:%s>0</uax:%s>\n' % (data_type[0], data_type[0]))
                header.append('        </Value>\n')
                header.append('    </UAVariable>\n')

        header.append('    <UAVariable ParentNodeId="ns=1;i=1000" NodeId="ns=1;i=1001" BrowseName="1:' +
                      'OperationStatus" DataType="i=12" UserAccessLevel="1" AccessLevel="1">\n')
        header.append('        <DisplayName>OperationStatus</DisplayName>\n')
        header.append('        <References>\n')
        header.append('            <Reference ReferenceType="HasTypeDefinition">i=63</Reference>\n')
        header.append('            <Reference ReferenceType="HasComponent" IsForward="false">ns=1;i=1000</Reference>\n')
        header.append('        </References>\n')
        header.append('        <Value>\n')
        header.append('            <uax:String>Init</uax:String>\n')
        header.append('        </Value>\n')
        header.append('    </UAVariable>\n')

        header.append('</UANodeSet>\n')

        with open(self.directory + '/tools/nodeset/nodeset.xml', 'w') as f:
            for line in iter(header):
                f.write(line)

        if os.path.isfile(self.directory + "/src/nodeset.c"):
            os.remove(self.directory + "/src/nodeset.c")

        if os.path.isfile(self.directory + "/include/opcua/nodeset.h"):
            os.remove(self.directory + "/include/opcua/nodeset.h")

        ret = os.system(
                "python %s/tools/nodeset_compiler/nodeset_compiler.py " % self.directory +
                "--types-array=UA_TYPES --existing %s/tools/schema/Opc.Ua.NodeSet2.Minimal.xml" % self.directory +
                " --xml %s %s/include/opcua/nodeset" % (
                    self.directory + '/tools/nodeset/nodeset.xml', self.directory))

        if ret:
            self.logger.error("Error creating the nodeset files!")
            sys.exit(-1)

    # Creates the app.c file
    def create_app(self):

        if not self.oplk_tags:
            if self.root is None:
                self.logger.error("There is no xml root defined!")
                sys.exit(-1)
            if not self.oplk_elements:
                self.create_oplk_elements()
            self.create_oplk_tags()
            self.logger.info("Creating POWERLINK tags!")

        with open(self.directory + "/tools/xdd_compiler/exchange.c", 'r') as f:
            file_data = f.readlines()

        data_l = list()

        self.create_variables()

        for item in iter(self.manufacturer):
            data_l.append(item)

        for item in iter(self.standardised):
            data_l.append(item)

        # Create the structure for the Input variables
        unique_names = list()
        data_new = list()

        for item in iter(data_l):
                name_str = item['name'] + "_" + item['index'] + "_" + item['subIndex']
                unique_names.append(name_str)
                data_new.append(
                    {'dataType': self.oplk_types[item['dataType']], 'name': name_str,
                     'index': item['index'], 'subIndex': item['subIndex'],
                     'accessType': item['accessType'], 'type': item['type']})

        tmp_data_in = list()
        tmp_data_out = list()

        # Input and Output structure
        tmp_data_in.append("// structure for input process image\n")
        tmp_data_in.append("typedef struct\n")
        tmp_data_in.append("{\n")

        tmp_data_out.append("// structure for output process image\n")
        tmp_data_out.append("typedef struct\n")
        tmp_data_out.append("{\n")

        for item in iter(data_new):
            if item['accessType'] == 'ro':
                tmp_data_in.append("   %s                %s;\n" % (
                                self.opcua_data_types[self.oplk_types_reverse[item['dataType']]][0], item['name']))
            else:
                tmp_data_out.append("   %s                %s;\n" % (
                                self.opcua_data_types[self.oplk_types_reverse[item['dataType']]][0], item['name']))

        tmp_data_in.append("} PI_IN;\n")
        tmp_data_in.append("\n")

        tmp_data_out.append("} PI_OUT;\n")
        tmp_data_out.append("\n")

        for item in iter(tmp_data_in):
            file_data.append(item)

        for item in iter(tmp_data_out):
            file_data.append(item)

        # Variable declaration
        file_data.append("//------------------------------------------------------------------------------\n")
        file_data.append("// local vars\n")
        file_data.append("//------------------------------------------------------------------------------\n")
        file_data.append("// process image\n")
        file_data.append("static PI_IN*           pProcessImageIn_l;\n")
        file_data.append("static const PI_OUT*    pProcessImageOut_l;\n")
        file_data.append("\n")
        file_data.append("// application variables\n")

        for item in iter(data_new):
            file_data.append("static %s            %s;\n" % (
                            self.opcua_data_types[self.oplk_types_reverse[item['dataType']]][0], item['name'] + "_l"))

        file_data.append("static char*            Status_l;\n")
        file_data.append("\n")
        file_data.append("BOOL status_init = 1;")
        file_data.append("\n")

        # processSync function

        with open(self.directory + '/tools/xdd_compiler/app_top.txt', 'r') as f:
            app_top = f.readlines()

        for line in iter(app_top):
            file_data.append(line)

        tmp_data_in = []
        tmp_data_out = []

        file_data.append("\n")

        for item in iter(data_new):
            if item['accessType'] == 'ro':
                tmp_data_in.append("    pProcessImageIn_l->%s = %s;\n" % (item['name'], item['name'] + "_l"))
            else:
                tmp_data_out.append("    %s = pProcessImageOut_l->%s;\n" % (item['name'] + "_l", item['name']))

        for line in iter(tmp_data_out):
            file_data.append(line)

        file_data.append("\n")
        file_data.append("// setup output image - digital inputs\n")

        for line in iter(tmp_data_in):
            file_data.append(line)

        file_data.append("\n")
        file_data.append("    ret = oplk_exchangeProcessImageIn();\n")
        file_data.append("\n")
        file_data.append("    return ret;\n")
        file_data.append("}\n")
        file_data.append("\n")

        # link OPCUA to PLK function
        callback = list()
        callback.append("void callbackOPCUA(UA_Server *server) {\n")

        for item in iter(data_new):
            # Input type
            if item['accessType'] == 'rw':
                callback.append("	// Write a different value\n")
                callback.append("	UA_NodeId %s = UA_NODEID_NUMERIC(2, %s);\n" % (
                                "nodeId" + item['name'], item['index'] + item['subIndex']))
                callback.append("\n")
                callback.append("	%s variable_%s;\n" % (
                                self.opcua_data_types[self.oplk_types_reverse[item['dataType']]][0],
                                item['index'] + item['subIndex']))
                callback.append("	memcpy(&variable_%s, &%s, sizeof(%s));\n" % (
                                item['index'] + item['subIndex'], item['name'] + "_l",
                                self.opcua_data_types[self.oplk_types_reverse[item['dataType']]][0]))
                callback.append("	UA_Variant var%s;\n" % item['name'])
                callback.append("	UA_Variant_init(&var%s);\n" % item['name'])
                callback.append("	UA_Variant_setScalar(&var%s, &variable_%s, &UA_TYPES[%s]);\n" %
                                (item['name'], item['index'] + item['subIndex'],
                                 self.opcua_data_types[self.oplk_types_reverse[item['dataType']]][1]))
                callback.append("	UA_Server_writeValue(server, %s, var%s);\n" % ("nodeId" + item['name'], item['name']))
                callback.append("\n")
            else:
                callback.append("	// Read a value\n")
                callback.append("	UA_NodeId %s = UA_NODEID_NUMERIC(2, %s);\n" %
                                ("nodeId" + item['name'], item['index'] + item['subIndex']))
                callback.append("\n")
                callback.append("	UA_Variant var%s;\n" % item['name'])
                callback.append("	UA_Server_readValue(server, %s, &var%s);\n" % ("nodeId" + item['name'], item['name']))
                callback.append("	memcpy(&%s, var%s.data, sizeof(%s));\n" %
                                (item['name'] + "_l", item['name'], item['dataType']))
                callback.append("\n")

        callback.append("	// Write the status value\n")
        callback.append("	UA_NodeId nodeIdStatus = UA_NODEID_NUMERIC(2, 1001);\n")
        callback.append("\n")
        callback.append("	UA_String strStatus = UA_STRING(Status_l);\n")
        callback.append("	UA_Variant varStatus;\n")
        callback.append("	UA_Variant_init(&varStatus);\n")
        callback.append("	UA_Variant_setScalar(&varStatus, &strStatus, &UA_TYPES[UA_TYPES_STRING]);\n")
        callback.append("	UA_Server_writeValue(server, nodeIdStatus, varStatus);\n")

        callback.append("}\n")
        callback.append("\n")

        for line in iter(callback):
            file_data.append(line)

        # Setup Inputs function
        inputs_l = list()

        inputs_l.append("void  setupInputs(void) {\n")

        for item in iter(data_new):
            if item['accessType'] == 'ro':
                inputs_l.append("    %s = 0;\n" % (item['name'] + "_l"))

        inputs_l.append("}\n")
        inputs_l.append("\n")

        for line in iter(inputs_l):
            file_data.append(line)

        # Setup status value
        status_l = list()

        status_l.append("void setStatus_OPCUA(const char* status) {\n")
        status_l.append("	if (status_init) {\n")
        status_l.append("		Status_l = malloc(strlen(status) + 1);\n")
        status_l.append("		strcpy(Status_l, status);\n")
        status_l.append("		status_init = 0;\n")
        status_l.append("	}\n")
        status_l.append("	else {\n")
        status_l.append("		free(Status_l);\n")
        status_l.append("		Status_l = malloc(strlen(status) + 1);\n")
        status_l.append("		strcpy(Status_l, status);\n")
        status_l.append("	}\n")
        status_l.append("}\n")
        status_l.append("\n")

        for line in iter(status_l):
            file_data.append(line)

        # Print Input and Print Outputs function
        output_func = list()
        input_func = list()

        output_func.append("void printOutputs(void) {\n")
        output_func.append('	printf("Output values:\\n");\n')

        input_func.append("void printInputs(void) {\n")
        input_func.append('	printf("Input values:\\n");\n')

        for item in iter(data_new):
            if item['accessType'] == 'ro':
                input_func.append('	printf("%s: %s\\n",%s);\n' % (item['name'], '%d', item['name'] + "_l"))
            else:
                output_func.append('	printf("%s: %s\\n",%s);\n' % (item['name'], '%d', item['name'] + "_l"))

        output_func.append("}\n")
        output_func.append("\n")

        input_func.append("}\n")
        input_func.append("\n")

        for line in iter(input_func):
            file_data.append(line)

        for line in iter(output_func):
            file_data.append(line)

        # initProcessImage function
        with open(self.directory + '/tools/xdd_compiler/app_init.txt', 'r') as f:
            app_init = f.readlines()

        with open(self.directory + '/tools/xdd_compiler/app_error.txt', 'r') as f:
            app_error = f.readlines()

        for line in iter(app_init):
            file_data.append(line)

        for item in iter(data_new):
            if item['accessType'] == 'ro':
                file_data.append("    obdSize = sizeof(pProcessImageIn_l->%s);\n" % item['name'])
            else:
                file_data.append("    obdSize = sizeof(pProcessImageOut_l->%s);\n" % item['name'])
            file_data.append("    varEntries = 1;\n")
            file_data.append("    ret = oplk_linkProcessImageObject(0x%s,\n" % item['index'])
            file_data.append("                                      0x{0:02x},\n".format(int(item['subIndex'])))
            if item['accessType'] == 'ro':
                mode = 'FALSE'
                file_data.append("                                      offsetof(PI_IN, %s),\n" % item['name'])
            else:
                mode = 'TRUE'
                file_data.append("                                      offsetof(PI_OUT, %s),\n" % item['name'])
            file_data.append("                                      %s,\n" % mode)
            file_data.append("                                      obdSize,\n")
            file_data.append("                                      &varEntries);\n")

            for line in iter(app_error):
                file_data.append(line)

            file_data.append("\n")

        file_data.append('   fprintf(stderr, "Linking process vars... ok\\n\\n");\n')
        file_data.append("\n")
        file_data.append("    return kErrorOk;\n")
        file_data.append("}\n")
        file_data.append("\n")
        file_data.append("/// \}\n")

        with open(self.directory + "/src/opcua2powerlink/app.c", 'w') as f:
            for line in iter(file_data):
                f.write(line)

    # Create all the required files
    def create_all(self):
        if not self.oplk_tags:
            if self.root is None:
                self.logger.error("There is no xml root defined!")
                sys.exit(-1)
            if not self.oplk_elements:
                self.create_oplk_elements()
            self.create_oplk_tags()
            self.logger.info("Creating POWERLINK tags!")

        self.logger.info("Creating Files!")
        self.create_objdict()
        self.create_nodeset()
        self.create_app()
        self.logger.info("Finished creating files!")


# Main function controlling the compilation
if __name__ == '__main__':
    # Get the xdd file path
    xdd_file = sys.argv[1]
    # Get the project start path
    root_dir = sys.argv[2]
    # Get the namespace link
    link_name = sys.argv[3]

    converter = ConvertXDD(link=link_name, xdd=xdd_file, directory=root_dir)
    converter.create_all()
