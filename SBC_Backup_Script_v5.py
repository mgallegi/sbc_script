##############################################################################
#
#                         SBC Backup Script
#
##############################################################################

# Import libraries:
import paramiko
import time
import sys
import os
from datetime import datetime

# All function Definitions:


def ssh_connection(ip):
    # Establish SSH Session:
    # print(ip)
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(hostname='%s' % ip, port=22, username='sbc_backup',
                       password='Fu36QF8A', auth_timeout=3, timeout=2,
                       banner_timeout=200)  # This is used to establish a connection

    # This helps you invoke the shell of the client machine
    remote_connection = ssh_client.invoke_shell()
    remote_connection.send("show clock\n")
    time.sleep(3)
    get_time = output = remote_connection.recv(1020)
    # print(get_time)
    get_time_split = get_time.split()

    # #Time:
    time_flag = get_time_split[3]
    time_flag_1 = (time_flag)
    bkp_time = str(time_flag_1[0:10])
    bkp_time_1 = bkp_time[2:10]
    # print(bkp_time_1)

    # #Date:
    c = get_time_split[5:9]
    c1 = str(c[0])
    c2 = str(c[1])
    c3 = str(c[2])
    c4 = str(c[3])
    c5 = c1[2:5], c2[2:5], c3[2:4], c4[2:6]
    bkp_date = "_".join(c5)
    # print(c1[2:5])

    print("Deleting Old Backup. Please wait...")
    print(" ")
    print(" ")

    # Delete Backup:
    # I only want output from this command.
    remote_connection.send('show backup-config\n')
    time.sleep(2)
    # Getting output I want.
    if remote_connection.recv_ready():
        output = remote_connection.recv(5000)
        backup_delet = output.decode()
        print(backup_delet)

    old_day = c1[2:5]
    file = open(backup_list_file, "w")
    file.write(backup_delet)
    file.close()
    try:
        findString('_'+old_day+'_', backup_list_file, backup_del_file)
        f = open(backup_del_file, "r")
        lines_2 = f.readlines()
        f.close()
        del_backup = lines_2[0]

        remote_connection.send("delete-backup-config "+del_backup+"\n")
        time.sleep(2)
        print(del_backup+" deleted.")
        print(" ")
        print(" ")
    except:
        print("Old Backup was NOT deleted...")
        print(" ")
        print(" ")

   # Create Backup Name:::::
    backup_name = element_name+"_"+bkp_time_1+"_"+bkp_date+".gz"
    print(backup_name)
    # Create Backup Name:
    print("Creating Backup. Please wait...")
    print(" ")
    print(" ")

    print(backup_name)
    remote_connection.send("backup-config "+backup_name+"\n")
    ssh_client.close
    print("SBC Backup --> "+backup_name+" is ready.")


def findString(substr, infile, outfile):
    with open(infile) as a, open(outfile, 'w') as b:
        for line in a:
            if substr in line:
                b.write(line)


print("=========================================")
print("SBC Backup is running.. Please wait...")
print("=========================================")
print("...")
print("...")
print("...")
print("...")

# Set network element / ip:

network_elements = {1: ('iSBC01', '10.176.43.75'),
                    2: ('iSBC02', '10.176.43.76'),
                    3: ('iSBC03', '10.176.43.35'),
                    4: ('iSBC04', '10.176.43.36'),
                    5: ('iSBC05', '10.176.43.51'),
                    6: ('iSBC06', '10.176.43.52'),
                    7: ('iSBC07', '10.176.43.67'),
                    8: ('iSBC08', '10.176.43.68'),
                    9: ('iSR01', '10.176.43.10')
                    }


# print(network_elements)


network_elements = {1: ('iSBC01', '10.176.43.75')}


# Set Variables:
remote_connection = ""
ssh_client = ""

get_time_split = ""
bkp_time_1 = ""
bkp_date = ""
backup_delet = ""
c1 = ""
now = datetime.now()
dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

a = 1
b = len(network_elements)

# Create Folder:
if not os.path.exists('C:/sbc_backup/'):
    os.makedirs('C:/sbc_backup/')

# Create File variable:
backup_list_file = 'C:/sbc_backup/backup_list.txt'
backup_del_file = 'C:/sbc_backup/backup_a_borrar.txt'
log_file = 'C:/sbc_backup/logs.txt'

# Connect and create backup
for b in network_elements:

    x = network_elements[a]
    element_name = x[0]
    # print(element_name)
    ip = x[1]
    # print(ip)
    flag = '%s' % ip

    print("==================================================================")
    print("Trying to connect to "+element_name+" IP: "+ip+". Please wait...")

    try:
        print("Shh Connection attempt N=1...")
        ssh_connection(ip)
        print("==================================================================")
    except:
        try:
            print("Shh Connection attempt N=2...")
            ssh_connection(ip)
            print("==================================================================")
        except:
            print("Connection to "+element_name+" failed.")
            ssh_log_file = open(log_file, 'a')
            ssh_log_file.write(element_name + ' '+dt_string +
                               ' --> It was not possible to establish an SSH session with the element.\n')
            ssh_log_file.close()
            print("SBC Backup Script finished with issues. Check logs.")
            print("==================================================================")

    a = a+1


# Clean up:
try:
    os.remove(backup_list_file)
    os.remove(backup_del_file)
except:
    flag = 0

# Close the script
print("---------------------")
print("SBC Backup Finished..")
print("---------------------")
time.sleep(4)
sys.exit()
