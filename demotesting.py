import os
import re
import redis
#CONNECT TO REDIS 0 DATABASE
red = redis.StrictRedis(host='localhost', port=6379, db=0)

# Write the tool name and Source file name in every File
def tooldetails(t,name):
    t.write("Source file Name : "+str(name)+"\n")
    t.write("This file is created by AUTOBOAT \n\n")
    
#CONVERT the Truncate into DELETE ALL Query     
def trunc(line,t):
    line=line.upper()
    nline=line.replace(";"," ALL ;")
    nline=nline.replace("TRUNCATE TABLE","DELETE FROM")
    nline=nline.replace("TRUNCATE","DELETE FROM")
    nline=namecon(nline)
    t.write("\n"+str(nline)+"\n")
    
#CONVERT the ANALYZE  into COLLECT ALL Query    
    
def anal(line,t,f):
    line=line.upper()
    nline=line.replace('ANALYZE','COLLECT STATISTICS on')
    nline=nline.replace("("," COLUMN (")
    nline=namecon(nline)
    t.write(str(nline))
    
#Folder Hierarchical Creation
    
def Foldercrt(root,root1):    
    for path, subdirs, files in os.walk(root):
        for name in subdirs:       
            temp=path.split(root)
            if temp[1] == '':
                root12=str(root1)+"\\"+str(name)
                #print(os.path.exists(root12))
                if not os.path.exists(root12):                    
                    os.makedirs(root12) 
                    #print(root12)                 
            else:
                root12=str(root1)+str(temp[1])+"\\"+str(name)
                #print(os.path.exists(root12))
                if not os.path.exists(root12):                    
                    os.makedirs(root12) 
                    #print(root12)


#Check the Keyword present or not if the Replace with the TD keywords
#And the CAST function CONVERTING 

def namecon(line):    
    word=re.split("(\W)",line)
    nline=""
    ind=0
#print((word))
    while ind < len(word):
        if word[ind] ==':' and word[ind+2]==':':
            word[ind]='::'
            word[ind+2]=''
        if red.exists(word[ind].upper()):
            temp=red.get(word[ind].upper())
            word[ind]=temp.decode("utf-8")
        ind=ind+1           
    #print(word)
    if '::' in word:
        ind=0
    while ind<len(word):  
        if word[ind]=='::':
            if word[ind-2] == '.':
                word[ind-3]='CAST('+str(word[ind-3])
            else:
                word[ind-1]='CAST('+str(word[ind-1])
            word[ind]=' AS '
            if word[ind+4]!='.' :                
                word[ind+3]=str(word[ind+3])+')'
            else:
                word[ind+5]=str(word[ind+5])+')'
            print("called")    
        ind=ind+1
    #print(word)
    for ind_word in word:
        nline=nline+str(ind_word)
    return nline



def rechange(line):
    line=line.replace("*/"," */ ")
    nline=line.replace('CHARACTER VARYING',"VARCHAR")
    nline=nline.replace(' :: ','::')
    return nline


def distinct(line):  
    i=0
    j=0
    word=re.split("(\W)",line)
    nline=""
    while i < len(word):
        if word[i].upper()=='IS' and word[i+2].upper()=='DISTINCT':
            word[i-2]='COALESCE('+str(word[i-2])+",'#')"
            word[i]='<>'
            word[i+2]=''
            word[i+4]='COALESCE('+str(word[i+4])+",'#')"
        elif word[i].upper()=='IS' and word[i+4].upper()=='DISTINCT' and word[i+2].upper()=='NOT':
            word[i-2]='COALESCE('+str(word[i-2])+",'#')"
            word[i]='='
            word[i+2]=''
            word[i+4]=''
            word[i+5]=''
            word[i+6]='COALESCE('+str(word[i+6])+",'#')"
        i=i+1
    while j < len(word):
         nline=nline+str(word[j])
         j+=1
    return nline
