import boto3
import botocore
from pathlib import Path
from PIL import Image
import argparse
from io import BytesIO
import time

def check_trpy_pix(inp_buc,oup_buc,aws_reg,acc_key,sec_key):
    
    src_bck = inp_buc #'imgwithtransp' source bucket
    dest_bck = oup_buc # 'bucwithoutransp' destination bucket

    #check if src and destination same
    if(src_bck == dest_bck):
        return "Source Bucket and Destination Bucket cannot be same."
    
    try:

        if(aws_reg == "" and  acc_key  == "" and sec_key == "" ):
            s3 = boto3.resource('s3')
             # AWS S3 Object with system config
        elif (aws_reg != "" and  acc_key  != "" and sec_key != "" ):
            # AWS S3 Object with Custom config
            s3 = boto3.resource('s3', aws_access_key_id= acc_key, aws_secret_access_key= sec_key , region_name= aws_reg)
        else:
            return "Input all: Region (-r) Acceess Key (-a) Secret Key (-p)"

                
        s3.meta.client.head_bucket(Bucket=src_bck) # check & fetch bucket content
        bcket = s3.Bucket(src_bck).objects.all()
        
    #error handling credential and not found
    except botocore.exceptions.ClientError as err :
        if(err.response['Error']['Message'] == "Not Found"):
            return "Source Bucket Not Found"
        elif (err.response['Error']['Message'] == "Forbidden"):
            return "Wrong Credentials"
    
    try:
        s3.meta.client.head_bucket(Bucket=dest_bck) # check destination bucket
    except botocore.exceptions.ClientError as err:
        return "No Such Destination Bucket - If bucket not created : Please Create"
  
    tot = 0  #Total files detected
    trpy = 0 #files detected with Transparency
    for x in bcket:
        tot=tot+1
        flnm=str(Path.cwd()/Path(str(x.key))) #set file name to store local
        try:
            img_bio = s3.Object(bucket_name=src_bck, key= x.key).get()["Body"].read() # Fetch image data
        
        #try:
            #s3.meta.client.download_file(src_bck, str(x.key),flnm) #download file locally, bucket, key and local filepath passed
        except Exception as E:
            return "\nDownload failed !\nTry Again"
       
        try:
            img = Image.open(BytesIO(img_bio)) #store using IO buffer and open image
            #img = Image.open(flnm) # opening Image
        
        except PIL.UnidentifiedImageError :   
            return "Error ! Corrupted / File Unreadable"  #Corrupted file detected 
       
        except Exception as E:  
            return "File Not found or Unidentified Format"  #Missing or Wrong Format error
            

        #checking transparency if image is Palette mode
        if (img.mode == "P" or img.mode == "PA" ):
            for _, index in img.getcolors():
                    if (index == transparent):
                        trpy=trpy+1
                        break
            with open ('log.txt','a') as f:  #logging
                 f.write(str(x.key)+" Transparent Pixel Detected\n")
                            
        #checking transparency if image is Palette mode
        elif (img.mode == "RGBA"):
            #checking extreme values 
            extrm = img.getextrema()
            if (extrm[3][0] < 255):
                trpy=trpy+1
                with open ('log.txt','a') as f: #logging 
                    f.write(str(x.key)+" Transparent Pixel Detected\n")
        elif('transparency' in img.info):
            trpy=trpy+1
            with open ('log.txt','a') as f: #logging 
                f.write(str(x.key)+" Transparent Pixel Detected\n")
                
        # no transparecy detected copy to dest bucket            
        else:
            copy_source = {'Bucket': 'imgwithtransp','Key': x.key} #setting source file
            try:
                s3.meta.client.copy(copy_source, dest_bck,x.key) # copying
            except Exception as E:
                return "\nCopy Failed"
    with open ('log.txt','a') as f: #logging
        f.write(str(time.ctime()))
            
    return "Found "+str(tot)+" files\n- "+str(tot - trpy)+" has been moved\n- "+str(trpy)+" has transparent pixels\n- log Generated     at "+str(Path.cwd())

#argparse 
parser = argparse.ArgumentParser(
                    prog = 'Transparency_Check',
                    description = 'CHECK FOR IMAGE WITHout TRANSPARENCY pixel AND STORE IN destINATION buCKET  ',
                    epilog = 'Have fun')

parser.add_argument('-r', '--aws_reg',  type=str ,default = ""  , help = 'Enter Bucket Region') # Arg for region
parser.add_argument('-a', '--acc_key',  type=str ,default = ""  , help = 'Enter AWS ACCESS KEY ID') #Arguement for Access ID
parser.add_argument('-p', '--sec_key',  type=str ,default = ""  , help = 'Enter AWS SECRET KEY') # Arguement for Secret Key
parser.add_argument('-i', '--inp_buc',  type=str, required = True , help = 'Input Source Bucket')      # input bucket arguement
parser.add_argument('-o', '--oup_buc',  type=str ,required = True , help = 'Enter Destination Bucket name')#output bucket arguement

parser.add_argument(dest='result',action ='store_const',const = check_trpy_pix)   #output 
args = parser.parse_args()

print(args.result(args.inp_buc,args.oup_buc,args.aws_reg,args.acc_key,args.sec_key))
