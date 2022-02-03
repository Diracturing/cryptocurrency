#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 14 23:05:16 2022

@author: Julius
"""
import json
import socket
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
import datetime
import base64


# =============================================================================
#     Coinbase transaction (every block starts with it)
# =============================================================================
def transaction0(pub,value):     
    tran={}
    tran["vin"]=[]
    tran["vin"].append({})
    tran["vin"][0]["coinbase"]=0
    
    
    tran["vout"]=[]
    tran["vout"].append({})
    tran["vout"][0]["value"]=value
    tran["vout"][0]["pubkey"]=base64.b64encode(pub).decode("utf-8")
    tran["time"]=str(datetime.datetime.now())
    
    tmp=json.dumps(tran)
    

    digest = hashes.Hash(hashes.SHA256())
    digest.update(tmp.encode())
    
       
    
    tran["txid"]=base64.b64encode(digest.finalize()).decode("utf-8") 

    return json.dumps(tran)
    

    
# =============================================================================
# Regular transaction
# *handle same txid somewhere (in wallet?)
# =============================================================================
def transaction(txid,pr,recpub,value): 
    tran={}
    tran["vin"]=[]
    tran["vin"].append({})
    tran["vin"][0]["txid"]=txid
    tran["vin"][0]["index"]=0
    
    
    
    tran["vout"]=[]
    tran["vout"].append({})
    tran["vout"][0]["value"]=value
    tran["vout"][0]["pubkey"]=base64.b64encode(recpub).decode("utf-8")
    tran["time"]=str(datetime.datetime.now())
    
    tmp=json.dumps(tran)
    
    sig= pr.sign((tmp+txid).encode(),ec.ECDSA(hashes.SHA256()))
    tran["vin"][0]["sig"]=base64.b64encode(sig).decode("utf-8") 

    
    
    tmp=json.dumps(tran)
    digest = hashes.Hash(hashes.SHA256())
    digest.update(tmp.encode())
    tran["txid"]=base64.b64encode(digest.finalize()).decode("utf-8") 
    
    return json.dumps(tran)

# =============================================================================
# check if a transaction is valid    
# =============================================================================
def check(t0,t1):
    t0=json.loads(t0)
    t1=json.loads(t1)
    
    txid=t0["txid"]
    pub=t0["vout"][0]["pubkey"]

    
    pub = serialization.load_pem_public_key(base64.b64decode(pub.encode("utf-8")),)

    
    
    txid1=t1["txid"]
    sig=base64.b64decode(t1["vin"][0]["sig"].encode("utf-8"))


    del t1["txid"]
    del t1["vin"][0]["sig"]

    tmp=json.dumps(t1)
    
    
    try:
        pub.verify(sig, (tmp+txid).encode(), ec.ECDSA(hashes.SHA256()))
    except:
        return False
    
    return True


def main():
    priv1 = ec.generate_private_key(ec.SECP384R1())
    priv2 = ec.generate_private_key(ec.SECP384R1())
    pub1=priv1.public_key().public_bytes(encoding=serialization.Encoding.PEM,format=serialization.PublicFormat.SubjectPublicKeyInfo)
    pub2=priv2.public_key().public_bytes(encoding=serialization.Encoding.PEM,format=serialization.PublicFormat.SubjectPublicKeyInfo)
    
    t0=transaction0(pub1,5)

    dic=json.loads(t0)
    t1=transaction(dic["txid"],priv1,priv2.public_key().public_bytes(encoding=serialization.Encoding.PEM,format=serialization.PublicFormat.SubjectPublicKeyInfo),5)
    print(check(t0,t1))
    
    
    
if __name__ == "__main__":
    main()