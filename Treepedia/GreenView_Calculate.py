# This program is used to calculate the green view index based on the collecte metadata. The
# Object based images classification algorithm is used to classify the greenery from the GSV imgs
# in this code, the meanshift algorithm implemented by pymeanshift was used to segment image
# first, based on the segmented image, we further use the Otsu's method to find threshold from
# ExG image to extract the greenery pixels.

# For more details about the object based image classification algorithm
# check: Li et al., 2016, Who lives in greener neighborhoods? the distribution of street greenery and it association with residents' socioeconomic conditions in Hartford, Connectictu, USA

# This program implementing OTSU algorithm to chose the threshold automatically
# For more details about the OTSU algorithm and python implmentation
# cite: http://docs.opencv.org/trunk/doc/py_tutorials/py_imgproc/py_thresholding/py_thresholding.html


# Copyright(C) Xiaojiang Li, Ian Seiferling, Marwa Abdulhai, Senseable City Lab, MIT 
# First version June 18, 2014
def graythresh(array,level):
    '''array: is the numpy array waiting for processing
    return thresh: is the result got by OTSU algorithm
    if the threshold is less than level, then set the level as the threshold
    by Xiaojiang Li
    '''
    
    import numpy as np
    
    maxVal = np.max(array)
    minVal = np.min(array)
    
#   if the inputImage is a float of double dataset then we transform the data 
#   in to byte and range from [0 255]
    if maxVal <= 1:
        array = array*255
        # print "New max value is %s" %(np.max(array))
    elif maxVal >= 256:
        array = np.int((array - minVal)/(maxVal - minVal))
        # print "New min value is %s" %(np.min(array))
    
    # turn the negative to natural number
    negIdx = np.where(array < 0)
    array[negIdx] = 0
    
    # calculate the hist of 'array'
    dims = np.shape(array)
    hist = np.histogram(array,range(257))
    P_hist = hist[0]*1.0/np.sum(hist[0])
    
    omega = P_hist.cumsum()
    
    temp = np.arange(256)
    mu = P_hist*(temp+1)
    mu = mu.cumsum()
    
    n = len(mu)
    mu_t = mu[n-1]
    
    sigma_b_squared = (mu_t*omega - mu)**2/(omega*(1-omega))
    
    # try to found if all sigma_b squrered are NaN or Infinity
    indInf = np.where(sigma_b_squared == np.inf)
    
    CIN = 0
    if len(indInf[0])>0:
        CIN = len(indInf[0])
    
    maxval = np.max(sigma_b_squared)
    
    IsAllInf = CIN == 256
    if IsAllInf !=1:
        index = np.where(sigma_b_squared==maxval)
        idx = np.mean(index)
        threshold = (idx - 1)/255.0
    else:
        threshold = level
    
    if np.isnan(threshold):
        threshold = level
    
    return threshold



def VegetationClassification(Img):
    '''
    This function is used to classify the green vegetation from GSV image,
    This is based on object based and otsu automatically thresholding method
    The season of GSV images were also considered in this function
        Img: the numpy array image, eg. Img = np.array(Image.open(StringIO(response.content)))
        return the percentage of the green vegetation pixels in the GSV image
    
    By Xiaojiang Li
    '''
    
    import pymeanshift as pms
    import numpy as np
    
    # use the meanshift segmentation algorithm to segment the original GSV image
    (segmented_image, labels_image, number_regions) = pms.segment(Img,spatial_radius=6,
                                                     range_radius=7, min_density=40)
    
    I = segmented_image/255.0
    
    red = I[:,:,0]
    green = I[:,:,1]
    blue = I[:,:,2]
    
    # calculate the difference between green band with other two bands
    green_red_Diff = green - red
    green_blue_Diff = green - blue
    
    ExG = green_red_Diff + green_blue_Diff
    diffImg = green_red_Diff*green_blue_Diff
    
    redThreImgU = red < 0.6
    greenThreImgU = green < 0.9
    blueThreImgU = blue < 0.6
    
    shadowRedU = red < 0.3
    shadowGreenU = green < 0.3
    shadowBlueU = blue < 0.3
    del red, blue, green, I
    
    greenImg1 = redThreImgU * blueThreImgU*greenThreImgU
    greenImgShadow1 = shadowRedU*shadowGreenU*shadowBlueU
    del redThreImgU, greenThreImgU, blueThreImgU
    del shadowRedU, shadowGreenU, shadowBlueU
    
    greenImg3 = diffImg > 0.0
    greenImg4 = green_red_Diff > 0
    threshold = graythresh(ExG, 0.1)
    
    if threshold > 0.1:
        threshold = 0.1
    elif threshold < 0.05:
        threshold = 0.05
    
    greenImg2 = ExG > threshold
    greenImgShadow2 = ExG > 0.05
    greenImg = greenImg1*greenImg2 + greenImgShadow2*greenImgShadow1
    del ExG,green_blue_Diff,green_red_Diff
    del greenImgShadow1,greenImgShadow2
    
    # calculate the percentage of the green vegetation
    greenPxlNum = len(np.where(greenImg != 0)[0])
    greenPercent = greenPxlNum/(400.0*400)*100
    del greenImg1,greenImg2
    del greenImg3,greenImg4
    
    return greenPercent



# using 18 directions is too time consuming, therefore, here I only use 6 horizontal directions
# Each time the function will read a text, with 1000 records, and save the result as a single TXT
def GreenViewComputing_ogr_6Horizon(GSVinfoFolder, outTXTRoot, greenmonth, key_file):
    
    """
    This function is used to download the GSV from the information provide
    by the gsv info txt, and save the result to a shapefile
    
    Required modules: StringIO, numpy, requests, and PIL
    
        GSVinfoTxt: the input folder name of GSV info txt
        outTXTRoot: the output folder to store result green result in txt files
        greenmonth: a list of the green season, for example in Boston, greenmonth = ['05','06','07','08','09']
        key_file: the API keys in txt file, each key is one row, I prepared five keys, you can replace by your owne keys if you have Google Account
        
    last modified by Xiaojiang Li, MIT Senseable City Lab, March 25, 2018
    
    """
    
    import time
    from PIL import Image
    import numpy as np
    import requests
    from StringIO import StringIO
    
    
    # read the Google Street View API key files, you can also replace these keys by your own
    lines = open(key_file,"r")
    keylist = []
    for line in lines:
        key = line[:-1]
        keylist.append(key)
    
    print ('The key list is:=============', keylist)
    
    # set a series of heading angle
    headingArr = 360/6*np.array([0,1,2,3,4,5])
    
    # number of GSV images for Green View calculation, in my original Green View View paper, I used 18 images, in this case, 6 images at different horizontal directions should be good.
    numGSVImg = len(headingArr)*1.0
    pitch = 0
    
    # create a folder for GSV images and grenView Info
    if not os.path.exists(outTXTRoot):
        os.makedirs(outTXTRoot)
    
    # the input GSV info should be in a folder
    if not os.path.isdir(GSVinfoFolder):
        print 'You should input a folder for GSV metadata'
        return
    else:
        allTxtFiles = os.listdir(GSVinfoFolder)
        for txtfile in allTxtFiles:
            if not txtfile.endswith('.txt'):
                continue
            
            txtfilename = os.path.join(GSVinfoFolder,txtfile)
            lines = open(txtfilename,"r")
            
            # create empty lists, to store the information of panos,and remove duplicates
            panoIDLst = []
            panoDateLst = []
            panoLonLst = []
            panoLatLst = []
            
            # loop all lines in the txt files
            for line in lines:
                metadata = line.split(" ")
                panoID = metadata[1]
                panoDate = metadata[3]
                month = panoDate[-2:]
                lon = metadata[5]
                lat = metadata[7][:-1]
                
                # print (lon, lat, month, panoID, panoDate)
                
                # in case, the longitude and latitude are invalide
                if len(lon)<3:
                    continue
                
                # only use the months of green seasons
                if month not in greenmonth:
                    continue
                else:
                    panoIDLst.append(panoID)
                    panoDateLst.append(panoDate)
                    panoLonLst.append(lon)
                    panoLatLst.append(lat)
            
            # the output text file to store the green view and pano info
            gvTxt = 'GV_'+os.path.basename(txtfile)
            GreenViewTxtFile = os.path.join(outTXTRoot,gvTxt)
            
            
            # check whether the file already generated, if yes, skip. Therefore, you can run several process at same time using this code.
            print GreenViewTxtFile
            if os.path.exists(GreenViewTxtFile):
                continue
            
            # write the green view and pano info to txt            
            with open(GreenViewTxtFile,"w") as gvResTxt:
                for i in range(len(panoIDLst)):
                    panoDate = panoDateLst[i]
                    panoID = panoIDLst[i]
                    lat = panoLatLst[i]
                    lon = panoLonLst[i]
                    
                    # get a different key from the key list each time
                    idx = i % len(keylist)
                    key = keylist[idx]
                    
                    # calculate the green view index
                    greenPercent = 0.0

                    for heading in headingArr:
                        print "Heading is: ",heading
                        
                        # using different keys for different process, each key can only request 25,000 imgs every 24 hours
                        URL = "http://maps.googleapis.com/maps/api/streetview?size=400x400&pano=%s&fov=60&heading=%d&pitch=%d&sensor=false&key=AIzaSyAwLr6Oz0omObrCJ4n6lI4VbCCvmaL1Z3Y"%(panoID,heading,pitch)
                        
                        # let the code to pause by 1s, in order to not go over data limitation of Google quota
                        time.sleep(1)
                        
                        # classify the GSV images and calcuate the GVI
                        try:
                            response = requests.get(URL)
                            im = np.array(Image.open(StringIO(response.content)))
                            percent = VegetationClassification(im)
                            greenPercent = greenPercent + percent

                        # if the GSV images are not download successfully or failed to run, then return a null value
                        except:
                            greenPercent = -1000
                            break

                    # calculate the green view index by averaging six percents from six images
                    greenViewVal = greenPercent/numGSVImg
                    print 'The greenview: %s, pano: %s, (%s, %s)'%(greenViewVal, panoID, lat, lon)

                    # write the result and the pano info to the result txt file
                    lineTxt = 'panoID: %s panoDate: %s longitude: %s latitude: %s, greenview: %s\n'%(panoID, panoDate, lon, lat, greenViewVal)
                    gvResTxt.write(lineTxt)


# ------------------------------Main function-------------------------------
if __name__ == "__main__":
    
    import os,os.path
    import itertools
    
    
    GSVinfoRoot = 'MYPATH//spatial-data/metadata'
    outputTextPath = r'MYPATH//spatial-data/greenViewRes'
    greenmonth = ['01','02','03','04','05','06','07','08','09','10','11','12']
    key_file = 'MYPATH/Treepedia/Treepedia/keys.txt'
    
    GreenViewComputing_ogr_6Horizon(GSVinfoRoot,outputTextPath, greenmonth, key_file)


