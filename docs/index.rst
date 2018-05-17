**Treepedia** 

**What is Treepedia?**

Treepedia is a project by the MIT Senseable City Lab to measure the green canopy of cities. Researchers at MIT and the World Economic Forum (WEF) are using Google Street View panoramas to calculate a Green View Index. The goal is to focus attention on the value of plants in urban areas and encourage residents and governments to protect and increase each city’s tree cover. On each map, you can click down to get a street view of a particular location and its canopy percentage.

If you would like to contribute to this now open-sourced project and calculate the green view index for your city, follow the instructions below.

**Installation**

Before running any analysis, there are python packages that you will need to install to run all code. This guide provides the right set-up environment for a Windows System, but similar procedures follow for Mac/Linux.

The following packages are needed to run this project:
- Anaconda (with python and the following packages:openCV, PIL, xmltodict, numpy, matplotlib, fiona, shapely)
- gdal
- pyshiftmean package 

Skip the tutorial below if you already have these packages. 

**Install Python**

Feel free to download the latest 2.7x version of Python (rather than the 3.x Python version) here: https://www.python.org/ftp/python/2.7.8/python-2.7.8.msi

Install Python with default options and directories. After installation, go to Python  IDLE (Python GUI) to find out what version of python you are using. Make note of the number that shows the version of your Python in the top right: 

Python 2.7.12 [MSC v.1500 32 bit (Intel)] on win32

MSC v.1500  may differ if you are using a different Python installation, if it does then please make a note of that number. Note, if you installed the 64-bit version of Python, for the rest of the tutorial please remove the (x86) from the paths.

Note: You will be using the pip command to install additional packages. In order to use this command, set a path in your environment system variables as Python/Scripts. 

**Install GDAL**

Head over to Tamas Szekeres’ Windows binaries and download the appropriate GDAL Binary.

For this tutorial, we are using the MSC v.1500 on a 32-bit system, the picture below illustrates how to match the version with your own python version. Look for either 64-bit or 32-bit systems and the release-1500 number which should match the number from IDLE in step 4 above, and click the appropriate link. This should take you to the link of binaries (installers) to download. 

Locate the core installer, which has most of the components of GDAL. After downloading your version, install GDAL with standard settings. Next, return to the list of GDAL binaries and install the python bindings for your version of Python, this can either be 2.7, 3.1, or 3.2. Recall that we had installed Python 2.7 earlier, so we have to locate this version, as seen below:

Add the appropriate System path variables to tell the Windows system where GDAL installations are located. Add: <;C:\Program Files (x86)\GDAL> to your System Path variable list. In addition, add two new system variables with the following specifications: 

Variable name: GDAL_DATA
Variable value: C:\Program Files (x86)\GDAL\gdal-data

Variable name: GDAL_DRIVER_PATH
Variable value: C:\Program Files (x86)\GDAL\gdalplugins

If you open Python in your terminal window and type <import ogr, osr>, you should not get any errors. 

**PyMeanShift Package** 

In order to get the pymeanshift package, follow the instructions in the following link: 
https://github.com/fjean/pymeanshift/wiki/Install 

If the link to install Visual C++ 2008 Express Edition with SPI provided on the site does not work for you, head to the following site to download: http://download.microsoft.com/download/8/1/d/81d3f35e-fa03-485b-953b-ff952e402520/VS2008ProEdition90dayTrialENUX1435622.iso 

**Additional Packages**

Finally, we require a couple more packages to run the scripts provided to generate the metadata and calculate the Green View Index of streets provided. These will be installed through the requirements file. 
-	OpenCV: http://opencvpython.blogspot.com/2012/05/install-opencv-in-windows-for-python.html 
-	PIL (in terminal window): pip install pillow
-	xmltodict (in terminal window) pip install xmltodict
-       numpy: pip install numpy
-	matplotlib: pip install matplotlib

## Generate Points Along Street Network of Target City

For any city or area that you wish to run the provided scripts on, you will require an shp file that is a polygon of the city or area's boundary (ideally an official government boundary file). You will also require a shp file containing the road network for your area or city. The roads can be retrieved via multiple sources but we suggest the standard of using open street map data. OSM data can be accessed through multiple sources and methods but one of the simplest modes is by using the Mapzen service. There you can download the OpenStreetMap Dataset split by geometry type: lines, points, or polygons from the following site: https://mapzen.com/data/metro-extracts/. The road network is provided in the lines shp file for your specified city.

Run the file [“createPoints.py”](https://github.com/abdulhaim/Treepedia/blob/master/Treepedia/createPoints.py), with the appropriate arguments in your command for id_field, cityname, city_utm_zone_epsg, inshp,outpath, and outpnts as specified in the file. Note that id_field will always be "ID" unless you are not using street data from OSM, in which case you will need to input the appropriate argument to tel it what is the name of the attribute filed to use as the ID (case sensitive). If you are generating points along the street network of a big city, you may chose to change the variable "dist" to a value other than 20 meters. After running the file, you should have a new shp file containing points every 20 meters or any value you have set previously, with each point containing latitude and longitude attributes. 

_HIGHLY IMPORTANT NOTE:_ This point sampling module uses the WGS84 Projection (EPSG:4326) so make sure you are set to the correct projection for your city by changing line 74 in the above python file. 

**Alternative to Generate SHP File: ArcMap**

You may also generate the SHP file for your city using the ArcMap. 

1. Import your lines.shp and polygon.shp file into your layers column in that order and calculate the intersection of these layers. 
2. Click on Editor and begin start editing. Left click the new layer created by the new roads to go into "Open Attribute Table" and "Select by Attributes" to pass in the following queries to remove highways. 

Removed roads
"fclass" = 'trunk_link' OR "fclass" = 'trunk_link' OR "fclass" = 'steps' OR "fclass" = 'track' OR "fclass" = 'track_grade1' OR "fclass" = 'motorway' OR "fclass" = 'motorway_link' OR "fclass" = 'service'

"highway" = 'trunk_link' OR "highway" = 'tertiary' OR "highway" = 'motorway' OR "highway" = 'motorway_link' OR "highway" = 'steps' OR "highway" = ' ' OR "highway" = 'pedestrian' OR "highway" = 'primary' OR "highway" = 'primary_link' OR "highway" = 'footway' OR "highway" = 'tertiary_link' OR "highway" = 'trunk' OR "highway" = 'secondary' OR "highway" = 'secondary_link' OR "highway" = 'tertiary_link'  OR "highway" = 'bridleway' OR "highway" = 'service'

We have provided a sample street network, boundary, and final point sampling shapefile in the test folder [here.](https://github.com/abdulhaim/Treepedia/tree/master/test)

3. Take look at http://spatialreference.org/ref/ for the Spatial Reference number of your region (with EPSG format). Change the number in the first line of the code below and run the following script in the Python Console to generate points every 20 meters. If the number for your city is not available on the site above, a google of "City Name EPSG" should give you your number. 

`sr = arcpy.SpatialReference(2805) #for your City`
`points = []`
`for row in arcpy.da.SearchCursor(r'LOCATION OF INTERSECT SHP', ["SHAPE@"],spatial_reference=sr):`
     `if row[0] is None:`
         `continue`
     `length = int(row[0].length)`
     `for i in xrange(65,length,65):` #the number 65 represents 20 meters in feet. 
         `point = row[0].positionAlongLine(i)`
         `points.append(point)`
`arcpy.CopyFeatures_management(points,'LOCATION OF NEW SHP FILE WITH NAME')` #saving shapefile 

QGIS also contains the tools to generate your road network shp file from OSM data and other usefule open source tools may include osmosis, the R package 'osmar' or the Python package 'osmnx'.

**Create Metadata for GSV**
Run the file [“metadataCollector.py”](https://github.com/abdulhaim/Treepedia/blob/master/Treepedia/metadataCollector.py) to collect the metadata of Google Street View Panoramas with the appropriate arguments in your command for the inputShp file and the directory where your metadata .txt files will be stored as specified in the .py file. 

The output of this step will be folders containing textfiles with Google Street View (GSV) panorama ID's of the points along the street network. 

**Calculate Green View Index** 
Run the file [“GreenViewCalc.py”](https://github.com/abdulhaim/Treepedia/blob/master/Treepedia/GreenViewCalc.py) to take the metaData and calculate the Green View Index for every panoID, with the appropriate arguments in your command for the path of the folder containing the metadata textfiles generated in the previous step (GSVinfoRoot), the path to the temporary folder where GSV Images will be downloaded and removed accordingly (GSVimgpath), the path to a new empty folder that will contain the textfiles containing the Green View Index for every city (outputTextPath), and the path to a textfile with Google Street View keys (key_file). Note that you should have 10-15 keys in this folder so that the limit of retrieving 25,000 images is not exceeded. 

Each city has its own growing season in which greenery is abundant: You may change this parameter by modifying the "greenSeason" list in the file and specify the green months accordingly. 

Note: If the computation stops due to short connection, make sure to delete the text-files that did not finish processing the metadata. 

The output of this step are folders containing text-files with the Green View index computed for each point (with its respective panorama ID). 

**Send Your Data for Visualization!**
Before sending your data for visualization, run the file ["Greenview2Shp.py"](https://github.com/abdulhaim/Treepedia/blob/master/Treepedia/Greenview2Shp.py). Remember to specify the folder containing the GVI's for each point and the path where you would like to output the final Shapefile containing the GVI points of your city in your command arguments. Finally, send us (The Senseable City Lab) your output for visualization!

If you are a government, researcher or stakeholder that has used this library to compute the GVI for your city and would like us to include a mapping of it on the Treepedia website, please contact us at: senseable-trees@mit.edu
