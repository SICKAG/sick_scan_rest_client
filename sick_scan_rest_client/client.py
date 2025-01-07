#
# Copyright (c) 2023 - 2024 SICK AG
# SPDX-License-Identifier: MIT
#

from enum import Enum
from hashlib import sha256
import hmac
import json
import os
from secrets import token_bytes
from typing import Tuple, Optional

from Crypto.Cipher import AES
import requests


class RESTClient:
    """Send GET and POST requests to REST API endpoints (variables or methods) to a sensor """

    class UserLevel(Enum):
        """Enumeration of the user levels"""
        # pylint: disable=invalid-name
        # We want to keep the names as they are defined in the devices
        Run = 0
        Operator = 1
        Maintenance = 2
        AuthorizedClient = 3
        Service = 4
        SICKService = 5
        Production = 6
        Developer = 7

    def __init__(self, device_ip_address: str = "192.168.0.1") -> None:
        """
        Constructor of the RESTClient

        Args:
            device_ip_address (str): IP address of the sensor

        """

        self.base_url = "http://"+device_ip_address+":80/api/"
        self.user_level = RESTClient.UserLevel.Run
        self.password = ""

        os.environ['NO_PROXY'] = device_ip_address  # Disable proxy

    def set_user_level(self, user_level: UserLevel, password: str) -> bool:
        """
        Set a user level and the corresponding password for the following requests.

        User level and password are checked with the checkPassword method and False
        is returned if they do not match and the user level is set to the level 'Run'.

        Args:
            user_level (str): Desired user level
            password (str): Password for the selected user level

        Returns:
            bool: True if successful, false otherwise
        """
        success = True
        self.user_level = user_level
        self.password = password
        success, _ = self.__post_item(item_name="checkCredentials", value=None, is_method=False)
        if not success:
            self.user_level = RESTClient.UserLevel.Run
            self.password = ""
        return success

    def read_variable(self, variable_name: str) -> Tuple[bool, dict]:
        """
        Read a variable from the sensor.

        Args:
            variable_name (str): name of the variable

        Returns:
            bool: True if successful, false otherwise
            dict: Dictionary with the response from the sensor. The
                  actual variable value is contained in the 'data' field.
        """
        request_url = self.base_url + variable_name
        response = requests.get(request_url, timeout=5)
        success, result_dict = self.__evaluate_rest_result(response)
        return success, result_dict

    def write_variable(
            self,
            variable_name: str,
            value: dict) -> Tuple[bool, dict]:
        """
        Write a variable of the sensor.

        Args:
            variable_name (str): Name of the variable
            value (dict): Parameters of the variable, provided as a dictionary

        Returns:
            bool: True if successful, false otherwise
            dict: Dictionary with the response from the sensor.
        """
        return self.__post_item(variable_name, value, False)

    def call_method(
            self,
            method_name: str,
            value: dict,
            challenge: Optional[dict] = None) -> Tuple[bool, dict]:
        """
        Call a method of the sensor.

        Args:
            method_name (str): Name of the method
            value (dict): Parameters of the method, supplied as a dictionary,
                          or None if the method has no parameters
            challenge(dict): optional challenge from the sensor.
            If not provided a new challenge is requested.

        Returns:
           bool: True if successful, false otherwise
           dict: Dictionary with the response from the sensor.
        """
        return self.__post_item(method_name, value, True, challenge)

    def __post_item(self, item_name: str, value: dict, is_method: bool,
                    challenge: Optional[dict] = None) -> Tuple[bool, dict]:
        """
        Write a variable or execute a method.

        The parameters must be supplied as dictionary in the value parameter.
        Use json.loads to create the dictionary from a JSON string which is
        obtained e.g. from an openAPI description. For a method with no
        parameters the value parameter can be ignored.

        Args:
            item_name: name of the item, i.e. variable name or method name
            value: parameters of the item, supplied as dictionary
            is_method: true, if the item is a method, false otherwise
            challenge: optional challenge from the sensor.
            If not provided a new challenge is requested.


        Returns:
           bool: True if successful, false otherwise
           dict: Dictionary with the response from the sensor.
        """
        if challenge is None:
            challenge = self.get_challenge()
        header = self.__get_auth_post_header(item_name, challenge)
        request_dict = {}
        request_dict["header"] = header
        if value is not None:
            request_dict["data"] = {}
            if is_method:
                request_dict["data"] = value
            else:
                request_dict["data"][item_name] = value
        request = json.dumps(request_dict)
        response = requests.post(self.base_url+item_name, data=request, timeout=5)
        success, result_dict = self.__evaluate_rest_result(response)

        return success, result_dict

    def __evaluate_rest_result(self, response: dict) -> Tuple[bool, dict]:
        """
        Evaluate the result structure from the requests.post function

        Args:
            response (dict): Response dictionary returned by requests.post

        Returns:
            bool: True if successful, false otherwise
            dict: Dictionary with the response from the sensor.
        """
        result = None
        status = False
        if response.status_code == 200:
            result = json.loads(response.text)
            if result["header"]["status"] == 0:
                status = True
        return status, result

    def get_challenge(self) -> dict:
        """
        Gets a challenge from the sensor

        Returns:
            dict: The challenge for the user
        """

        url = self.base_url + 'getChallenge'
        request_payload = '{ "data": { "user": "' + self.user_level.name + '" } }'
        r = requests.post(url, data=request_payload, timeout=5)
        return r.json()["challenge"]

    def __get_auth_post_header(self, item_name: str, challenge: dict) -> dict:
        """
        Create response to challenge from sensor

        Args:
            item_name (str): Name of the item for which the response is computed
            challenge (dict): Challenge from the sensor

        Returns:
            dict: Computed response values as dictionary
        """

        # parse the challenge
        realm = challenge['realm']
        nonce = challenge['nonce']
        opaque = challenge['opaque']

        # .encode() returns a bytes representation of the Unicode string
        # For the password we use __stringToBytes since we allow here
        # only characters according to ISO 8859-15 (8Bit per characters)
        # as input. If Unicode characters are used in a password string,
        # it can happen that different characters are mapped to the same
        # byte value. Example: 'sick' and 'ųũţū' would be interpreted as equivalent
        # passwords.
        hstr1 = (self.user_level.name + ":" + realm + ":").encode() \
            + self.__string_to_bytes(self.password)
        if 'salt' in challenge:
            hstr1 += ":".encode() + bytes(challenge['salt'])
        # Get the hashed data as a hex string
        hash1 = sha256(hstr1).hexdigest()

        method_type = 'POST'
        hstr2 = (method_type + ":" + item_name).encode()
        hash2 = sha256(hstr2).hexdigest()
        hstr3 = (hash1 + ":" + nonce + ":" + hash2).encode()
        response = sha256(hstr3).hexdigest()

        # fill header
        header = {}
        header['nonce'] = nonce
        header['opaque'] = opaque
        header['realm'] = realm
        header['response'] = response
        header['user'] = self.user_level.name
        return header

    def __string_to_bytes(self, string: str) -> bytes:
        """Converts a string to a byte array.
        To determine the byte value of each character first its unicode value
        is computed and then the modulo 256 of this value is taken.

        Args:
            string (str): The string that shall be converted.

        Returns:
            bytes: The byte representation of the string.
        """
        bytes_of_string = bytearray()
        for char in string:
            bytes_of_string.append(ord(char) % 256)
        return bytes(bytes_of_string)

    def change_password(self, target_user_level: UserLevel, target_user_level_new_password: str) -> Tuple[bool, dict]:
        """
        Change the password for a user level
        less than or equal to the current user level.

        Args:
            target_user_level (UserLevel): User level of the user whose password should be changed
            target_user_level_new_password (str): New password for the user

        Returns:
            bool: True if successful, false otherwise
            dict: Dictionary with the response from the sensor.
        """

        if target_user_level.value > self.user_level.value:
            raise ValueError(
                "The user level of the target user must be\
                    less than or equal to the current user level.")

        # Get a challenge from the sensor
        challenge = self.get_challenge()
        # Compute the hash of the password
        password_hash = self.__get_password_hash(
            bytes(challenge["salt"]),
            challenge["realm"],
            self.user_level.name, self.password, target_user_level.name,
            target_user_level_new_password)

        method_name = "changePassword"
        body = {"userLevel": target_user_level.value,
                "encryptedMessage": list(password_hash)}
        success, result = self.call_method(method_name, body, challenge)
        return success, result

    def __get_password_hash(
            self,
            device_provided_salt: list[int],
            realm: str,
            invoker_user_level: UserLevel,
            invoker_password: str,
            target_user_level: UserLevel,
            target_user_level_new_password: str) -> bytes:
        """Calculate the password hash to change the REST password.
        See the flow chart in the readme for a bigger picture.

        This method generates a password hash for changing the REST password by performing the following steps:
        1. Calculates the invoker's password hash using the invoker's user level, password, and the salt provided by the device.
        2. Calculates the target user's new password hash using the target user's user level, new password, and client-generated salt.
        3. Encrypts the target user's new password hash using the invoker's password hash as the AES encryption key and an initialization vector.
        4. Calculates the HMAC of the encrypted password hash using the invoker's password hash as the HMAC key.

        Args:
            device_provided_salt (list[int]): Salt generated by the device
            realm (str): Realm of the challenge
            invoker_user_level (UserLevel): User level of the invoker
            invoker_password (str): Password of the invoker
            target_user_level (UserLevel): User level of the target user
            target_user_level_new_password (str): New password for the target user

        Returns:
            bytes: The password hash
        """
        def utf8(s):
            return s.encode("utf-8")

        def _aes128_cbc_encrypt(data, key, iv):
            cipher = AES.new(key, AES.MODE_CBC, iv)
            return cipher.encrypt(data)

        def _user_level_prefix(user_level, realm):
            return user_level + ":" + realm + ":"

        #  Step 1: calculate invoker password hash
        invoker_password_and_level = utf8(_user_level_prefix(
            invoker_user_level, realm) + invoker_password)
        invoker_salted_password_hash = sha256(
            invoker_password_and_level + utf8(":") + device_provided_salt).digest()

        # Step 2: calculate target password hash
        client_generated_salt = token_bytes(16)  # 128 random bits
        target_new_password_and_level = utf8(_user_level_prefix(
            target_user_level, realm) + target_user_level_new_password)
        new_salted_password_hash = sha256(
            target_new_password_and_level + utf8(":") + client_generated_salt).digest()

        # Step 3: Encode new password
        aes_encryption_key = invoker_salted_password_hash[:16]
        initialization_vector = token_bytes(16)  # 128 random bits
        encrypted_salted_new_password_hash = _aes128_cbc_encrypt(
            new_salted_password_hash + client_generated_salt,
            aes_encryption_key,
            initialization_vector
        )

        # Step 4: Calculate HMAC
        hmac_key = invoker_salted_password_hash
        hmac_message = initialization_vector + encrypted_salted_new_password_hash
        hmac_result = hmac.new(hmac_key, hmac_message, sha256).digest()

        return hmac_message + hmac_result
