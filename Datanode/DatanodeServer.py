"""
DatanodeServer.py
"""
from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler
from DataNode import DataNode
from modules import dnRPCClient as dnRPCClient
from modules import nnRPCClient as nnRPCClient
import time
import os
from thread import *
import xmlrpclib
from modules import BlockDivider

######### GLOBAL VARIABLES #########
PORT = 8888
HOST = ""

NAMENODE_HOST = ""
NAMENODE_PORT = "8000"

MY_IP = ""  # public ip

datanode = None  #this is the datanodes structure


# Restrict to a particular path.
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)


# Create server
server = SimpleXMLRPCServer((HOST, PORT), requestHandler=RequestHandler)
server.register_introspection_functions()

######### HEART BEAT FUNCTIONS #########

#repeat this function every 10 seconds
def heartBeat():
    global MY_IP
    global NAMENODE_HOST
    global NAMENODE_PORT
    
    while 1:
        try:
            time.sleep(2)
            nn = nnRPCClient.nnRPCClient(NAMENODE_HOST, NAMENODE_PORT)
            nn.receiveHeartBeat(MY_IP)
        except:
            continue

#repeat this function every 10 seconds to send block report
def sendBlockReport():
    global MY_IP
    global datanode
    global NAMENODE_HOST
    global NAMENODE_PORT
    
    while 1:
        time.sleep(4)
        try: #attempt to connect to the server
            nn = nnRPCClient.nnRPCClient(NAMENODE_HOST, NAMENODE_PORT)
            #send datanodes blocks
            nn.receiveBlockReport(MY_IP, datanode.blocks)
        except:
            continue
    

######### BEGIN RPC FUNCTIONS #########

# Register a function under a different name
def hello_world():
    return "Hello, Datanode!\n"

#receive a block from anybody who calls this function
# primarily used by datanode
def receiveBlock(blockID, blockData):
    global datanode
    datanode.receiveBlock(blockID, blockData)
    print('Block received! ' + blockID)
    #call datanode structure to write this to hdd
    return os.getcwd()

def giveBlock(blockID):
    global datanode
    return datanode.giveBlock(blockID)


def removeBlock(blockID):
    global datanode
    datanode.removeBlock(blockID)
    return True

# used by namenode for targeted replications
def targetBlock(blockID, dnIp):
    global datanode
    targetDn = dnRPCClient.dnRPCClient(dnIp, 8888)
    #path = "/home/ec2-user/blocks/" + blockID
    path = datanode.block_dir + blockID #'/Users/alex/Developer/SUFS/blocks/' + blockID
    block_divider = BlockDivider.BlockDivider(4000000)

    smallblocks = block_divider.split_file('', path, '')
    for smallblock in smallblocks:
        obj = None
        with open(smallblock, "rb") as handle:
            obj = xmlrpclib.Binary(handle.read())
        #call datanode structure to write this to hdd
        targetDn.receiveBlock(blockID, obj)
        os.remove(smallblock)
    return True

######### CALL THIS FUNCTION FIRST VIA NAMENODE RPC #########

#receive my ip information from namenode as well as assignment to namenode
#begin heartbeat thread
#begin block thread
#instantiates the datanode structure
def receiveNNIp(nnIp, myIp):
    print ("received namenode ip, starting heartbeats")
    global NAMENODE_HOST 
    NAMENODE_HOST = nnIp
    global MY_IP 
    MY_IP = myIp

    #instantiate datanode stuff here after we get ips
    global datanode 
    datanode = DataNode(myIp, nnIp, 8000)

    #begin heartbeating
    start_new_thread(heartBeat,())
    #begin blockreport sending
    start_new_thread(sendBlockReport,())
    return True


# Register hello world function
server.register_function(hello_world)
server.register_function(receiveBlock)
server.register_function(giveBlock)
server.register_function(removeBlock)
server.register_function(targetBlock)
server.register_function(receiveNNIp)
# Run the server's main loop
print("Starting Datanode Server on port " + str(PORT) + "...")
server.serve_forever()
