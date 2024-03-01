#
# Copyright (c) 2023 SICK AG
# SPDX-License-Identifier: MIT
#

from sick_scan_rest_client.client import RESTClient
import json


# This is a short example script which demonstrates how to use the SICK Scan REST Client.
# To find out the format of a variable's or a method's body for the writeVariable or
# callMethod functions calls please refer to the openAPI description:
# https://www.sick.com/de/de/catalog/digitale-dienste-und-loesungen/software/openapi-datei-picoscan150/p/p678507?tab=downloads

# Summary of the performed actions:
# - Read variable "ScanDataEthSettings".
# - Read non existing variable "ScanDataEthSettingsTypo".
# - Login with the user level "Service".
# - Write variable "ScanDataEthSettings" and change ip address using a JSON string.
# - Write variable "ScanDataEthSettings" and change ip address using the previously
#   read variable content as dictionary
# - Read variable "ScanDataEthSettings" and make sure that value changed.
# - Write variable "ScanDataEnable".
# - Read variable "ScanDataEnable".
# - Call method "FindMe".

# Create the client object
client = RESTClient(deviceIpAddress="192.168.0.1")


# Read the variable "ScanDataEthSettings".
# The result is returned as a dictionary.
variableName = "ScanDataEthSettings"
success, resultScanDataEthSettings = client.readVariable(variableName)
resultJSON = json.dumps(resultScanDataEthSettings) # The result is a dictionary which can be converted with json.dumps to a json string.
print(f"Reading {variableName}: success = {success}, result={resultJSON}\n")

# Read the non existing variable "ScanDataEthSettingsTypo".
# Success will be false and the corresponding error can be found in the result dictionary.
variableName = "ScanDataEthSettingsTypo"
success, result = client.readVariable(variableName)
resultJSON = json.dumps(result) # The result is a dictionary which can be converted with json.dumps to a json string.
print(f"Reading {variableName}: success = {success}, result={resultJSON}\n")

# Login with the user level "Service" and the corresponding password. Here we use the default password.
# To login with other user levels please note that they have to be activated first via the UI.
userLevel = "Service"
password = "servicelevel"
success = client.setUserLevel(username=userLevel, password=password)
if success:
    print(f"Logging in with user level: {userLevel}\n")
else:
    print(f"Error logging in with user level: {userLevel}\n") 

# Write the variable "ScanDataEthSettings" and change ip address using a JSON string.
variableName = "ScanDataEthSettings"
body = '{"Protocol": 1, "IPAddress": [192, 168, 0, 100], "Port": 2115}'
success, result = client.writeVariable(variableName, json.loads(body))
resultJSON = json.dumps(result) # The result is a dictionary which can be converted with json.dumps to a json string.
print(f"Writing {variableName} based on JSON string as body: success = {success}, result={resultJSON}\n")

# Write the variable "ScanDataEthSettings" and change ip address using the previously read dictionary.
variableName = "ScanDataEthSettings"
body = resultScanDataEthSettings["data"][variableName]
body["IPAddress"] = [192,168,0,102]
success, result = client.writeVariable(variableName, body)
resultJSON = json.dumps(result) # The result is a dictionary which can be converted with json.dumps to a json string.
print(f"Writing {variableName} using previously read body: success = {success}, result={resultJSON}\n")

# Read the variable "ScanDataEthSettings" and make sure that value changed.
variableName = "ScanDataEthSettings"
success, result = client.readVariable(variableName)
resultJSON = json.dumps(result) # The result is a dictionary which can be converted with json.dumps to a json string.
print(f"Reading {variableName} with changed ip address: success = {success}, result={resultJSON}\n")

# Write the variable "ScanDataEnable".
# This is an example how to write a variable with a single value as argument.
variableName = "ScanDataEnable"
body = True
success, result = client.writeVariable(variableName, body)
resultJSON = json.dumps(result) # The result is a dictionary which can be converted with json.dumps to a json string.
print(f"Writing {variableName} with parameter {body}: success = {success}, result={resultJSON}\n")

# Read variable "ScanDataEnable".
variableName = "ScanDataEnable"
success, result = client.readVariable(variableName)
resultJSON = json.dumps(result) # The result is a dictionary which can be converted with json.dumps to a json string.
print(f"Reading {variableName}: success = {success}, result={resultJSON}\n")

# Call the method "FindMe". Both device LEDs will blink for the given duration (in seconds).
methodName = "FindMe"
body =  {"uiDuration": 5}
success, result = client.callMethod(methodName, body)
resultJSON = json.dumps(result) # The result is a dictionary which can be converted with json.dumps to a json string.
print(f"Calling {methodName} with parameter {body}: success = {success}, result={resultJSON}\n")

# Call the method "WriteEeprom".
# This is to show how to call a method without a parameter.
# Please note that calling this method saves the previously written device parameters permanently!
# Above the data output parameters are modified. Change them back and save parameters again if required.
methodName = "WriteEeprom"
body =  None
success, result = client.callMethod(methodName, body)
resultJSON = json.dumps(result) # The result is a dictionary which can be converted with json.dumps to a json string.
print(f"Calling {methodName} with no parameter: success = {success}, result={resultJSON}\n")
