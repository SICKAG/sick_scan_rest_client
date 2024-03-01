#
# Copyright (c) 2023 SICK AG
# SPDX-License-Identifier: MIT
#

import requests
import os
import json
import hashlib
from typing import Tuple

class RESTClient:
    """Send GET and POST requests to REST API endpoints (variables or methods) to a sensor """


    def __init__(self, deviceIpAddress:str="192.168.0.1") -> None:
        """
        Constructor of the RESTClient

        Args:
            deviceIpAddress (str): IP address of the sensor

        """
        self.deviceIpAddress = deviceIpAddress
        self.webServerSocket = "http://"+self.deviceIpAddress+":80"
        self.baseUrl = self.webServerSocket + "/api/"
        self.username=None
        self.password=None

        os.environ['NO_PROXY'] = self.deviceIpAddress # Disable proxy


    def setUserLevel(self, username:str, password:str) -> bool:
        """
        Set a user level and the corresponding password for the following requests.

        User level and password are checked with the checkPassword method and False
        is returned if they do not match.

        Args:
            username (str): Desired user level
            password (str): Password for the selected username

        Returns:
            bool: True if successful, false otherwise
        """
        success = True
        self.username = username
        self.password = password
        success, _ = self.__postItem(itemName="checkCredentials", value=None, isMethod=False)
        if not success:
            self.username = None
            self.password = None
        return success


    def readVariable(self, variableName:str)->Tuple[bool, dict]:
        """
        Read a variable from the sensor.

        Args:
            variableName (str): name of the variable

        Returns:
            bool: True if successful, false otherwise
            dict: Dictionary with the response from the sensor. The
                  actual variable value is contained in the 'data' field.
        """
        requestURL = self.baseUrl + variableName
        response = requests.get(requestURL)
        success, resultDict = self.__evaluateRestResult(response)
        return success, resultDict


    def writeVariable(self, variableName:str, value:dict)->Tuple[bool, dict]:
        """
        Write a variable of the sensor.

        Args:
            variableName (str): Name of the variable
            value (dict): Parameters of the variable, provided as a dictionary

        Returns:
            bool: True if successful, false otherwise
            dict: Dictionary with the response from the sensor.
        """
        return self.__postItem(variableName, value, isMethod = False)


    def callMethod(self, methodName:str, value:dict)->Tuple[bool, dict]:
        """
        Call a method of the sensor.

        Args:
            methodName (str): Name of the method
            value (dict): Parameters of the method, supplied as a dictionary,
                          or None if the method has no parameters

        Returns:
           bool: True if successful, false otherwise
           dict: Dictionary with the response from the sensor.
        """
        return self.__postItem(methodName, value, isMethod = True)



    def __postItem(self, itemName:str, value:dict, isMethod:bool) -> Tuple[bool, dict]:
        """
        Write a variable or execute a method.

        The parameters must be supplied as dictionary in the value parameter.
        Use json.loads to create the dictionary from a JSON string which is
        obtained e.g. from an openAPI description. For a method with no
        parameters the value parameter can be ignored.

        Args:
            itemName: name of the item, i.e. variable name or method name
            itemValue: parameters of the item, supplied as dictionary
            isMethod: true, if the item is a method, false otherwise


        Returns:
           bool: True if successful, false otherwise
           dict: Dictionary with the response from the sensor.
        """

        header = self.__getAuthPostHeader(itemName)
        requestDict = dict()
        requestDict["header"] = header
        if value is not None:
            requestDict["data"] = dict()
            if isMethod:
                requestDict["data"] = value
            else:
                requestDict["data"][itemName] = value
        request = json.dumps(requestDict)
        response = requests.post(self.baseUrl+itemName, data=request)
        success, resultDict = self.__evaluateRestResult(response)

        return success, resultDict

    def __evaluateRestResult(self, response:dict)->Tuple[bool, dict]:
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
                status =  True
        return status, result


    def __getAuthPostHeader(self, itemName:str) -> dict:
        """
        Create response to challenge from sensor

        Args:
            itemName (str): Name of the item for which the response is computed

        Returns:
            dict: Computed response values as dictionary
        """

        if self.username is None or self.password is None:
            raise RuntimeError("Undefined user level or password. Call setUserLevel first.")

        # get challenge from sensor
        url = self.baseUrl + 'getChallenge'
        requestPayload = '{ "data": { "user": "'+ self.username + '" } }'
        r = requests.post(url, data=requestPayload)
        chal = r.json()

        # parse the challenge
        realm = chal['challenge']['realm']
        nonce = chal['challenge']['nonce']
        opaque = chal['challenge']['opaque']

        # compute the response
        hstr1 = self.username + ":" + realm + ":" + self.password
        if 'salt' in chal['challenge']:
            salt = chal['challenge']['salt']
            # build byte character string (no ASCII!)
            saltBinary = ''
            for i in salt:
                saltBinary = saltBinary + chr(salt[i])
            hstr1 = hstr1 + ":" + saltBinary
        ha1 = hashlib.sha256(hstr1.encode()).hexdigest()

        methodType = 'POST'
        hstr2 = methodType + ":" + itemName
        ha2 = hashlib.sha256(hstr2.encode()).hexdigest()
        hstr3 = ha1 + ":" + nonce + ":" + ha2
        response = hashlib.sha256(hstr3.encode()).hexdigest()

        # fill header
        header = dict()
        header['nonce'] = nonce
        header['opaque'] = opaque
        header['realm'] = realm
        header['response'] = response
        header['user'] = self.username
        return header
