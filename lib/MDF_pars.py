#Channel name extraction functions

def extract_channel_name(arg, dict_loc, index, set, cg_index):
        # Extract a channel name out of the mdf recorded signals recorded by dPSPACE Bus Manager. (ex. The massage St is on the position before  /ISignal Value/St Value/IO_Signal)
        # ()://Signal Chain/IO Function View/Communication/Bus Manager/Bus Configuration/RestBus/Simulated ECUs/CAN_1/VCU/RX/PDUs/StsFbMsg_Id1/St/ISignal Value/St Value/IO_Signal
        tbl_dict=[]
        appearance=0
        char="/" 
        channel_name_pos = 3 # counting of the character "/" from the end of the signal string 
        channel_name=arg
        pos=arg.rindex(char)
        i=0
        #extract name phase 1 
        while i < channel_name_pos:
            pos=channel_name.rindex(char)
            channel_name=channel_name[:pos]
            i+=1
        #extract name phase 2 
        pos=channel_name.rindex(char)
        channel_name=channel_name[pos:]
        channel_name=channel_name[1:]
        
        #Inspect if more than one occurrence of a channel name    
        for i in range(len(dict_loc)): 
            tbl_dict.append((list(dict_loc.items())[i][0]))
        appearance=tbl_dict.count(channel_name)  
      
        if appearance!=0:
            channel_name=channel_name + "_" + str(set)+ str(cg_index+1)+ "_" + str(index+1)  
        
        return channel_name
    
def extract_non_IO_channel_name(arg, dict, index, set, cg_index):
    tbl_dict=[]
    appearance=0
    char_start="/"
    char_end="/"
    
    channel_name_pos = 1 # counting of the character "/" from the end of the signal string 
    channel_name=arg
   
    #extract name phase 1 
    channel_type_In="In"
    channel_type_Out="Out"
    channel_type_run="Runnable Function"
    channel_type_rep="TA_Replacevalue"
    
    
    if arg.find(char_start) == -1:
        channel_name = arg
        return channel_name 
    
    i=0
    while i < channel_name_pos:
        pos=channel_name.rindex(char_start)
        channel_name=channel_name[pos:]
        i+=1
        
    #extract name phase 2
    channel_name_chk=channel_name[1:]
    #Check if Matlab model In/Out sigbnals 
    if channel_name_chk.find(channel_type_In) != -1 or channel_name_chk.find(channel_type_Out) != -1:
        channel_name=arg
        pos=arg.rindex(char_start)
        i=0 
        while i < channel_name_pos:
            pos=channel_name.rindex(char_start)
            channel_name=channel_name[:pos]
            i+=1           
        pos=channel_name.rindex(char_end)
        channel_name=channel_name[pos:]
        channel_name=channel_name[1:]
    elif channel_name_chk.find(channel_type_run) != -1: 
        #Runtime processor model signals
        char_end="-"
        pos=channel_name.rindex(char_end)
        channel_name=channel_name[:pos]
        channel_name=channel_name[1:]
    elif channel_name_chk.find(channel_type_rep)  != -1:
        #Model request/replacment values 
        channel_name=arg
        channel_name_pos = 3
        pos=arg.rindex(char_start)
        i=0
        #extract name phase 1 
        while i < channel_name_pos:
            pos=channel_name.rindex(char_start)
            channel_name=channel_name[:pos]
            i+=1
        #extract name phase 2 
        pos=channel_name.rindex(char_end)
        channel_name=channel_name[pos:]
        channel_name=channel_name[1:]
        
    else:
        #Not identified channel
        #channel_name = "∑_Ch_Undef"+"_"+str(index)
        #channel_name = "∫_Ch_Undef"+"_"+str(index)
        #Create unique name
        channel_name = "Ch_Undef"+"_" + str(set)+ str(cg_index+1)+ "_" + str(index+1)  
        
    #Inspect if more than one occurrence of a channel name    
    for i in range(len(dict)): 
        tbl_dict.append((list(dict.items())[i][0]))
    appearance=tbl_dict.count(channel_name)  
      
    if appearance!=0:
        if channel_name.find("Ch_Undef") == -1:
            channel_name=channel_name + "_" + str(set)+ str(cg_index+1)+ "_" + str(index+1)  
    return channel_name
    
def chennel_type(arg):
    #Filter all IO_Signal-s out of all MDF channles
    channel_type="IO_Signal"
    char="/"  
    channel_name=arg
    #pos=arg.rindex(char)
    #act_channel_type=channel_name[pos+1:]
    #print(act_channel_type)
    if(channel_name.find(channel_type) != -1):
        return True
    else:
        return False
    
