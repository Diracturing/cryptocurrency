#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan 29 23:29:38 2022

@author: Julius
"""

import socket

import MsgHandler




def main():
    s=socket.socket()
    s.bind(('',16000))
    s.listen()

    cc,_=s.accept()

    Msg=MsgHandler.MsgHandler()
    while True:
        print(Msg.getNextMsg(cc))     
        

if __name__=="__main__":
    main()





























