#import libraries
import numpy as np 
import cv2
import PIL
from PIL import Image, ImageOps , ImageDraw
import argparse
from pathlib import Path

#Opening and Type Check
def tych (in_img,op_dir):
    
    face = 0
    
    try:
       prep = Image.open(in_img).convert('RGB') # opening Image & convert to RGB
    
    except PIL.UnidentifiedImageError :   
        return "Error ! Corrupted / File Unreadable"  #Corrupted file detected 
   
    except Exception as E:  
        return "File Not found or Unidentified Format"  #Missing or Wrong Format error

    im_data = np.asarray(prep)  # converting PIL image to Numpy array
    gy_img = cv2.cvtColor(im_data, cv2.COLOR_RGB2GRAY) # COnverting to Grey
    cv2.imshow('grey',gy_img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    #Load weights & Set up detecor
    try:
        wt_pth = Path.cwd()/Path('haar_frntface_def.xml')#Weight file.
        detect_face = cv2.CascadeClassifier(str(wt_pth))
        
    except Exception as E:
        return "\nWeight file Not Found \nMove Haar Cascade weight file into\n"+str(Path.cwd())

    # detect & output = face co-ordinates 
    #Set scale factor between 1 and 2 to fine tune detect 
    #set 5 as no. of bounding box to consixdered.
    #input in grey image from passed parameter
    results = detect_face.detectMultiScale(gy_img, 1.5,5) 

    # loop through tuples in results to mark all face & draw box.
    for (x,y,w,h) in results:
        face = face+1 #counting faces
        filename = str(Path(op_dir)/Path('face_'+str(face)+'.jpg')) # setting file name.
        prep.crop((x,y,x+w,y+h)).save(filename,format="jpeg") # cropping headshot and saving.
        
    prep.close() #close image
    return "Faces Found = " + str(face) # final output string with face count
    
  
#argparse 
parser = argparse.ArgumentParser(
                    prog = 'Face_Detector',
                    description = 'Detects Face/headshot in Input image and save to face to O/P directory ',
                    epilog = 'Have fun')
parser.add_argument('-i', '--inp_img',  type=str,
                    help = 'Input entire path in double quotes', required = True)      #input image
parser.add_argument('-o', '--output_dir',  type=Path,required = True , help = 'Enter Output folder path in quotes')   #output dir

parser.add_argument(dest='result',action ='store_const',const = tych)   #output dir
args = parser.parse_args()

print(args.result(args.inp_img,args.output_dir))
