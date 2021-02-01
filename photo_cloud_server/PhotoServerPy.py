'''
.Created on 13.07.2016

@author: Marcel
'''
import os
import socket
import sys
import random
import time
import datetime 
import logging
from shutil import copyfile
from httplib import EXPECTATION_FAILED

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
    

# convert binary to integer
def binary_to_int(binary):
    data = binary[binary.find('b')+1:]
    return int(data, 2)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, filename="logfile.txt", filemode="a+",format="%(asctime)-15s %(levelname)-8s %(message)s")
    #create an INET, STREAMing socket
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #bind the socket to a public host, and a well-known port
    serversocket.bind((Host, 4123))
    print >>sys.stderr, 'bind socket .....' 
    #become a server socket
    serversocket.listen(5)
    print >>sys.stderr, 'start listen .....' 
    
    while True:
        print >>sys.stderr, 'wait for client .....' 
        connection, client_address = serversocket.accept()
        start_time = datetime.datetime.fromtimestamp(time.mktime(time.gmtime()))
        data = '0';
    
        try:
            print >>sys.stderr, 'connection from', client_address
            logging.info('connection from ' + str(client_address))
            # Receive the data in small chunks and retransmit it
            data = connection.recv(17)
            id = binary_to_int(data)
                
            if id == 1302:
                logging.info('correct ID ...')
                print >>sys.stderr, 'correct ID ...'
                # generate seed
                seed = random.randrange(1000, 9999, 1)
                # send seed
                connection.sendall(bin(seed).zfill(17))
                # calculate key and match witch received key
                key = ((seed + 12) * 2) + 123;
                rec_key_bin = connection.recv(17)
                rec_key = binary_to_int(rec_key_bin)
                
                if (key == rec_key):
                    logging.info('correct key ...')
                    print >>sys.stderr, 'correct key ...'
                    liste = get_file_list()
                    connection.sendall(bin(len(liste)).zfill(17))
                    print 'number of pictures: ' + str(len(liste))
                      
                    for pic in liste:
                        if error_counter > 50:
                            break
                        error_counter = 0
                        # send picture size
                        statinfo = os.stat(str(pic))
                        size =statinfo.st_size
                        connection.sendall(bin(size).zfill(65))
                        print('filesize: ' + str(size) + ' -- ' + str(bin(size)))
                        # open actual picture
                        photo = open(str(pic), "rb")
                        print 'open file ...'
                        # send picture
                        while size > 0:
                            if (size > 1024):
                                data = photo.read(1024)
                                try:
                                    connection.sendall(data)
                                    size = size - 1024
                                    error_counter = 0
                                except socket.error, ex:
                                    error_counter = error_counter + 1
                                    print str(error_counter) + '--'  + str(size) 
                                    time.sleep(0.1) 
                                    if error_counter > 50:
                                        connection.close()
                                        break
                            else:
                                data = photo.read(size)
                                try:
                                    connection.sendall(data)
                                    size = 0
                                    error_counter = 0
                                    break
                                except socket.error, ex:
                                    error_counter = error_counter + 1
                                    print str(error_counter) + str(size) 
                                    time.sleep(0.1)
                                    if error_counter > 50:
                                        connection.close()
                                        break
                        photo.close()
                        print >>sys.stderr, 'sending complete ...'
                        name = str(round(time.time(),0))
                        name = name[0:name.find('.')]
                        copyfile(pic, 'save/' + name + ".jpg")
                        time.sleep(2)
                        os.remove(pic)
                    error_counter = 0
                    connection.close()
                else:
                    print >>sys.stderr, 'wrong key ...'
                    connection.close()
            else:
                print >>sys.stderr, 'wrong ID ...'
                connection.close()
        except:
            print >>sys.stderr, 'disconect with error ...'
            connection.close()
        finally:
            # Clean up the connection
            logging.info('finish')
            
