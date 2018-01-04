import demotesting as PK
import datetime

Cline=''
root1='C:\\Users\\212634268\\Desktop\\krotas\\testing\\TGT' 
A=open("audit.txt","a")
root='C:\\Users\\212634268\\Desktop\\krotas\\testing\\GP_SVN' 
PK.Foldercrt(root,root1)
for path, subdirs, files in os.walk(root):
    for name in files:
        if name.endswith(".txt") or name.endswith(".sql"):            
            num=0
            check=['CREATE','INSERT','TRUNCATE','UPDATE','ANALYZE','DELETE']
            print(path)
            filename = os.path.join(path,name)
            f = open(filename, "r")
            t = open("tgt.txt","w")
            PK.tooldetails(t,name)
            comtflag=0
            for line in f:
                line=PK.rechange(line)          
                fr=line.split()
                if comtflag==1:t.write("\n") # give one line space comments 
                for i in fr:                
                    if "/*" not in i and comtflag==0:                        
                        if i.upper() in check or i in [x.lower() for x in check]:                        
                            if i.upper() in 'TRUNCATE':PK.trunc(line,t)
                            elif i.upper() in 'ANALYZE' :PK.anal(line,t,f)
                            elif i.upper() in 'CREATE' and 'TABLE' not in line.upper():
                                break
                            elif ';' in line:
                                Cline=PK.namecon(line)
                                t.writelines("\n"+str(Cline))                       
                           else                            
                                flag=0
                                Cline=PK.namecon(line)
                                t.writelines("\n"+str(Cline))
                                for line in f:                                
                                    if ';' in line:                                                                               
                                        Cline=PK.namecon(line)
                                        t.write(str(Cline)+" ")
                                        flag=1
                                        break
                                                               
                                    if flag == 1:                                    
                                        break
                                    else : 
                                        Cline=PK.namecon(line)
                                        t.write(str(Cline))
                            t.write("\n"+".IF ERRORCODE != 0 THEN .EXIT "+str(num)+" ;\n\n")                    
                            num=num+1
                    elif "/*" in i or comtflag==1:                    
                        comtflag=1
                        if i in '*/':                        
                            t.write(str(i)+"\n\n")
                            comtflag=0
                        else:                        
                            t.write(str(i)+" ")
            
            f.close()
            t.close()
            spname=name.split('.')
            tgt=str(spname[0])+"_tgt_T"
            temp=path.split(root)
            print(tgt)
            if temp[1] ==' ':                                
                path1=root1+'\\'+str(tgt)
            else :
                path1=root1+str(temp[1])+'\\'+str(tgt)
            replacements = {'WITHOUT TIME ZONE':'',';':' ;'}
            with open('tgt.txt') as infile, open(path1, 'w') as outfile:            
                for line in infile:                
                    for src, target in replacements.items():                
                        line = line.replace(src, target)
                    outfile.write(line)
            A.write(str(os.path.join(path, name))+"\t"+str(path1)+"\t"+str(datetime.datetime.now())+"\n")
            

A.close()         
             