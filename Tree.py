#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan 22 22:59:52 2022

@author: Julius
"""

class Tree:
    def __init__(self,parent,block):
        self.parent=parent
        self.children=[]
        self.block=block
        
    def addchild(self,child):
        self.children.append(child)
        
        
    def getChildren(self):
        return self.children
    
    def getParent(self):
        return self.parent
        

if __name__ == "__main__":
    T=Tree(0,1)
    T.addchild(Tree(T,1))
    T.getChildren()




        
