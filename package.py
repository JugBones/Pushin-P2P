from enum import Enum
import hashlib
import json


# To avoid typo let's use enum
# Add more if there is more Request Method
class RequestMethod(Enum):
    POST = "PUTTING"
    GET = "I WANT"


# Add more if there is more content type
class ContentType(Enum):
    APP_JSON = 'application/json'


class Package:
    """
    A class represent the header and payload. 
    """

    def __init__(self, content_type: ContentType, payload: str = "", checksum: str = None, payload_length: int = 0):
        self.__checksum = hashlib.md5(
            payload.encode()).hexdigest() if checksum is None else checksum

        self.__content_type: str = content_type.value if isinstance(
            content_type, ContentType) else content_type

        self.__payload_length = len(
            payload) if payload_length == 0 else payload_length

        self.__payload = payload

    def read_json(package: str) -> "Package":
        """
        Static method that read package in json format and return a Package instance.

        Args:
            package (str): package in json string format.

        Returns:
            Package: Package class instance.
        """
        _package = json.loads(package)
        checksum = _package["Checksum"]
        content_type = _package["Content-Type"]
        payload_length = _package["Payload-Length"]
        payload = _package["Payload"]
        return Package(payload, content_type, checksum=checksum, payload_length=payload_length)

    def verify_payload(self) -> bool:
        """
        Compare checksum in the header and payload's checksum

        Returns:
            bool: True if the checksum matches, False otherwise.
                  If checksum is corrupted, it should return False.
        """
        return self.__checksum == hashlib.md5(self.__payload.encode()).hexdigest()

    def __str__(self) -> str:
        # To string method, str(<Header instance>) or print(<Header instance>)
        # should return str represtation of header
        return json.dumps({
            "Checksum": self.__checksum,
            "Content-Type": self.__content_type,
            "Payload-Length": self.__payload_length,
            "Payload": self.__payload
        })
