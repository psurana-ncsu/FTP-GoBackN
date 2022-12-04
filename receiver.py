import time
import socket
import random

class Receiver:
    host = socket.gethostname()
    expected_seq_no = 0
    data_type = '0101010101010101'
    ack_type = '1010101010101010'
    complete = False
    def __init__(self, port, output_file, loss_prob):
        self.server_port = port
        self.filename = output_file
        self.file = open(self.filename, "wb")
        self.loss_prob = loss_prob
        self.soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.soc.bind((self.host, self.server_port))
        print(f"SERVER is listening at {self.HOST} {self.PORT}\n")

    def carry_around_add(a, b):
        c = a + b
        return (c & 0xffff) + (c >> 16)

    def err_probability(p):
        r = random.random()
        if r <= p:
            print("R {} less than P {}".format(r, p))
            return False
        else:
            return True


    def calculate_checksum(self, checksum, data):
        s = 0
        # Check if length of data is even or odd. For calculating checksum we need to do
        # ones complement of ones complement sum of 16 bit words. Therefore if the
        # data has an even number of bytes this will work out. However if the data has
        # an odd number of bytes we should add one byte of zeroes to do zero padding
        if len(data) % 2 != 0:
            data = data + b"0"
        for i in range(0, len(data), 2):
            w = data[i] + (data[i + 1] << 8)
            s = self.carry_around_add(s, w)
        # check_this_value contains the checksum computed off the data. We need to convert it to 16 bits and compare with
        # the checksum received from the packet
        check_this_value = ~s & 0xffff
        check_this_value = '{0:016b}'.format(check_this_value).encode()
        if checksum == check_this_value:
            return True
        else:
            return False        

    def rdt_receive(self):
        self.soc.settimeout(5)
        try:
            while True:
                datagram, client_addr = self.soc.recvfrom(2048)
                message = datagram.decode()
                if data == "End of file":
                    print("Server - Complete file received")
                    break
                # header is 64 bits
                header = message[:64]
                # 32 bits sequence no
                seq_no = header[:32]
                #  next 16 bits are checksum
                checksum = header[32:48]
                # next 16 are data type indicator
                data_inicator = header[48:]
                # data field
                data = message[64:]
                if self.expected_seq_no ==int(seq_no, 2):
                    if self.calculate_checksum (checksum, data):
                        if self.data_type == data_inicator:
                            # Probability for some error
                            if self.err_probability(self.loss_prob):
                                # Everything is correct write this to the file
                                self.file.write(str.encode(data[64:]))
                                # Set the new expected sequence number
                                self.expected_seq_no += len(data)
                                # Set the ack number
                                zero_padding = '{0:016b}'.format(0).encode()
                                ack_indicator = b"1010101010101010"
                                ack_segment = seq_no + zero_padding + ack_indicator
                                self.soc.sendto(ack_segment, client_addr)
                            else:
                                print("Packet loss, sequence number = {}".format(int(seq_no, 2)))
                        else:
                            print("Packet dropped - Data type mismatch.")
                    else:
                        print("Packet dropped - Checksum error.")
                else:
                    print("Packet dropped - Seq no out of order. Expected Seq no {}. Received Seq no {}".format(self.expected_seq_no, int(seq_no, 2)))