import pyuda
import sys
import time
import select
import paramiko
import re
import fcntl
import os
###############################################################################
def sshMakeConnection(username, password, cucm):
    ssh = paramiko.SSHClient()
    try:
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(cucm, username = username, password = password)
        print("... success");
        return ssh

    except ValueError as err:
        print("... failed.....")
        print(err.args) 
        sys.exit()
 
###############################################################################
def send_string_and_wait_for_string(shell, command, wait_string, should_print):
    # Send the su command
    # print("send shell command");
    shell.send(command)
    # print(command)
    # Create a new receive buffer
    receive_buffer = ""
    while not wait_string in receive_buffer:
        # Flush the receive buffer
        receive_buffer += shell.recv(1024)
    # Print the receive buffer, if necessary
    if should_print:
        print receive_buffer
        
    return receive_buffer
###############################################################################
def send_real_time_command(shell, command, wait_string, **keyword_parameters):
    shell.send(command)
    fl = fcntl.fcntl(sys.stdin.fileno(), fcntl.F_GETFL)
    fcntl.fcntl(sys.stdin.fileno(), fcntl.F_SETFL, fl | os.O_NONBLOCK)
    counter = 0;

    while True:
        try:
            stdin = sys.stdin.read()
            if "\n" in stdin or "\r" in stdin:
                sys.exit()
        except IOError:
            pass

        realtime_buffer = ""

        # Filters        
        if keyword_parameters['filter'] != "":    
            #print(keyword_parameters['filter'])
            while not "\n" in realtime_buffer:
                #sys.stdout.flush()
                #print('in inner while')
                realtime_buffer += shell.recv(1)
                #print(realtime_buffer)
                if (keyword_parameters['filter'] in realtime_buffer):
                    #print("have filtered message")

                    if len(realtime_buffer) >=1024 or "\n" in realtime_buffer:
                        #print("let's print")
                        print(realtime_buffer)
                        realtime_buffer = ""

        # No filters        

        else:
            while not "\n" in realtime_buffer:
                realtime_buffer += shell.recv(1)
                if(len(realtime_buffer) >= 1024):
                    print(realtime_buffer)
                    realtime_buffer = ""    
            if realtime_buffer != "":
                print(realtime_buffer)
            
###############################################################################
def testFunction(shell, command, wait_string, phone):
    shell.send(command)
    fl = fcntl.fcntl(sys.stdin.fileno(), fcntl.F_GETFL)
    fcntl.fcntl(sys.stdin.fileno(), fcntl.F_SETFL, fl | os.O_NONBLOCK)
    while True:
        try:
            stdin = sys.stdin.read()
            if "\n" in stdin or "\r" in stdin:
                sys.exit()
        except IOError:
            pass

        realtime_buffer = ""
        while not "\n" in realtime_buffer:
            realtime_buffer += shell.recv(1)
            #print realtime_buffer
        if(phone in realtime_buffer):
            if ("OffHook" in realtime_buffer) and ("restart0" in realtime_buffer):
                print(phone + ": is OffHook")
            elif ("OnHook" in realtime_buffer) and ("restart0" in realtime_buffer):
                print(phone + ": is OnHook")
            elif ("outgoing_call_proceeding" in realtime_buffer):
                print(phone + ": is proceeding call")
            elif ("CallState = call_initiated" in realtime_buffer) and ("LineSetCallState" in realtime_buffer):
                print(phone + ": is initiating call")
            elif ("CallPhase = CALL_ESTABLISHING" in realtime_buffer):
                print(phone + ": establishes connectivity")    
            elif ("CallState = disconnect_request" in realtime_buffer):
                print(phone + ": Disconnected from a call")    
            elif ("Destination process does not exist" in realtime_buffer):
                print(phone + ":Destination process does not exist")    
            elif ("CalledNum" in realtime_buffer):
                print (phone + realtime_buffer) 
            elif ("StationKeypadButton" in realtime_buffer) and ("restart0" in realtime_buffer):
                print (phone + ": " + "Button pressed")
            elif ("StationLineCallAccept" in realtime_buffer) and ("restart0" in realtime_buffer):
                print (phone + ": Call goes through")
            elif ("StationSoftKeyEvent" in realtime_buffer) and  ("restart0" in realtime_buffer):
                print (realtime_buffer)

###############################################################################
def getFileName(shell, command, wait_string):
    shell.send(command)
    realtime_buffer = ""
    while not wait_string in realtime_buffer:
        realtime_buffer += shell.recv(1)

    #print("["+ realtime_buffer +"]")
    splited_buffer = realtime_buffer.split()    
    for string in splited_buffer:
        if ".txt.gzo" in string:
            return string
    #print(realtime_buffer)
    #return realtime_buffer
###############################################################################

'''
server = raw_input("Enter CUCM address: ")
user   = raw_input("Enter the username: ")
pw     = raw_input("Enter your password: ")
'''
server = "139.126.117.5"
user = "administrator"
pw = "w0rdp@ss"

# Create a raw shell

client = sshMakeConnection(user, pw, server);
shell  = client.invoke_shell()

send_string_and_wait_for_string(shell, "", "admin:", True)
#filterText = raw_input("MAC address: ")
filterText = "SEP68BC0C8035A4"

fileName = getFileName(shell, "file list activelog cm/trace/ccm/sdl\n", "admin:")
fileTailCommand = "file tail activelog cm/trace/ccm/sdl/" + fileName + "\n"

#print "[" + fileTailCommand + "]"

#testFunction(shell, fileTailCommand , "admin:", filterText)
send_real_time_command(shell, fileTailCommand, "admin:", filter = filterText)

# Disable more
#send_string_and_wait_for_string("terminal length 0\n", "#", False)

