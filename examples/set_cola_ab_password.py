#
# Copyright (c) 2023 - 2024 SICK AG
# SPDX-License-Identifier: MIT
#

from sick_scan_rest_client.client import RESTClient
import json
import hashlib

# ============================================
# WARNING: CoLa A/B is SICKs legacy protocol.
# It is recommended to use the REST interface.
# ============================================

# This is a short example script which demonstrates how to change the Cola A/B password via the REST API.

# Summary of the performed actions:
# - Login with the user level "Service".
# - Set Cola A/B password of user "Maintenance" to "sick".

# Create the client object
client = RESTClient(device_ip_address="192.168.0.1")

# Login with the user level "Service" and the corresponding password. Here we use the default password.
# To login with other user levels please note that they have to be activated first via the UI.
user_level = RESTClient.UserLevel.Service
password = "servicelevel"
success = client.set_user_level(user_level, password)
if success:
    print(f"Logging in with user level: {user_level.value}\n")
else:
    print(f"Error logging in with user level: {user_level.value}\n")


def get_password_hash(password):
    """
    Hashes the password using the MD5 algorithm.
    Only ISO 8859-15 (8 bits per character) characters are allowed.
    First the string is encoded using ISO 8859-15 and then the MD5 algorithm is applied.
    This results in 16 bytes. The bytes are grouped into four groups
    of four bytes each. Each group is XORed to a single byte.
    The resulting four bytes are concatenated to a 32 bit integer.

    Args:
        password (string): Password to be hashed

    Returns:
        int: Hashed password
    """
    digest = hashlib.md5(password.encode("ISO 8859-15")).digest()

    hash_parts = bytearray(4)
    hash_parts[0] = digest[0] ^ digest[4] ^ digest[8] ^ digest[12]
    hash_parts[1] = digest[1] ^ digest[5] ^ digest[9] ^ digest[13]
    hash_parts[2] = digest[2] ^ digest[6] ^ digest[10] ^ digest[14]
    hash_parts[3] = digest[3] ^ digest[7] ^ digest[11] ^ digest[15]

    return int.from_bytes(hash_parts, byteorder='little', signed=False)

# Set the password of user "Maintenance" to "sick"
# Note that it is only possible to change the password of a user
# with a user level less than or equal to the current user level.
method_name = "SetPassword"
body =  {"siUserLevel": RESTClient.UserLevel.Maintenance.value, "udiNewPassword": get_password_hash("sick")}
success, result = client.call_method(method_name, body)
resultJSON = json.dumps(result)
print(f"Calling {method_name} with parameter {body}: success = {success}, result={resultJSON}\n")

# To change the password of maintenance back to the default password 'main', execute the following lines:
# method_name = "SetPassword"
# body =  {"siUserLevel": RESTClient.UserLevel.Maintenance.value, "udiNewPassword": get_password_hash("main")}
# success, result = client.call_method(method_name, body)
