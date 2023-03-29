import hashlib
import json
from typing import List
from enum import Enum


class HandshakeMessage(Enum):
    SYN = "Hi, are you there?"
    SYN_ACK = "Yes, I am here."
    ACK = "I received the message that you are there."


class TransportSegment:
    """
    A class represent the header and payload. 
    """

    def __init__(self, segment_number: int, data: str = "", checksum: str = None):
        self.__segment_number = segment_number
        self.__data = data.value if isinstance(
            data, HandshakeMessage) else data
        self.__checksum = hashlib.md5(
            self.__data.encode()).hexdigest() if checksum is None else checksum

    def read_json(package: str) -> "TransportSegment":
        """
        Static method that read package in json format and return a Package instance.

        Args:
            package (str): package in json string format.

        Returns:
            Package: Package class instance.
        """
        _segment = json.loads(package)
        sequence_number = _segment["Segment-Number"]
        checksum = _segment["Checksum"]
        data = _segment["Data"]
        return TransportSegment(sequence_number, data, checksum=checksum)

    def divide_data(max_segment_size: int, data: str) -> List[str]:
        chunks = [data[i:i+max_segment_size]
                  for i in range(0, len(data), max_segment_size)]

        return [str(TransportSegment(index, chunk)) for index, chunk in enumerate(chunks)]

    def reassemble_data(chunks: List) -> str:
        li = [TransportSegment.read_json(chunk) for chunk in chunks]
        data = sorted(li, key=lambda x: x.__segment_number)

        return "".join([d.get_data() for d in data])

    def verify_payload(self) -> bool:
        """
        Compare checksum in the header and payload's checksum

        Returns:
            bool: True if the checksum matches, False otherwise.
                  If checksum is corrupted, it should return False.
        """
        return self.__checksum == hashlib.md5(self.__data.encode()).hexdigest()

    def get_data(self):
        return self.__data

    def __str__(self) -> str:
        # To string method, str(<Header instance>) or print(<Header instance>)
        # should return str represtation of header
        return json.dumps({
            "Segment-Number": self.__segment_number,
            "Checksum": self.__checksum,
            "Data": self.__data
        })
