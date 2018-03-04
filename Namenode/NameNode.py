import boto3
import socket
import sys
import math
import time
import os
import xmlrpclib
from threading import Thread, Lock
from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler
from anytree import Node, RenderTree


class NameNode:
    """
    Namenode needs to do two things
    1) Which blocks are part of which files
    2) Picking N different Datanodes to store each block (then return list of blocks and datanodes)
    3) only one writer at a time so we need a lock and thread for writeFile
    """
    def __init__(self):
        self.REPLICATION = 3 # pick 3 different datanodes to store each block by default
        self.BLOCK_SIZE = 256 # size of blocks for splitting
        self.fileD = {} # Dictionary for which blocks are part of which file
        self.blockD = {} # Dictionary for which datanodes are storing each block
        self.alive = {} # Dict for alive datanodes
        self.dnToBlock = {}
        self.mutex = Lock()
        self.home = Node("home") # a directory tree



    def createDirectory(self, path, dir):
        pathList = path.split("/")
        parent = pathList[len(pathList)]




    def writeFile(self, filename, blocks):  #pass in array of blocks as arguments

        uniqueFile = filename
        #need to find out how to make 'uniqueFile' the name of the file otherwise dictionary overwrites itself everytime method is called
        self.fileD['uniqueFile'] = blocks

        '''
        For each block from file, we need to apply replication factor 
        '''
        # For every element in blocks, part of key<uniqueFile>, Value<blocks>
        #place the block into N different datanodes either by default or updated REPLICATION
        #blockD = {blockName, datanodes}

        #return list of blocks and datanodes back to client

    # def blockReport(self, datanodeNum, blocks ):
    #     """
    #     The block report given from the data node
    #     Pass in all blocks as array assigned to the specific datanodeNumber e.g. datanode1,datanode2,etc
    #     :param datanodeNum:
    #     :param blocks:
    #     :return:
    #     """
    #     blockManager = xmlrpclib.ServerProxy('http://localhost:5000')
    #     print blockManager.get_blockID()
    #     print blockManager.get_DataNodeNumber()


    def checkTimes(self):
        for key in self.alive.keys():
            diff = time.time() - self.alive[key]
            if (diff > 10):
                del self.alive[key]

    def checkReplicas(self):
        notRep = [] #structure that holds 
        for blockID in self.dnToBlock.keys():
            if (len(self.dnToBlock[blockID]) != self.REPLICATION):
                notRep.append(blockID)
        return notRep

    def addFile(self, file_name, file_size):
        total_blocks = math.floor(file_size / self.BLOCK_SIZE)
        print("File Size: " + str(file_size))
        print("Number of Blocks: " + str(total_blocks))
        return total_blocks




# for testing
# s = Namenode()
# s.blockReport( 1, 2)
