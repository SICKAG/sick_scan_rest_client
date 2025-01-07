#
# Copyright (c) 2024 SICK AG
# SPDX-License-Identifier: MIT
#

from sick_scan_rest_client.client import RESTClient
import json


# This is a short example script which demonstrates how to use the SICK Scan REST Client.
# To find out the format of a variable's or a method's body for the writeVariable or
# callMethod functions calls please refer to the openAPI description:
# https://www.sick.com/de/de/catalog/digitale-dienste-und-loesungen/software/openapi-datei-picoscan150/p/p678507?tab=downloads

# Summary of the performed actions:
# - Login with the user level "Service".
# - Call the method "GetFieldEvaluationContour" to read the field points of an existing evaluation case (EvaluationId: 1)
# - Call the method "SetFieldEvaluationContour" using the previously read field points (dictionary) and manipulate the points

client = RESTClient(device_ip_address="192.168.0.1")

# Login with the user level "Service" and the corresponding password. Here we use the default password.
# To login with other user levels please note that they have to be activated first via the UI.
user_level = RESTClient.UserLevel.Service
password = "servicelevel"
success = client.set_user_level(user_level=user_level, password=password)
if success:
    print(f"Logging in with user level: {user_level}\n")
else:
    print(f"Error logging in with user level: {user_level}\n")

# Call the method "GetFieldEvaluationContour"
# This call is only successful if an evaluation case with the EvaluationId 1 exists.
method_name = "GetFieldEvaluationContour"
body =  {"EvaluationId": 1}
success, result = client.call_method(method_name, body)
result_json = json.dumps(result) # The result is a dictionary which can be converted with json.dumps to a json string.
print(f"Calling {method_name} with parameter {body}: success = {success}, result={result_json}\n")

# Call the method "SetFieldEvaluationContour" using the previously read dictionary and change one field point
method_name = "SetFieldEvaluationContour"
contour = result["data"]["Contour"][0]
# Multiply all x and y values of the points by 0.5 to shrink the field
for point in contour["Points"]:
    point["x"] = int(point["x"] * 0.5)
    point["y"] = int(point["y"] * 0.5)
success, result = client.call_method(method_name, contour)
result_json = json.dumps(result) # The result is a dictionary which can be converted with json.dumps to a json string.
print(f"Calling {method_name} with parameter {contour}: success = {success}, result={result_json}\n")