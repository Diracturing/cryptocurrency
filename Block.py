#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 21 21:35:05 2022

@author: Julius
"""
import Transaction as T


import json
import socket
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
import datetime
import base64
import Tree


hardness=24## how hard the puzzle should be
blockChain=Tree.Tree(0,0)
keepMining=True


def CreateBlock(transactions,pub,value):   
    if blockChain.block==0:
        prevBlockHash=0
    else:
        prevBlockHash=base64.b64encode(hash(longestChain().block)).decode("utf-8")
    
    coinbase=T.transaction0(pub, value)
    

    block={}
    block["block header"]={}
    block["block header"]["previous block hash"]=prevBlockHash
    block["block header"]["timestamp"]=str(datetime.datetime.now())
    
    block["transactions"]=[]
    block["transactions"].append(json.loads(coinbase))
    

    for i in transactions:
        block["transactions"].append(json.loads(i))

    
    while(mine(json.dumps(block)) and keepMining):
        block["transactions"][0]["vin"][0]["coinbase"]+=1
    
    return json.dumps(block)

# =============================================================================
# return the node which is last in the longest chain
# =============================================================================
def longestChain():
    arr=blockChain.getChildren()

    while len(arr)!=0:
        arr2=[]
        for i in range(len(arr)):
            arr2+=arr[i].getChildren()
        if(len(arr2)!=0):
            arr=arr2
        else:
            return arr[0]

    return blockChain

def hash(data):
    digest = hashes.Hash(hashes.SHA256())
    digest.update(data.encode())
    
    return digest.finalize()

# =============================================================================
# try solve the mining puzzle    
# =============================================================================
def mine(block):
    s=hash(block)

    s=int.from_bytes(s, "big")
    if s<(2**(256-hardness)):
        return False
    else:
        return True

# =============================================================================
# Try find the block with specified hash
# =============================================================================
def search(Tree,prevHash):
    if base64.b64encode(hash(Tree.block)).decode("utf-8") ==prevHash:
        return Tree
    else:
        if len(Tree.getChildren())==0:
            return 0
        else: 
            for i in Tree.getChildren():
                s=search(i, prevHash)
                if s!=0:
                    return s              
    return 0
                
# =============================================================================
# check if block did solve the puzzle
# =============================================================================
def puzzleCheck(block):
    if int.from_bytes(hash(block), "big")<(2**(256-hardness)):
        return True
    else:
        return False

#check uniqueness of block?
#Might add static first block
def addToTree(block):
    if blockChain.block==0:
        if puzzleCheck(block):
            blockChain.block=block
            return True
        else:
            return False
    
    prevHash=json.loads(block)["block header"]["previous block hash"]
    parent=search(blockChain,prevHash)
    if(parent!=0 and puzzleCheck(block) and transactionCheck(block, parent)):
        parent.addchild(Tree.Tree(parent, block))
        return True
    return False
        

#multi spending if current block contain many of the same txid
def transactionCheck(block,initparent):
    block=json.loads(block)["transactions"]
    
    for i in range(len(block)):
        if i!=0:
            if block[i]["vout"][0]["value"]!=5:
                return False
    
    
    for i in range(len(block)):
        parent=initparent
        goToNextTransaction=False
        
        if i!=0:
            txid=block[i]["vin"][0]["txid"]
            while True:
                transactions=json.loads(parent.block)["transactions"]
                for j in range(len(transactions)):
                    if j!=0:
                        if transactions[j]["vin"][0]["txid"]==txid:
                            return False 

                    if transactions[j]["txid"]==txid:
                        if not T.check(json.dumps(transactions[j]), json.dumps(block[i])):
                            return False
                        goToNextTransaction=True
                        break
                if goToNextTransaction==True:
                    break
                parent=parent.getParent()
                if parent==0:
                    return False
                           
    return True
    


def main():
    
    priv1 = ec.generate_private_key(ec.SECP384R1())
    priv2 = ec.generate_private_key(ec.SECP384R1())
    pub1=priv1.public_key().public_bytes(encoding=serialization.Encoding.PEM,format=serialization.PublicFormat.SubjectPublicKeyInfo)
    pub2=priv2.public_key().public_bytes(encoding=serialization.Encoding.PEM,format=serialization.PublicFormat.SubjectPublicKeyInfo)
    

    #0=T.transaction("32",priv1,pub2,5)
    b1=CreateBlock([],pub1,5)
    print(b1)
    print("")
    print(addToTree(b1))
    
    
    
    t1=T.transaction(json.loads(b1)["transactions"][0]["txid"],priv1,pub2,5)

    b2=CreateBlock([], pub2, 5) #base64.b64encode(hash(b1)).decode("utf-8"))

    t2=T.transaction(json.loads(b2)["transactions"][0]["txid"],priv2,pub1,5)

    #p=transactionCheck(b2,blockChain)
    #print(p)
    
    print(addToTree(b2))

    
    b3=CreateBlock([], pub1, 5)
    print(addToTree(b3))

    b4=CreateBlock([t1,t2], pub1, 5)
    #print(transactionCheck(b4, longestChain()))
    
    
    print(addToTree(b4))

    
    
    
if __name__ == "__main__":
    main()