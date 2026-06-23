import arcpy,os
arcpy.env.overwriteOutput = True

# Project object
aprx = arcpy.mp.ArcGISProject(
    r"C:\project\folder\SPCSZonesProject.aprx"
)

# Map objects
map1 = aprx.listMaps("CAPlane1")[0]
map2 = aprx.listMaps("CAPlane2")[0]
map3 = aprx.listMaps("CAPlane3")[0]
map4 = aprx.listMaps("CAPlane4")[0]
map5 = aprx.listMaps("CAPlane5")[0]
map6 = aprx.listMaps("CAPlane6")[0]

placesLayer = map1.listLayers("California Places")[0]
zonesLayer = map1.listLayers("CA Zones")[0]

# Layout object
lyt = aprx.listLayouts()[0]

# Map Frame objects
mapFrame1 = lyt.listElements("MAPFRAME_ELEMENT","Map Frame 1")[0]
mapFrame2 = lyt.listElements("MAPFRAME_ELEMENT","Map Frame 2")[0]
mapFrame3 = lyt.listElements("MAPFRAME_ELEMENT","Map Frame 3")[0]
mapFrame4 = lyt.listElements("MAPFRAME_ELEMENT","Map Frame 4")[0]
mapFrame5 = lyt.listElements("MAPFRAME_ELEMENT","Map Frame 5")[0]
mapFrame6 = lyt.listElements("MAPFRAME_ELEMENT","Map Frame 6")[0]

# Spatial Reference Text objects
srText1 = lyt.listElements("TEXT_ELEMENT","Spatial Reference Text 1")[0]
srText2 = lyt.listElements("TEXT_ELEMENT","Spatial Reference Text 2")[0]
srText3 = lyt.listElements("TEXT_ELEMENT","Spatial Reference Text 3")[0]
srText4 = lyt.listElements("TEXT_ELEMENT","Spatial Reference Text 4")[0]
srText5 = lyt.listElements("TEXT_ELEMENT","Spatial Reference Text 5")[0]
srText6 = lyt.listElements("TEXT_ELEMENT","Spatial Reference Text 6")[0]

# Create PDF Document object
finalPDF = r"C:\project\PDFs\SPCSZones.pdf"
if arcpy.Exists(finalPDF):
    arcpy.Delete_management(finalPDF)
pdfDoc = arcpy.mp.PDFDocumentCreate(finalPDF)

# Create list of place names sorted alphabetically
placesSortedByNameList = sorted(
    [row[0] for row in arcpy.da.SearchCursor(placesLayer,["NAME"])]
)

# Create dictionary of X,Y coordinates for each place
placesCoordsDict = {row[0]:row[1] for row in arcpy.da.SearchCursor(
    placesLayer,["NAME","SHAPE@XY"])}

zone_map = {
    "CA_1":("I", "NAD_1983_2011_StatePlane_California_I_FIPS_0401"),
    "CA_2":("II", "NAD_1983_2011_StatePlane_California_II_FIPS_0402"),
    "CA_3":("III", "NAD_1983_2011_StatePlane_California_III_FIPS_0403"),
    "CA_4":("IV", "NAD_1983_2011_StatePlane_California_IV_FIPS_0404"),
    "CA_5":("V", "NAD_1983_2011_StatePlane_California_V_FIPS_0405"),
    "CA_6":("VI", "NAD_1983_2011_StatePlane_California_VI_FIPS_0406"),
}
zones = []
with arcpy.da.SearchCursor(zonesLayer,["SHAPE@","ZONE"]) as cursor:
    for poly_geom, zoneVal in cursor:
        if zoneVal in zone_map:
            spcsZone, srString = zone_map[zoneVal]
            zones.append((poly_geom, spcsZone, srString))

# Create Spatial Reference object for places layer which will be
# the Geographic Coordinate System of the source feature class
srPlacesLayer = arcpy.Describe(placesLayer).spatialReference

# Geodatabase paths
geogFC = r"{0}\geogFC".format(aprx.defaultGeodatabase)
projFC = r"{0}\projFC".format(aprx.defaultGeodatabase)

# Write one PDF page for each place in the sorted list
pageCount = 0
for Count, placeName in enumerate(placesSortedByNameList):
    pageCount +=1
    xCoord,yCoord = placesCoordsDict[placeName]
    point_geom = arcpy.PointGeometry(arcpy.Point(float(xCoord),float(yCoord)))

    # find matching zone
    spcsZone, srString = None,None
    for poly_geom, zoneVal, stVal in zones:
        if poly_geom.contains(point_geom):
            spcsZone, srString = zoneVal, stVal
            break
        else:
            continue

    # warn and skip if no zone matched
    if spcsZone is None:
        print(f"{Count + 1}: WARNING:{placeName} not within CA Zones layer")
        pageCount -= 1
        continue

    srSPCS = arcpy.SpatialReference(srString)
    print("{2}: {0} is in CA StatePlane Zone {1}".format(placeName, spcsZone, Count + 1))

    arcpy.management.CreateFishnet(geogFC,
                                   "{0} {1}".format(xCoord - 0.25, yCoord - 0.25),
                                   "{0} {1}".format(xCoord - 0.25, yCoord + 0.25),
                                   0.5, 0.5, 1,1,
                                   geometry_type="POLYGON", labels="NO_LABELS"
                                   )
    arcpy.management.DefineProjection(geogFC,srPlacesLayer)
    arcpy.management.Project(geogFC,projFC,srSPCS)
    projFCExtent = arcpy.Describe(projFC).extent

    zonesNumerals = ["I","II","III","IV","V","VI"]
    mapFrames = [mapFrame1,mapFrame2,mapFrame3,mapFrame4,mapFrame5,mapFrame6]
    srTexts = [srText1,srText2,srText3,srText4,srText5,srText6]
    if spcsZone in zonesNumerals:
        activeIdx = zonesNumerals.index(spcsZone)

        for i,(mf,sr) in enumerate(zip(mapFrames,srTexts)):
            isActive = (i==activeIdx)
            mf.visible = isActive
            sr.visible = isActive
        mapFrames[activeIdx].camera.setExtent(projFCExtent)
        mapFrames[activeIdx].camera.scale = mapFrames[activeIdx].camera.scale * 1.05

        # Title text object
        titleText = lyt.listElements("TEXT_ELEMENT", "Title")[0]
        titleText.text = placeName

        # Export PDF for this country's page
        lyt.exportToPDF(r"C:\project\PDFs\sheet{0}.pdf".format(Count))
        pdfDoc.appendPages(r"C:\project\PDFs\sheet{0}.pdf".format(Count))

print(f"{pageCount} pages exported")
pdfDoc.saveAndClose()
del pdfDoc
os.startfile(finalPDF)

del aprx
