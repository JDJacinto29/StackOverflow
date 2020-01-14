# Note: Script will not work if you already have the IP4 settings window open

import tkinter as Tkinter
from tkinter import *
from tkinter import simpledialog as sdg
from tkinter import messagebox
import os
import configparser as ConfigParser
import collections  # for using named tuples
import subprocess # for setting IP

def setIP(connectType):

    config,Parameters = readConfig(configFile)

    if connectType == "ResetLAN":

        # Reset LAN
        subprocess.call('netsh interface ip set address "Local Area Connection" dhcp')
        subprocess.call('netsh interface ip set dns "Local Area Connection" dhcp')
        print("LAN Reset To DHCP\n")

    elif connectType == "ResetWireless":

        # Reset Wireless
        subprocess.call('netsh interface ip set address "Wireless Network Connection" dhcp')
        subprocess.call('netsh interface ip set dns "Wireless Network Connection" dhcp')
        print("Wireless Reset To DHCP\n")

    elif connectType == "LAN":

        # Set LAN to new IP
        subprocess.call('netsh interface ip set address "Local Area Connection" static %s %s' %(Parameters.TargetIP,Parameters.TargetSubnet))
        print("LAN Reset To:\nIP Address: %s\nSubnet Mask: %s\n" %(Parameters.TargetIP,Parameters.TargetSubnet))

    elif connectType == "Wireless":

        # Set Wireless to new IP
        subprocess.call('netsh interface ip set address "Wireless Network Connection" static %s %s' %(Parameters.TargetIP,Parameters.TargetSubnet))
        print("Wireless Reset To:\nIP Address: %s\nSubnet Mask: %s\n" %(Parameters.TargetIP,Parameters.TargetSubnet))

def openINIFile():

    # Lets look for the ini
    configFile = None

    for file in os.listdir(currentDirectory):

        # parse the current directory until an ini file is found
        if file.endswith(".ini"):

            # save the file name
            configFile = file

    # if not found, prompt user
    # if configFile == None:
    #     configFile = filedialog.askopenfilename(initialdir = currentDirectory, title = "Config File Not Found, Please Locate Manually")

    return configFile

def readConfig(configFile):

    # parse the config file
    config = ConfigParser.ConfigParser()
    config.read(configFile)

    # set up named Tuple for paramters
    Parameter = collections.namedtuple('Parameters', 'TargetIP, TargetSubnet')

    # populate tuple
    Parameters = Parameter(TargetIP = config.get('Parameters','TargetIP'),TargetSubnet = config.get('Parameters','TargetSubnet'))

    return config,Parameters

def write_config():

    # save to config file
    with open(configFile, 'w') as fh:

        config.write(fh)

class UpdateIP(StringVar):

    def set(self, ip):

        print('UpdateIP.set({})'.format(ip))
        
        # update IP Address
        config[tkvar.get()]['TargetIP'] = ip
        write_config()

        super().set(ip)

def runGUI():

    # set global variables
    global SiteIDs
    global tkvar
    global popupMenu
    global updateIP
    global updateSM
    global e1

    root.title("Select Connection Type")
    frame = Tkinter.Frame(root,height=226, width=250)
    frame.configure(background='black')
    frame.pack_propagate(0) # don't shrink
    frame.pack()

    # List of sections from param
    SiteIDs = config.sections()

    # ignore Paramter section
    if "Parameters" in SiteIDs: SiteIDs.remove("Parameters")

    # Add a "Custom" option to enter a new site ID
    SiteIDs.append("Add Custom...")

    # Create a Tkinter variable
    tkvar = Tkinter.StringVar(root)
    tkvar.set(config.get("Parameters",'lastused')) # set the default option

    # popupMenu = Tkinter.OptionMenu(frame, tkvar, *SiteIDs)
    popupMenu = Tkinter.OptionMenu(frame, tkvar, *SiteIDs, command=changeSiteID)
    Tkinter.Label(frame, text="Site ID:",bg="black",fg="white").place(x = 61, y = 4)
    popupMenu.place(x = 110, y = 4,height=21,width=124)
    # link function to change dropdown
    # tkvar.trace('w', changeSiteID)

    # IP Address entry field
    Tkinter.Label(frame, text="IP Address:",bg="black",fg="white").place(x = 38, y = 30)
    updateIP = UpdateIP(root) 
    # updateIP.trace("w", lambda index, mode, sv=updateIP: updateIPAdress())
    e1 = Tkinter.Entry(frame,textvariable=updateIP)
    e1.insert(0,config.get(config.get('Parameters','lastused'),'targetip'))
    e1.place(x = 110, y = 31)

    # Subtnet Mask entry field
    Tkinter.Label(frame, text="Subnet Mask:",bg="black",fg="white").place(x = 25, y = 55)
    updateSM = Tkinter.StringVar(root)
    # updateSM.trace("w", lambda name, index, mode, sv=updateSM: updateSubnetMask())
    e2 = Tkinter.Entry(frame,textvariable=updateSM)
    e2.insert(0,config.get(config.get('Parameters','lastused'),'targetsubnet'))
    e2.place(x = 110, y = 56)

    # LAN  button
    LAN = Tkinter.Button(frame,text="Set\nLAN",command=write_LAN,height=2,width=9,font = ('Sans','14'))
    LAN.place(x = 10, y = 86)

    # Wireless button
    Wireless = Tkinter.Button(frame,text="Set\nWireless",command=write_Wireless,height=2,width=9,font = ('Sans','14'))
    Wireless.place(x = 130, y = 86)

    # Reset LAN button
    Reset = Tkinter.Button(frame,text="Reset LAN",command=write_ResetLAN,height=1,width=14)
    Reset.place(x = 10, y = 156)

    # Reset Wireless button
    Reset = Tkinter.Button(frame,text="Reset Wireless",command=write_ResetWireless,height=1,width=14)
    Reset.place(x = 130, y = 156)

    # Status button
    Status = Tkinter.Button(frame,text="Print Network Status",command=write_Status,height=1,width=20)
    Status.place(x = 10, y = 191)

    # quit button
    quitButton = Tkinter.Button(frame, text="QUIT", fg="red",command=quit)
    quitButton.place(x = 190, y = 191)
    
    # Run GUI
    root.mainloop()

def write_LAN():

    setIP("LAN")
    exit()

def write_Wireless():
    
    setIP("Wireless")
    exit()

def write_ResetLAN():
    
    setIP("ResetLAN")
    exit()

def write_ResetWireless():
    
    setIP("ResetWireless")
    exit()

def write_Status():
    
    subprocess.call('netsh interface ip show config')

def addCustomSiteID():

    newID = sdg.askstring("Add Custom", "Enter Custom Site ID")

    # If they hit cancel, forgive them
    if newID == None:

        print("Changed your mind? No problem...")

    # make sure that ID doesnt exist already, case insensitive
    elif newID.lower() in (ID.lower() for ID in SiteIDs):

        messagebox.showinfo("Duplicate SiteID", "The Site ID you entered already exists. Please enter a unique ID")

    # Add the new ID
    else:

        # update IP Address
        config.add_section(newID)

        # Add some default values
        defaultIP = '192.168.0.0'
        defaultSM = '255.255.0.0'
        config.set(newID,'TargetIP',defaultIP)
        config.set(newID,'targetsubnet',defaultSM)

        # save to cofig file
        with open(configFile, 'w') as configfile:
            
            config.write(configfile)

        # add new ID to the menu
        popupMenu.children['menu'].add_command(label=newID,command=Tkinter._setit(tkvar, newID))

        # Set the selected option to the new ID
        tkvar.set(newID)

        #Fill the text entries with default addresses
        updateIP.set(defaultIP)
        updateSM.set(defaultSM)

def changeSiteID(option):
    
    if option == "Add Custom...":

        addCustomSiteID()

    else:
        # Replace the text in the IP Address entry box
        updateIP.set(config.get(option,'targetip'))
        updateSM.set(config.get(option,'targetsubnet'))

    # Update the last used variable
    lastUsed = option
    # resetLastUsedVariable(lastUsed)

# def updateIPAdress():

    # update IP Address
    config[tkvar.get()]['TargetIP'] = updateIP.get()

    # save to cofig file
    with open(configFile, 'w') as configfile:
        config.write(configfile)

def updateSubnetMask():

    # update IP Address
    config[tkvar.get()]['TargetSubnet'] = updateSM.get()

    # save to cofig file
    with open(configFile, 'w') as configfile:
        config.write(configfile)

def resetLastUsedVariable(lastUsed):

    # update IP Address
    config["Parameters"]['lastused'] = lastUsed

    # save to cofig file
    with open(configFile, 'w') as configfile:
        config.write(configfile)

if __name__ == '__main__':

    # get the current directory
    currentDirectory = os.getcwd()

    # Generate Tkinter root
    root = Tkinter.Tk()

    # parse the config
    configFile = openINIFile()
    config,Parameters = readConfig(configFile)

    runGUI()