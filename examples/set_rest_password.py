#
# Copyright (c) 2023 - 2024 SICK AG
# SPDX-License-Identifier: MIT
#

import json
from sick_scan_rest_client.client import RESTClient

# This is a short example script which demonstrates how to change the REST password via the REST API.

# Summary of the performed actions:
# - Login with the user level "Service".
# - Set REST password of user "Maintenance" to "sick".

# Create the client object
client = RESTClient(device_ip_address="192.168.0.1")

# Login with the user level "Service" and the corresponding password. Here we use the default password.
user_level = RESTClient.UserLevel.Service
password = "servicelevel"
success = client.set_user_level(user_level, password=password)
if success:
    print(f"Logging in with user level: {user_level}\n")
else:
    print(f"Error logging in with user level: {user_level}\n")

# The user level of the target user must be less than or equal to the logged in user level.
success, result = client.change_password(RESTClient.UserLevel.Maintenance, "sick")
resultJSON = json.dumps(result)
print(f"success = {success}, result={resultJSON}\n")

# To change the password of maintenance back to the default password 'main', execute the following line:
# success, result = client.change_password(RESTClient.UserLevel.Maintenance, "main")
