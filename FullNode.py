#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 24 22:41:22 2022

@author: Julius
"""

import threading
import socket
import sys
import Block
import MsgHandler
import Transaction as T

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
import datetime
import json

initIp="10.0.2.5"  # the ip of the first starting full node

port=16000
connections=[]
if len(sys.argv)==1: ### The first starting node should run with single arbitary argument
    connections.append(initIp)
socketConnections=[]  
transactions=[]
transactionsLock=threading.Lock()


# =============================================================================
# Start the node by generating keys, create mining thread, user input thread, thread to connect to other peers and start to listen for new incoming connections
# =============================================================================
def p2p():
    priv1 = ec.generate_private_key(ec.SECP384R1())
    pub1=priv1.public_key().public_bytes(encoding=serialization.Encoding.PEM,format=serialization.PublicFormat.SubjectPublicKeyInfo) 
    
    threading.Thread(target=listenToUser,daemon=True,args=(priv1, pub1,)).start()
    threading.Thread(target=mining,daemon=True,args=(priv1,pub1,)).start()
    
    if len(connections)!=0:
        threading.Thread(target=connectToPeers,daemon=True,args=(initIp,)).start() #
    
    s=socket.socket()
    s.bind(('',port))
    s.listen()
    

    while True:
        (client,addr)=s.accept()
        socketConnections.append(client)
        threading.Thread(target=connection,daemon=True,args=(client,addr[0],)).start() #
        

    s.close()

## *currently just a quick test
## *fix how to easy do transactions (implement for example a wallet)
def listenToUser(priv1,pub1):
    msgHandler=MsgHandler.MsgHandler()

    while True:
        cmd=input()
        if cmd=="transaction":
            txid=json.loads(Block.longestChain().block)["transactions"][0]["txid"]
            transaction=T.transaction(txid, priv1, pub1, 5)
            with transactionsLock:
                transactions.append(transaction)
            for peer in socketConnections:
                msgHandler.sendMsg(peer,"transaction")   #peer.send("add".encode())
                msgHandler.sendMsg(peer, transaction)  #peer.send(block.encode())
        elif cmd=="show":
            print(Block.longestChain().block)
            
            
        


def connectToPeers(addr):
    msgHandler=MsgHandler.MsgHandler()
    print("connect to:")
    print(addr)
    s=socket.socket()
    s.connect((addr,port))
    socketConnections.append(s)
    while True:
        peer=msgHandler.getNextMsg(s)
        if peer==None:
            #if disconnect
            return
        if peer=="end":
            listen(s,addr,msgHandler)
            return
        elif peer not in connections:
            connections.append(peer)
            threading.Thread(target=connectToPeers,daemon=True,args=(peer,)).start()
            

# =============================================================================
# if new incoming connection then send it all the peer addresses
# =============================================================================
def connection(cc,addr):
    msgHandler=MsgHandler.MsgHandler()
    for i in range(len(connections)):
        msgHandler.sendMsg(cc, connections[i])
    msgHandler.sendMsg(cc,"end")   
    connections.append(addr)

    listen(cc,addr,msgHandler)

    
# =============================================================================
# After connecting to a peer listen for further actions
# *problem if init block not consistent
# *might want to create array for everyone in connecttopeers and then might collect all blocks  
# =============================================================================
def listen(cc,addr,msgHandler):
    if(addr==initIp):
        #cc.send("blockchain".encode())
        #cc.send(Block.blockChain.block.encode())
        ### send all blocks
        pass

    
    while True:
         print("w8ing for msgs...")
         rec=msgHandler.getNextMsg(cc)   
         if rec==None:
             cc.close()
             connections.remove(addr)
             socketConnections.remove(cc)
             return
         else:
             if rec=="blockchain":
                 while True:
                     rec=msgHandler.getNextMsg(cc)  
                     if rec==None:
                         cc.close()
                         connections.remove(addr)
                         socketConnections.remove(cc)
                         return
                     else:
                         if rec=="end":
                             break
                         else:
                             Block.addToTree(rec)
             
             elif rec=="add":
                 rec=msgHandler.getNextMsg(cc)   
                 print("block recieved")
                 if(Block.addToTree(rec)): ## should look if it is longest
                     print("correct block added")
                     Block.keepMining=False
                 else:
                     print("incorrect block")
             elif rec=="transaction":
                 rec=msgHandler.getNextMsg(cc)
                 with transactionsLock:
                     transactions.append(rec)
             else:
                 print(rec)
    

def mining(priv1,pub1):
    while True:
        print("starting to mine")
        global transactions
        with transactionsLock:
            block=Block.CreateBlock(transactions, pub1, 5) ## Later need change to limit size of transactions
            transactions=[]
        if Block.keepMining==True:
            print("Successful block")
            Block.addToTree(block)
            blockp2p(block)
        Block.keepMining=True
            
        
def blockp2p(block):
    msgHandler=MsgHandler.MsgHandler()
    for peer in socketConnections:
        msgHandler.sendMsg(peer,"add")   
        msgHandler.sendMsg(peer, block)  
    
    

def main():
    p2p()


if __name__=="__main__":
    main()

