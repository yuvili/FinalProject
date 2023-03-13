import struct


class Packet:
    def __init__(self, data, address):
        self.sequence_number = 1
        self.ack_number = 1
        self.data = data
        self.address = address
        self.checksum = self.calculate_checksum()

    def calculate_checksum(self):
        # convert packet to byte string
        packet_bytes = struct.pack('!II1024s', self.sequence_number, self.ack_number, self.data)

        # calculate checksum using ones' complement sum
        checksum = 0
        for i in range(0, len(packet_bytes), 2):
            if i == len(packet_bytes) - 1:
                # handle odd number of bytes
                checksum += packet_bytes[i]
            else:
                # sum two bytes at a time
                checksum += (packet_bytes[i] << 8) + packet_bytes[i+1]

        # fold the 32-bit sum to 16 bits
        while (checksum >> 16) != 0:
            checksum = (checksum & 0xFFFF) + (checksum >> 16)

        # take the one's complement of the result
        checksum = ~checksum & 0xFFFF
        return checksum

    def is_packet_corrupt(self):
        """
        Function to validate the checksum of a packet
        """
        return self.checksum != 0