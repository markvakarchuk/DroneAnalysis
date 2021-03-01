import os
import glob
import ntpath
#import exifread #used later on for GPS data
import arcgis
from arcgis.gis import GIS
from arcgis.raster.analytics import *
from arcgis.raster.analytics import create_image_collection
import arcpy

arcpy.AddMessage("Starting upload.py...")
arcpy.AddMessage("Attempting to login...")
#import parameters
portal_url = arcpy.GetParameterAsText(0)
portal_username = arcpy.GetParameterAsText(1)
portal_password = arcpy.GetParameterAsText(2)
prj_name = arcpy.GetParameterAsText(3)
local_image_folder_path = arcpy.GetParameterAsText(4)
file_type = arcpy.GetParameterAsText(5)

#How to print in Model Builder
gis = GIS(url=portal_url, username=portal_username, password=portal_password)
me = gis.users.me



#image_item_list contains all the items in the folder in the portal
#only use if testing, not needed for initial upload
#image_item_list = me.items(folder=prj_name, max_items=9999)


prj_folder_item = gis.content.create_folder(folder=prj_name, owner=portal_username)

#Add images into folder on portal

#image_list contains all of the images on the local hard drive
image_list = glob.glob(os.path.join(local_image_folder_path, '*' + file_type))

image_item_list = []
item_prop_template = {"type": "Image"}

#increment_step_size = 90 / len(image_list)
#arcpy.SetProgressor("step","Uploading {} images".format(len(image_list)),0,100,increment_step_size)
arcpy.SetProgressor("default","Uploading {} images".format(len(image_list)))
i = 1
for image_full_path in image_list:
    arcpy.AddMessage("Uploading image {}".format(i))
    image_name = ntpath.split(image_full_path)[1]
    item_prop_template["title"] = image_name
    item_prop_template["tags"] = image_name
    item_prop_template["description"] = image_name

    image_item = gis.content.add(item_properties=item_prop_template, data=image_full_path, 
                                owner=portal_username, folder=prj_name)
    image_item_list.append(image_item)
    i += 1
    #arcpy.SetProgressorPosition()

#download exifread
#os.system('pip install exifread')
arcpy.AddMessage("Checking EXIF data...")
#Construct the GPS array structure - [[imageName1, gpsLatitude1, gpsLongtitude1, gpsAltitude1]...]
gps = [[ntpath.split(image)[1], 
        arcpy.GetImageEXIFProperties(image)[1], 
        arcpy.GetImageEXIFProperties(image)[0],
        arcpy.GetImageEXIFProperties(image)[2]] for image in image_list]

#dictionary and attributes 
attrs = arcpy.GetImageEXIFProperties(image_list[0])[3]

maker = attrs.get("EXIF_Make")
model = attrs.get("EXIF_Model")

camera_properties = {"maker":maker,"model":model,"focallength":8.0,"columns":2064,"rows":1544,"pixelsize":0.0024}

#may need to change pixel size

raster_type_params = {
    "gps": gps, "cameraProperties": camera_properties, "isAltitudeFlightHeight": "False",
    "averagezdem":{
        "url":"https://elevation3d.arcgis.com/arcgis/rest/services/WorldElevation3D/Terrain3D/ImageServer"
    }
}

arcpy.AddMessage("Creating Collection...")
image_collection_name = prj_name + "_col"
image_collection_item = create_image_collection(image_collection=image_collection_name,
                                                input_rasters=image_item_list,
                                                raster_type_name="UAV/UAS",
                                                raster_type_params=raster_type_params,
                                                folder=prj_name)


ici_id = image_collection_item.id
arcpy.SetParameter(6, ici_id)


arcpy.AddMessage("Completed upload.py!")
