import cv2
import numpy as np
from skimage.metrics import structural_similarity
import time 
# read image
tmplt_handle = cv2.imread('templates/template_open2.png', cv2.IMREAD_UNCHANGED)
tmplt_deadbolt = cv2.imread('templates/template_deadbolt.png', cv2.IMREAD_UNCHANGED)
compoh = cv2.imread('templates/oh.png')
compod = cv2.imread('templates/od.png')
compch = cv2.imread('templates/ch.png')
compcd = cv2.imread('templates/cd.png')

def getMatch(img, tmplt):

# read template with alpha
    hh, ww = tmplt.shape[:2]
    tmplt_mask = tmplt[:,:,3]
    tmplt_mask = cv2.merge([tmplt_mask,tmplt_mask,tmplt_mask])
    tmplt2 = tmplt[:,:,0:3]
    corrimg = cv2.matchTemplate(img,tmplt2,cv2.TM_CCORR_NORMED, mask=tmplt_mask)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(corrimg)
    max_val_ncc = '{:.3f}'.format(max_val)
    # print("correlation match score: " + max_val_ncc)
    xx = max_loc[0]
    yy = max_loc[1]
    # print('xmatch =',xx,'ymatch =',yy)

    # draw red bounding box to define match location
    result = img.copy()
    pt1 = (xx,yy)
    pt2 = (xx+ww, yy+hh)
    cv2.rectangle(result, pt1, pt2, (0,0,255), 1)
    newimg = img[pt1[1]:pt2[1], pt1[0]:pt2[0]]
    newimg = newimg[len(newimg)//3:2*len(newimg)//3, len(newimg[0])//3:2*len(newimg[0])//3]
    # cv2.imshow('result', result)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    return newimg

def imgsim(first, second):
    # Convert images to grayscale
    first_gray = cv2.cvtColor(first, cv2.COLOR_BGR2GRAY)
    second_gray = cv2.cvtColor(second, cv2.COLOR_BGR2GRAY)

    # Compute SSIM between two images
    score, diff = structural_similarity(first_gray, second_gray, full=True)
    # print("Similarity Score: {:.3f}%".format(score * 100))
    return score*100


cam = cv2.VideoCapture(0)
b2hstatus = ''
b1hstatus = ''
b1hcounter = 0
b2dstatus = ''
b1dstatus = ''
b1dcounter = 0

uploadqueue = []

LASTUPLOAD = time.time()
while True:
    FPSSTART = time.time()

    ret, img = cam.read()
    #img = cv2.imread('../dchc.png')
    handle, deadbolt = getMatch(img, tmplt_handle), getMatch(img, tmplt_deadbolt)

    ohsim, chsim = imgsim(handle, compoh), imgsim(handle, compch)
    odsim, cdsim = imgsim(deadbolt, compod), imgsim(deadbolt, compcd)
    #print(ohsim, chsim, odsim, cdsim)

    hstatus = 'inconclusive' if ohsim<30 and chsim<30 else 'locked' if chsim>ohsim else 'unlocked'
    dstatus = 'inconclusive' if odsim<30 and cdsim<30 else 'locked' if cdsim>odsim else 'unlocked'
    
    if(b1hstatus!=hstatus): #Fail change.
        b1hstatus = hstatus
        b1hcounter = 0
    elif(b1hstatus==hstatus and b2hstatus!=b1hstatus): #waiting to change
        b1hcounter += 1
        if(b1hcounter > 15): #Success change.
            uploadqueue.append(f'handle {b1hstatus}')
            b1hcounter = 0
            b2hstatus = b1hstatus

    if(b1dstatus!=dstatus): #Fail change.
        b1dstatus = dstatus
        b1dcounter = 0
    elif(b1dstatus==dstatus and b2dstatus!=b1dstatus): #waiting to change
        b1dcounter += 1
        if(b1dcounter > 15): #Success change.
            uploadqueue.append(f'deadbolt {b1dstatus}')
            b1dcounter = 0
            b2dstatus = b1dstatus

    if(uploadqueue and time.time()-LASTUPLOAD>1): #max 60 readings/min = 1 reading/sec
        print(f"upload {uploadqueue.pop(0)}")
        time.sleep(0.25) #MIMIC SENDING DATA
        LASTUPLOAD = time.time()
    FPSEND = time.time()
    #print(1/(FPSEND-FPSSTART))
    #print(b1hcounter, b1dcounter, uploadqueue)

