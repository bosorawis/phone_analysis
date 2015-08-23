import pyuda
import sys
import time
import select
import paramiko
import re
import fcntl
import os

fl = fcntl.fcntl(sys.stdin.fileno(), fcntl.F_GETFL)
fcntl.fcntl(sys.stdin.fileno(), fcntl.F_SETFL, fl | os.O_NONBLOCK)

###############################################################################
def sshMakeConnection(username, password, cucm):
    #print('sshMakeConnection')
    ssh = paramiko.SSHClient()
    #print(cucm)
    #print(username)
    #print(password)
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
    realtime_buffer = ""
    while not wait_string in receive_buffer:
        # Flush the receive buffer
        receive_buffer += shell.recv(1024)
        if "file tail" in command:
            print('tail')
            realtime_buffer = ""
            while not "\n" in realtime_buffer:
                realtime_buffer += shell.recv(1)
            
            print(realtime_buffer)
            try:
                stdin = sys.stdin.read()
                if "\n" in stdin or "\r" in stdin:
                    break
            except IOError:
                    pass
        else:  
            continue
    # Print the receive buffer, if necessary
    if should_print:
        print receive_buffer

    return receive_buffer
###############################################################################




# server = raw_input("Enter CUCM address: ")
# user   = raw_input("Enter the username: ")
# pw     = raw_input("Enter your password: ")
server = "139.126.117.5"
user = "administrator"
pw = "w0rdp@ss"


# Create a raw shell

client = sshMakeConnection(user, pw, server);
shell  = client.invoke_shell()

#print("hello")
# Wait for the prompt
#send_string_and_wait_for_string(shell, "\n", "admin:", True)

#send_string_and_wait_for_string(shell, "file tail activelog /cm/trace/ccm/sdl/SDL001_100_000441.txt.gzo", "admin:", True)
#send_string_and_wait_for_string(shell, "file tail activelog /cm/trace/ccm/sdl/SDL001_100_000441.txt.gzo", "admin:", True)

send_string_and_wait_for_string(shell, "", "admin:", True)
#send_string_and_wait_for_string(shell, "show status\n", "admin:", True)

send_string_and_wait_for_string(shell, "file tail activelog /cm/trace/ccm/sdl/SDL001_100_000441.txt.gzo\n", "admin:", True)

# Disable more
#send_string_and_wait_for_string("terminal length 0\n", "#", False)



#stdin, stdout, stderr = ssh.exec_command("show status")
#print(stdout.readline())
