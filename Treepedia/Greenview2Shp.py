# This script is used to convert the green view index results saved in txt to Shapefile
# considering the facts many people are more comfortable with shapefile and GIS
# Copyright(C) Xiaojiang Li, Ian Seiferling, Marwa Abdulhai, Senseable City Lab, MIT 


def Read_GSVinfo_Text(GVI_Res_txt):
    '''
    This function is used to read the information in text files or folders
    the fundtion will remove the duplicate sites and only select those sites
    have GSV info in green month.
    
    Return:
        panoIDLst,panoDateLst,panoLonLst,panoLatLst,greenViewLst
    
    Pamameters:
        GVI_Res_txt: the file name of the GSV information txt file
    '''   

    import os,os.path

    # empty list to save the GVI result and GSV metadata
    panoIDLst = []
    panoDateLst = []
    panoLonLst = []
    panoLatLst = []
    greenViewLst = []
    
    # read the green view index result txt files
    lines = open(GVI_Res_txt,"r")
    for line in lines:
        # check the completeness of each line, each line include attribute of, panoDate, lon, lat,greenView
        if "panoDate" not in line or "greenview" not in line:
            continue
        
        panoID = line.split(" panoDate")[0][-22:]
        panoDate = line.split(" longitude")[0][-7:]
        coordinate = line.split("longitude: ")[1]
        lon = coordinate.split(" latitude: ")[0]
        latView = coordinate.split(" latitude: ")[1]
        lat = latView.split(', greenview:')[0]
        greenView = line.split("greenview:")[1]
        
        # check if the greeView data is valid
        if len(greenView)<2:
            continue
        
        elif float(greenView) < 0:
            print greenView
            continue
        
        # remove the duplicated panorama id
        if panoID not in panoIDLst:
            panoIDLst.append(panoID)
            panoDateLst.append(panoDate)
            panoLonLst.append(lon)
            panoLatLst.append(lat)
            greenViewLst.append(greenView)

    return panoIDLst,panoDateLst,panoLonLst,panoLatLst,greenViewLst



# read the green view index files into list, the input can be file or folder
def Read_GVI_res(GVI_Res):
    '''
        This function is used to read the information in text files or folders
        the fundtion will remove the duplicate sites and only select those sites
        have GSV info in green month.
        
        Return:
            panoIDLst,panoDateLst,panoLonLst,panoLatLst,greenViewLst
        
        Pamameters:
            GVI_Res: the file name of the GSV information text, could be folder or txt file
        
        last modified by Xiaojiang Li, March 27, 2018
        '''
    
    import os,os.path
    
    # empty list to save the GVI result and GSV metadata
    panoIDLst = []
    panoDateLst = []
    panoLonLst = []
    panoLatLst = []
    greenViewLst = []
    
    
    # if the input gvi result is a folder
    if os.path.isdir(GVI_Res):
        allTxtFiles = os.listdir(GVI_Res)
        
        for txtfile in allTxtFiles:
            # only read the text file
            if not txtfile.endswith('.txt'):
                continue
            
            txtfilename = os.path.join(GVI_Res,txtfile)
            
            # call the function to read txt file to a list
            [panoIDLst_tem,panoDateLst_tem,panoLonLst_tem,panoLatLst_tem,greenViewLst_tem] = Read_GSVinfo_Text(txtfilename)
            
            panoIDLst = panoIDLst + panoIDLst_tem
            panoDateLst = panoDateLst + panoDateLst_tem
            panoLonLst = panoLonLst + panoLonLst_tem
            panoLatLst = panoLatLst + panoLatLst_tem
            greenViewLst = greenViewLst + greenViewLst_tem

    else: #for single txt file
        [panoIDLst_tem,panoDateLst_tem,panoLonLst_tem,panoLatLst_tem,greenViewLst_tem] = Read_GSVinfo_Text(txtfilename)


    return panoIDLst,panoDateLst,panoLonLst,panoLatLst,greenViewLst




def CreatePointFeature_ogr(outputShapefile,LonLst,LatLst,panoIDlist,panoDateList,greenViewList,lyrname):

    """
    Create a shapefile based on the template of inputShapefile
    This function will delete existing outpuShapefile and create a new shapefile containing points with
    panoID, panoDate, and green view as respective fields.
    
    Parameters:
    outputShapefile: the file path of the output shapefile name, example 'd:\greenview.shp'
      LonLst: the longitude list
      LatLst: the latitude list
      panoIDlist: the panorama id list
      panoDateList: the panodate list
      greenViewList: the green view index result list, all these lists can be generated from the function of 'Read_GVI_res'
    
    Copyright(c) Xiaojiang Li, Senseable city lab
    
    last modified by Xiaojiang li, MIT Senseable City Lab on March 27, 2018
    
    """

    import ogr
    import osr

    # create shapefile and add the above chosen random points to the shapfile
    driver = ogr.GetDriverByName("ESRI Shapefile")

    # create new shapefile
    if os.path.exists(outputShapefile):
        driver.DeleteDataSource(outputShapefile)

    data_source = driver.CreateDataSource(outputShapefile)
    targetSpatialRef = osr.SpatialReference()
    targetSpatialRef.ImportFromEPSG(4326)

    outLayer = data_source.CreateLayer(lyrname, targetSpatialRef, ogr.wkbPoint)
    numPnt = len(LonLst)

    print 'the number of points is:',numPnt

    if numPnt > 0:
        # create a field
        idField = ogr.FieldDefn('PntNum', ogr.OFTInteger)
        panoID_Field = ogr.FieldDefn('panoID', ogr.OFTString)
        panoDate_Field = ogr.FieldDefn('panoDate', ogr.OFTString)
        greenView_Field = ogr.FieldDefn('greenView',ogr.OFTReal)
        outLayer.CreateField(idField)
        outLayer.CreateField(panoID_Field)
        outLayer.CreateField(panoDate_Field)
        outLayer.CreateField(greenView_Field)
        
        for idx in range(numPnt):
            #create point geometry
            point = ogr.Geometry(ogr.wkbPoint)

            # in case of the returned panoLon and PanoLat are invalid
            if len(LonLst[idx]) < 3:
                continue      
        
            point.AddPoint(float(LonLst[idx]),float(LatLst[idx]))
            
            # Create the feature and set values
            featureDefn = outLayer.GetLayerDefn()
            outFeature = ogr.Feature(featureDefn)
            outFeature.SetGeometry(point)
            outFeature.SetField('PntNum', idx)
            outFeature.SetField('panoID', panoIDlist[idx])
            outFeature.SetField('panoDate',panoDateList[idx])

            if len(greenViewList) == 0:
                outFeature.SetField('greenView',-999)
            else:
                outFeature.SetField('greenView',float(greenViewList[idx]))

            outLayer.CreateFeature(outFeature)
            outFeature.Destroy()

        data_source.Destroy()

    else:
        print 'You created a empty shapefile'




## ----------------- Main function ------------------------
if __name__ == "__main__":
    import os
    import sys
    
    inputGVIres = r'MYPATHH/spatial-data/greenViewRes'
    outputShapefile = 'MYPATHH/spatial-data/GreenViewRes.shp'
    lyrname = 'greenView'
    [panoIDlist,panoDateList,LonLst,LatLst,greenViewList] = Read_GVI_res(inputGVIres)
    print ('The length of the panoIDList is:', len(panoIDlist))
    
    CreatePointFeature_ogr(outputShapefile,LonLst,LatLst,panoIDlist,panoDateList,greenViewList,lyrname)

    print('Done!!!')
