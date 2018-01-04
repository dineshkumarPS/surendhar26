"""
import redis
r = redis.StrictRedis(host='localhost', port=6379, db=0)
k=r.get(a)
k=k.decode("utf-8")
print(k) 


import redis
import re

red = redis.StrictRedis(host='localhost', port=6379, db=0)
def namecon(line):    
    word=re.split("(\W)",line)
    nline=""
    ind=0
#print((word))
    while ind < len(word):
        if word[ind] ==':' and word[ind+2]==':':
            word[ind]='::'
            word[ind+2]=''
        if red.exists(word[ind]):
            temp=red.get(word[ind].upper())
            word[ind]=temp.decode("utf-8")
        ind=ind+1           
    print(word)
    if '::' in word:
        ind=0
    while ind<len(word):  
        if word[ind]=='::':
            if word[ind-2] == '.':
                word[ind-3]='CAST('+str(word[ind-3])
            else:
                word[ind-1]='CAST('+str(word[ind-1])
            word[ind]=' AS '
            if len(word) > ind+4:
                if word[ind+4]!='.' :       
                    word[ind+5]=str(word[ind+5])+')'
            else:
                word[ind+3]=str(word[ind+3])+')'
            #print("called")    
        ind=ind+1
    #print(word)
    for ind_word in word:
        nline=nline+str(ind_word)
    return nline

line="A.B::C_D"
nline=namecon(line)        
print(nline)
"""
import re
ptr=1
curname=1
loopcount=0
wvar={}
def looping(line,t,loopcount):
    nline=""
    global ptr,curname
    word=re.split("(\W)",line)
    #print(word)
    var=word[2]
    word[2]="CUR_PTR"+str(ptr)
    ptr+=1
    word[4]="AS"
    word[6]="CURSORNAME"+str(curname)
    curname+=1
    word[7]=" "
    word[9]=""
    l=len(word)
    #print(word)
    
    i=0
    while i < (l-6):
        nline=nline+str(word[i])
        i+=1
   # print(nline) 
       
    nline=nline.replace("''","'")
    print(nline)
    i=0
    temp=""
    print(loopcount)
    while (i<loopcount):
        temp+="  "
        i+=1
    t.write(str(loopspc(loopcount))+str(nline)+"\n")
    t.write(str(loopspc(loopcount))+"DO"+"\n")
    kline="SET "+str(var)+" = CUR_PTR" +str(ptr-1)+"."+str(word[12]+" FOR ")
    #print(kline)
    t.write(str(loopspc(loopcount))+str(kline)+"\n")
    
def eq(fline,t,loopcount):    
    fline=fline.replace(':=','=')
    t.write(str(loopspc(loopcount))+"SET "+str(fline))  

def loopspc(loopcount):
    i=0
    temp=""
    #print(loopcount)
    while (i<loopcount):
        temp+="    "
        i+=1
    return temp
def whileloop(line,t,loopcount):    
    global ptr,curname,wvar
    word=re.split("(\W)",line)
    #print(word)
    var=word[2]
    t.write(str(loopspc(loopcount))+"SET "+str(var)+" = "+str(word[6])+";\n")
    t.write(str(loopspc(loopcount))+"WHILE ("+str(var)+"<="+str(word[10])+")\n")
    t.write(str(loopspc(loopcount))+"DO") 
    wvar[loopcount]=var
    #print(loopcount)
    

    
def forcon(line,s,t):
    global loopcount
    if ".." in line:
        loopcount+=1
        whileloop(line,t,loopcount)
       
    else:
        loopcount+=1
        looping(line,t,loopcount)
        
    for fline in s:
        
        if 'FOR' in fline.upper():
            if ".." in fline:
                loopcount+=1
                whileloop(fline,t,loopcount)
                
            else:
                loopcount+=1
                looping(fline,t,loopcount)
                
        elif '=' in fline and '--' not in fline and 'IF(' not in fline:
            eq(fline,t,loopcount)
        elif 'END LOOP' in fline:
            if loopcount>=1 and loopcount in wvar:
                t.write(str(loopspc(loopcount))+"SET "+wvar[loopcount]+"="+wvar[loopcount]+"+1;\n")
                t.write(str(loopspc(loopcount))+"END WHILE;\n\n")
                loopcount-=1
                if loopcount==0:
                    break   
            elif loopcount>=1:
                t.write(str(loopspc(loopcount))+"END FOR;\n\n")
                loopcount-=1
                if loopcount==0:
                    break
            else:
                t.write(fline)
                break
        elif 'EXECUTE' in fline.upper():
            fline=fline.upper().replace("EXECUTE","CALL dbc.SysExecSQL")
            t.write(str(loopspc(loopcount))+str(fline))
        else:
            fline=fline.replace('LOOP','')
            t.write(str(loopspc(loopcount))+str(fline))
            
def dec(line,s,t):
    t.write("BEGIN \n")
    for line in s:
        if "BEGIN" in line:
            break
        elif len(line)>1:
            #print(len(line))
            Cline=PK.namecon(line)
            t.write("DECLARE "+str(Cline))
        
            
        
import demotesting as PK
f = open("NF.txt", "r")
t = open("tgt.txt","w")
flagbd=0

for line in f:
    line=PK.rechange(line)
    if 'DECLARE' in line.upper():
        dec(line,f,t)
    elif '$BODY$' in line and flagbd==0:
        flagbd=1
    elif 'FOR' in line.upper() and '--FOR' not in line:
        forcon(line,f,t)
    elif 'TRUNCATE' in line.upper():PK.trunc(line,t)
    elif 'ANALYZE' in line.upper() :PK.anal(line,t,f)
    elif '$BODY$' in line.upper() : break
    elif  'ERROR_MESSAGE' in line.upper():
        print("error msg is there")
    elif '=' in line:
        eq(line,t,loopcount)
    else:        
        Cline=PK.namecon(line)
        t.write(str(Cline))
print(wvar)
f.close()
t.close()

























