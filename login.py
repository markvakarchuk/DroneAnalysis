from arcgis.gis import GIS
portal_url = "https://arcstu.cise.jmu.edu/portal/"
portal_username = "vakarcmi"
portal_password = "&$89t0RQxNlp"


gis = GIS(url=portal_url, username=portal_username, password=portal_password)
me = gis.users.me

print(me.folders)

mefolders = me.folders

foldertitles = []
for f in mefolders:
    foldertitles.append(f.get("title"))

# try:
#     gis = GIS(url=portal_url, username=portal_username, password=portal_password)
#     me = gis.users.me
# except Exception:
#     e = sys.exc_info()[1]
#     print(e.args[0])
#     arcpy.AddError(e.args[0])
#     sys.exit(arcpy.AddError("Program came to an abrupt end, please correct error message stated above and try again. "))
