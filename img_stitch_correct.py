import os, glob, ntpath, arcgis, arcpy, sys, timeit, datetime
from arcgis.gis import GIS
from arcgis.raster.analytics import create_image_collection


arcpy.SetProgressorLabel("Attempting to login...")
#import parameters
portal_url = arcpy.GetParameterAsText(0)
portal_username = arcpy.GetParameterAsText(1)
portal_password = arcpy.GetParameterAsText(2)
prj_name = arcpy.GetParameterAsText(3)
local_image_folder_path = arcpy.GetParameterAsText(4)

#Login
starttime = time.time()
try:
    gis = GIS(url=portal_url, username=portal_username, password=portal_password)
    me = gis.users.me
except Exception:
    e = sys.exc_info()[1]
    print(e.args[0])
    arcpy.AddError(e.args[0])
    sys.exit(arcpy.AddError("Program came to an abrupt end, please correct error message stated above and try again. "))
endtime = time.time()
arcpy.AddMessage("Logging in took: {} seconds".format(round(endtime - starttime,2)))





#Read Exif if no issues upload images
starttime = time.time()
image_list = glob.glob(os.path.join(local_image_folder_path, '*'))
EXIF_attrs = arcpy.GetImageEXIFProperties(image_list[0])[3]
EXIF_Make = EXIF_attrs.get("EXIF_Make")
EXIF_Model = EXIF_attrs.get("EXIF_Model")
EXIF_Width = EXIF_attrs.get("width")
EXIF_Height = EXIF_attrs.get("height")
EXIF_BAND_COUNT = EXIF_attrs.get("EXIF_BAND_COUNT")
EXIF_DateTimeOriginal = EXIF_attrs.get("EXIF_DateTimeOriginal")
EXIF_FocalLength = EXIF_attrs.get("EXIF_FocalLength")

EXIF_DateTime = datetime.datetime.strptime(EXIF_DateTimeOriginal, '%Y:%m:%d %H:%M:%S')
image_collection_name = "imagery_" + prj_name + EXIF_DateTime



arcpy.SetProgressorLabel("Initializing folder...")
if prj_name not in me.folders:
    prj_folder_item = gis.content.create_folder(folder=prj_name, owner=portal_username)




image_item_list = []
item_prop_template = {"type": "Image"}

total_num_steps = len(image_list) * 3
arcpy.SetProgressorLabel("Uploading {} images".format(len(image_list)))
arcpy.SetProgressor("step","Uploading images",0,total_num_steps,1)
i = 1
for image_full_path in image_list:
    arcpy.SetProgressorLabel("Uploading image {}".format(i))
    image_name = ntpath.split(image_full_path)[1]
    item_prop_template["title"] = image_name
    item_prop_template["tags"] = image_name
    item_prop_template["description"] = image_name

    image_item = gis.content.add(item_properties=item_prop_template, data=image_full_path, 
                                owner=portal_username, folder=prj_name)
    image_item_list.append(image_item)
    i += 1
    arcpy.SetProgressorPosition()
endtime = time.time()
arcpy.AddMessage("Uploading images took: {} seconds".format(round(endtime - starttime,2)))


#download exifread
#os.system('pip install exifread')
starttime = time.time()
arcpy.SetProgressorLabel("Checking EXIF data...")
#Construct the GPS array structure - [[imageName1, gpsLatitude1, gpsLongtitude1, gpsAltitude1]...]
gps = [[ntpath.split(image)[1], 
        arcpy.GetImageEXIFProperties(image)[1], 
        arcpy.GetImageEXIFProperties(image)[0],
        arcpy.GetImageEXIFProperties(image)[2]] for image in image_list]

#dictionary and attributes 


camera_properties = {"maker":EXIF_Make,"model":EXIF_Model,"focallength":EXIF_FocalLength,"columns":EXIF_Width,"rows":EXIF_Height,"pixelsize":0.0024}

#may need to change pixel size

raster_type_params = {
    "gps": gps, "cameraProperties": camera_properties, "isAltitudeFlightHeight": "False",
    "averagezdem":{
        "url":"https://elevation3d.arcgis.com/arcgis/rest/services/WorldElevation3D/Terrain3D/ImageServer"
    }
}


arcpy.SetProgressorLabel("Creating Collection...")
image_collection_name = prj_name + "_col"
image_collection_item = create_image_collection(image_collection=image_collection_name,
                                                input_rasters=image_item_list,
                                                raster_type_name="UAV/UAS",
                                                raster_type_params=raster_type_params,
                                                folder=prj_name)
endtime = time.time()
arcpy.AddMessage("Reading EXIF and creating collection took: {} seconds".format(round(endtime - starttime,2)))
arcpy.SetProgressorPosition(round(total_num_steps * .75))


arcpy.AddMessage("Completed uploading and creating collection!")


#****************************************************************************************************************************************
#***********************************************            Part 2           ************************************************************
#***********************************************       Orthorectification    ************************************************************
#****************************************************************************************************************************************



arcpy.SetProgressorLabel("Starting adjustment and orthorectification...")
from arcgis.raster.orthomapping import compute_sensor_model
starttime = time.time()
compute_sensor_model(image_collection=image_collection_item, mode='Full', location_accuracy='High')
endtime = time.time()
arcpy.AddMessage("Computing Sensor Model took: {} seconds".format(round(endtime - starttime,2)))
arcpy.SetProgressorPosition(total_num_steps * 2)
modelbuilder_ortho = image_collection_item.layers[0].export_image(size=[1200,450], f='image', save_folder='.', save_file='modelbuilder_ortho.jpg')
arcpy.SetProgressorPosition(total_num_steps * 3)