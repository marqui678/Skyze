"""Created on 12/10/2017
   @author: michaelnew"""

# Third Party Imports
from datetime import datetime
import json

# Skyze Imports
from Skyze_Standard_Library.SkyzeServiceAbstract import *


class SkyzeMessageLoggerService(SkyzeServiceAbstract):
    """Skyze inter-service message logger"""

    def __init__(self, message_bus):
        """Constructor"""
        path_to_service = "Skyze_Message_Logger_Service"
        super().__init__(log_path=path_to_service)

    def log(self, message):
        print("Logger Service: " + message.getJSON())