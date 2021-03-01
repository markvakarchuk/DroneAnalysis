def login(portal_url, portal_username, portal_password):
    from arcgis.gis import GIS

    gis = GIS(url=portal_url, username=portal_username, password=portal_password)
    me = gis.users.me

    print(me.folders)

