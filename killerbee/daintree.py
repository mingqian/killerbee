import binascii
import time

class DainTreeDumper:
    def __init__(self, savefile):
        '''
        Writes to the specified file in Daintree SNA packet capture file format.
        @type savefile: String
        @param savefile: Output Daintree SNA packet capture file.
        @rtype: None
        '''
        ltime = time.localtime()
        timeymd = ''.join([str(ltime[0]),str(ltime[1]),str(ltime[2])])
        DSNA_HEADER1 = '#Format=4\r\n'
        DSNA_HEADER2 = '# SNA v3.0.0.7 SUS:%s ACT:067341\r\n'%timeymd
        self._pcount = 0
        self._fh = open(savefile, "w")
        self._fh.write(DSNA_HEADER1)
        self._fh.write(DSNA_HEADER2)

    def pcap_dump(self, packet, ts_sec=None, ts_usec=None, orig_len=None):
        '''
        This method is a wrapper around the pwrite() method for compatibility
        with the PcapDumper.pcap_dump method.
        '''
        self.pwrite(packet)

    def pwrite(self, packet, channel=26, rssi=0):
        '''
        Appends a new packet to the daintree capture  file.  
        @type packet: String
        @param packet: Packet contents
        @type channel: Int
        @param channel: Capture file reported channel number (optional, def=26)
        @type rssi: Int
        @param rssi: Capture file repored RSSI (optional, def=0)
        @rtype: None
        '''
        self._pcount += 1
        record = ''.join([
                str(self._pcount), " ", 
                "%6f"%time.time(), " ", 
                str(len(packet)), " ",
                str(binascii.hexlify(packet)), " ",
                "255 ",                             # LQI
                "1 ",                               # Unknown
                str(rssi), " ",                     # RSSI
                str(channel), " ",                  # Channel
                str(self._pcount), " ",             # packet#, repeated why?
                "0 1 32767\r\n"])                   # Unknown
        self._fh.write(record)
        
    def close(self):
        '''
        Close the input packet capture file.
        @rtype: None
        '''
        del(self._fh)


class DainTreeReader:
    def __init__(self, savefile):
        '''
        Reads from a specified Daintree SNA packet capture file.
        @type savefile: String
        @param savefile: Daintree SNA packet capture filename to read from.
        @rtype: None.  An exception is raised if the capture file is not in Daintree SNA format.
        '''
        DSNA_HEADER1 = b'#Format=4\r\n'
        self._fh = open(savefile, "rb")
        header = self._fh.readline()
        print(header)

        if header != DSNA_HEADER1:
            raise Exception('Invalid or unsupported Daintree SNA file specified')

    def close(self):
        '''
        Close the output packet capture.
        @rtype: None
        '''
        del(self._fh)

    def pnext(self):
        '''
        Retrieves the next packet from the capture file.  Returns a list of
        [Hdr, packet] where Hdr is a list of [timestamp, snaplen, plen] and
        packet is a string of the payload content.  Returns None at the end
        of the packet capture.
        @rtype: List
        '''
        try:
            while(1):
                record = self._fh.readline().split(' ')
                if record[0][0] == "#":
                    continue
                else:
                    break

            if record == None:
                return None
            # Return a list with the first element a list containing timestamp
            # for compatibility with ithe pcapdump PcapReader.pnext() method.
            return [[float(record[1]),len(record[3]),len(record[3])], binascii.unhexlify(record[3])]
        except IndexError:
            return [None, None]
