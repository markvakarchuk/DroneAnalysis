from arcgis.raster.orthomapping import compute_sensor_model
import os
import glob
import ntpath
import arcgis
from arcgis.gis import GIS
from arcgis.raster.analytics import *
from arcgis.raster.analytics import create_image_collection
import arcpy

arcpy.AddMessage("Starting adjust.py...")

ici_id = arcpy.GetParameter(1)
image_collection_item = arcgis.gis.Item(gis,itemid=ici_id)

arcpy.AddMessage("item id {}".formate(ici_id))
arcpy.AddMessage("item url {}".formate(image_collection_item.url))
#compute_sensor_model(image_collection=image_collection, mode='Quick', location_accuracy='Low')

#modelbuilder_ortho = image_collection_item.layers[0].export_image(size=[1200,450], f='image', save_folder='.', save_file='modelbuilder_ortho.jpg')
