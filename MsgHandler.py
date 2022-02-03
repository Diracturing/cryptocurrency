#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan 29 23:35:03 2022

@author: Julius
"""


class MsgHandler:
    def __init__(self):
        self.msg=""
    
        
    def getNextMsg(self,socket):
        """
        Waits until complete message have been recieved
        """
        
        while ':' not in self.msg:
            rec=socket.recv(2048)
            if rec==b'' or len(self.msg)>10:
                return
            else:
                self.msg=self.msg+rec.decode()
        
        index=self.msg.find(':')
        length=int(self.msg[:index])
        

        
        while len(self.msg)<=index+length:
            rec=socket.recv(2048)
            if rec==b'':
                return
            else:
                self.msg=self.msg+rec.decode()
            
        
        nextMsg=self.msg[index+1:index+1+length]
        self.msg=self.msg[index+1+length:]
        
        return nextMsg        


    def sendMsg(self,socket,msgToBeSent):
        """
        Adds the length to message before sending it
        """
        length=len(msgToBeSent)
        msgToBeSent=str(length)+":"+msgToBeSent
        socket.send(msgToBeSent.encode())
