#
# Copyright (c) 2023 - 2024 SICK AG
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
# - Call the method "WriteEeprom".


# Create the client object
client = RESTClient(device_ip_address="192.168.0.1")


# Read the variable "ScanDataEthSettings".
# The result is returned as a dictionary.
variable_name = "ScanDataEthSettings"
success, result_scan_data_eth_settings = client.read_variable(variable_name)
result_json = json.dumps(result_scan_data_eth_settings) # The result is a dictionary which can be converted with json.dumps to a json string.
print(f"Reading {variable_name}: success = {success}, result={result_json}\n")

# Read the non existing variable "ScanDataEthSettingsTypo".
# Success will be false and the corresponding error can be found in the result dictionary.
variable_name = "ScanDataEthSettingsTypo"
success, result = client.read_variable(variable_name)
result_json = json.dumps(result) # The result is a dictionary which can be converted with json.dumps to a json string.
print(f"Reading {variable_name}: success = {success}, result={result_json}\n")

# Login with the user level "Service" and the corresponding password. Here we use the default password.
# To login with other user levels please note that they have to be activated first via the UI.
userLevel = RESTClient.UserLevel.Service
password = "servicelevel"
success = client.set_user_level(userLevel, password)
if success:
    print(f"Logging in with user level: {userLevel}\n")
else:
    print(f"Error logging in with user level: {userLevel}\n")

# Write the variable "ScanDataEthSettings" and change ip address using a JSON string.
variable_name = "ScanDataEthSettings"
body = '{"Protocol": 1, "IPAddress": [192, 168, 0, 100], "Port": 2115}'
success, result = client.write_variable(variable_name, json.loads(body))
result_json = json.dumps(result) # The result is a dictionary which can be converted with json.dumps to a json string.
print(f"Writing {variable_name} based on JSON string as body: success = {success}, result={result_json}\n")

# Write the variable "ScanDataEthSettings" and change ip address using the previously read dictionary.
variable_name = "ScanDataEthSettings"
body = result_scan_data_eth_settings["data"][variable_name]
body["IPAddress"] = [192,168,0,102]
success, result = client.write_variable(variable_name, body)
result_json = json.dumps(result) # The result is a dictionary which can be converted with json.dumps to a json string.
print(f"Writing {variable_name} using previously read body: success = {success}, result={result_json}\n")

# Read the variable "ScanDataEthSettings" and make sure that value changed.
variable_name = "ScanDataEthSettings"
success, result = client.read_variable(variable_name)
result_json = json.dumps(result) # The result is a dictionary which can be converted with json.dumps to a json string.
print(f"Reading {variable_name} with changed ip address: success = {success}, result={result_json}\n")

# Write the variable "ScanDataEnable".
# This is an example how to write a variable with a single value as argument.
variable_name = "ScanDataEnable"
body = True
success, result = client.write_variable(variable_name, body)
result_json = json.dumps(result) # The result is a dictionary which can be converted with json.dumps to a json string.
print(f"Writing {variable_name} with parameter {body}: success = {success}, result={result_json}\n")

# Read variable "ScanDataEnable".
variable_name = "ScanDataEnable"
success, result = client.read_variable(variable_name)
result_json = json.dumps(result) # The result is a dictionary which can be converted with json.dumps to a json string.
print(f"Reading {variable_name}: success = {success}, result={result_json}\n")

# Call the method "FindMe". Both device LEDs will blink for the given duration (in seconds).
method_name = "FindMe"
body =  {"uiDuration": 5}
success, result = client.call_method(method_name, body)
result_json = json.dumps(result) # The result is a dictionary which can be converted with json.dumps to a json string.
print(f"Calling {method_name} with parameter {body}: success = {success}, result={result_json}\n")

# Call the method "WriteEeprom".
# This is to show how to call a method without a parameter.
# Please note that calling this method saves the previously written device parameters permanently!
# Above the data output parameters are modified. Change them back and save parameters again if required.
method_name = "WriteEeprom"
body =  None
success, result = client.call_method(method_name, body)
result_json = json.dumps(result) # The result is a dictionary which can be converted with json.dumps to a json string.
print(f"Calling {method_name} with no parameter: success = {success}, result={result_json}\n")
