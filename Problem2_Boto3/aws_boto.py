import boto3
from pathlib import Path
from PIL import Image
import argparse

def check_trpy_pix(inp_buc,oup_buc):
    try:
        s3 = boto3.resource('s3')
    except Exception as E:
        return "\nFailed to Establish connection !\nCheck Credenitals, Config File, Network and region"

    src_bck = inp_buc #'imgwithtransp' source bucket
    dest_bck = oup_buc # 'bucwithoutransp' destination bucket

    bucket = s3.Bucket(src_bck).objects.all() # fetch bucket content
  
    tot = 0  #Total files detected
    trpy = 0 #files detected with Transparency
    for x in bucket:
        tot=tot+1
        flnm=str(Path.cwd()/Path(str(x.key))) #set file name to store local
        
        try:
            s3.meta.client.download_file(src_bck, str(x.key),flnm) #download file locally, bucket, key and local filepath passed
        except Exception as E:
            return "\nDownload failed !\nTry Again"
        
        try:
           img = Image.open(flnm) # opening Image
        
        except PIL.UnidentifiedImageError :   
            return "Error ! Corrupted / File Unreadable"  #Corrupted file detected 
       
        except Exception as E:  
            return "File Not found or Unidentified Format"  #Missing or Wrong Format error

        #checking transparency if image is Palette mode
        if (img.mode == "P" or img.mode == "PA"):
            for _, index in img.getcolors():
                    if (index == transparent):
                        trpy=trpy+1
                        break
            with open ('log.txt','a') as f:  #logging
                 f.write(str(x.key)+" xTransparent Pixel Detected\n")
                            
        #checking transparency if image is Palette mode
        elif (img.mode == "RGBA"):
            #checking extreme values 
            extrm = img.getextrema()
            if (extrm[3][0] < 255):
                trpy=trpy+1
                with open ('log.txt','a') as f: #logging 
                    f.write(str(x.key)+" Transparent Pixel Detected\n")
                
        # no transparecy detected copy to dest bucket            
        else:
            copy_source = {'Bucket': 'imgwithtransp','Key': x.key} #setting source file
            s3.meta.client.copy(copy_source, dest_bck,x.key) # copying
    return "Found "+str(tot)+" files\n- "+str(tot - trpy)+" has been moved\n- "+str(trpy)+" has transparent pixels\n- log Generated     at "+str(Path.cwd())

#argparse 
parser = argparse.ArgumentParser(
                    prog = 'BOTO3 Transpy Check',
                    description = 'CHECK FOR IMAGE WITHout TRANSPARENCY pixel AND STORE IN destINATION buCKET  ',
                    epilog = 'Have fun')
parser.add_argument('-i', '--inp_buc',  type=str,
                    help = 'Input Source Bucket Name', required = True)      #input bucket arguement
parser.add_argument('-o', '--oup_buc',  type=str ,required = True , help = 'Enter Destination Bucket name')   #output bucket arguement

parser.add_argument(dest='result',action ='store_const',const = check_trpy_pix)   #output 
args = parser.parse_args()

print(args.result(args.inp_buc,args.oup_buc))
