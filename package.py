from typing import List
import hashlib


class Package:
    def divide_to_chunks(package: bytes, chunk_size: int) -> List[bytes]:
        """
        Divide package to be sent into chunks of specified bytes

        Args:
            package (bytes): package to be sent.
            chunk_size (int): number of bytes to be divided.

        Returns:
            List[bytes]: All the divided chunks in a List
        """
        chunks = [package[i: (i + chunk_size)]
                  for i in range(0, len(package), chunk_size)]
        return chunks

    def bundle_to_one(sorted_chunks: List[bytes]) -> bytes:
        """
        Merge sorted chunks into a package

        Args:
            sorted_chunks (List[bytes]): UDP segment might not be sent in order
                                        so before putting the packages 
                                        into the argument. please sort it first.

        Returns:
            bytes: Merged packages
        """

        return b"".join(sorted_chunks)

    def verify_package(checksum: bytes, package: bytes) -> bool:
        """
        Verifying packages using md5

        Args:
            checksum (bytes): the digest of the package,
            package (bytes): the package to compare against the digest.

        Returns:
            bool: True if matches and false if not matches, 
            if the checksum is corrupted it should return False.
        """
        package_checksum = hashlib.md5(package).digest()

        if package_checksum == checksum:
            return True

        return False

    def generate_checksum(chunk: bytes) -> bytes:
        """
        Generate checksum to be compare to verify the integrity of the file

        Args:
            chunk (bytes): The chunk to be sent

        Returns:
            bytes: checksum using md5 hash 
        """
        checksum = hashlib.md5(chunk).digest()
        return checksum
