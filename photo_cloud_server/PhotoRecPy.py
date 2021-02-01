'''
.Created on 13.07.2016

@author: Marcel
'''
import struct
import socket
import sys
import random
import os
import time
import datetime 
import logging


filelist = []
# Host = socket.gethostbyname(socket.gethostname())
Host = ''
print Host
error_counter = 0

# create list with all pictures
def get_file_list():
    filelist = []
    dirList = os.listdir('.')
    dirList.sort()
    
    for Datei in dirList:
        # Suche nach png und jpg Dateien
        if (Datei.find(".png") > -1 or Datei.find(".jpg") > -1):
            filelist.append(Datei)
    return filelist

def check_timeout(start_time_obj, timeout):
    time_obj = datetime.datetime.fromtimestamp(time.mktime(time.gmtime()))
    
    if(start_time_obj.year == time_obj.year and start_time_obj.month == time_obj.month):
        
        start_time = start_time_obj.day * 60*60*24 + start_time_obj.hour * 60*60 + start_time_obj.minute * 60 +start_time_obj.second
        time_act   = time_obj.day       * 60*60*24 + time_obj.hour       * 60*60 + time_obj.minute       * 60 +time_obj.second
        
        if(start_time + timeout < time_act):
            return True;
    
    return False;
    

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, filename="logfile_rec.txt", filemode="a+",format="%(asctime)-15s %(levelname)-8s %(message)s")
    #create an INET, STREAMing socket
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #bind the socket to a public host, and a well-known port
    serversocket.bind(('', 4000))
    print >>sys.stderr, 'bind socket .....' 
    #become a server socket
    serversocket.listen(5)
    print >>sys.stderr, 'start listen .....' 
    
    while True:
        print >>sys.stderr, 'wait for client .....' 
        connection, client_address = serversocket.accept()
        buffer_l = b'';
    
        try:
            print >>sys.stderr, 'connection from', client_address
            logging.info('connection from ' + str(client_address))
            # Receive the id
            test_timer = 0;
            while len(buffer_l) < 4:
                buffer_l += connection.recv(4-len(buffer_l))
                if (len(buffer_l) == 0):
                    test_timer = test_timer + 1;
                    time.sleep(0.1)
                if (test_timer >= 200):
                    print >>sys.stderr, 'disconnect with time out ...' 
                    break
            id = struct.unpack('!i', buffer_l)[0] 
                
            if id == 1302:
                logging.info('correct ID ...')
                print >>sys.stderr, 'correct ID ...'    
                # generate seed
                seed = random.randrange(1000, 9999, 1)     
                connection.send(struct.pack('!i',seed)) 
                
                # calculate key
                key = ((seed + 12) * 2) + 123; 
                
                # received key
                buffer_l = b'';
                while len(buffer_l) < 4:
                    buffer_l += connection.recv(4-len(buffer_l))
                rec_key = struct.unpack('!i', buffer_l)[0]   
                
                if (key == rec_key):
                    print >>sys.stderr, 'correct key ...' 
                    logging.info('correct key ...')  
                    connection.send(struct.pack('!i',1))
                    
                    # received file size
                    buffer_size = b'';
                    while len(buffer_size) < 8:
                        buffer_size += connection.recv(8-len(buffer_size))
                    file_size = struct.unpack('!q', buffer_size)[0]  
                    print >>sys.stderr, 'Filesize: ' + str(file_size)
                    
                    # received file
                    file_list = get_file_list()
                    buffer_file = b'';
                    kopie = open(str(len(file_list)+1)+'.png', "wb")
                    print 'filename: 1.jpg'
                    while file_size > len(buffer_file):
                        if (file_size - len(buffer_file) > 1024):
                            try:
                                kbyte = connection.recv(1024)
                                buffer_file = buffer_file + kbyte
                            except socket.error, ex:
                                print ex
                        else:
                            try:
                                kbyte = connection.recv(file_size-len(buffer_file))
                                buffer_file += kbyte
                                kopie.write(buffer_file)
                            except socket.error, ex:
                                print ex
                        
                    kopie.close()
                    print 'received: ' + str(len(buffer_file))
                    print 'picture completed ...'
                    logging.info('picture completed ...')
                    connection.close()
                    
                else:
                    print >>sys.stderr, 'wrong key ...' 
                    logging.info('wrong key ...')
                    connection.send(struct.pack('!i',0))  
                    connection.close()
                        
            else:
                print >>sys.stderr, 'wrong ID ...'
                logging.info('wrong ID ...')
                connection.close()
        except:
            print >>sys.stderr, 'disconect with error ...'
            logging.info('disconect with error ...')
            connection.close()
        finally:
            # Clean up the connection
            logging.info('finish ...')
            
