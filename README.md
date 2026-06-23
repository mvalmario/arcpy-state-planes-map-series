# arcpy-state-planes-map-series
ArcPy workflow that automatically generates a California city map series and assigns State Plane coordinate systems based on geographic location.

# Description

This project was adapted from an ArcPy automation exercise in the Udemy course *ArcPy for Python Developers using ArcGIS Pro*. The original workflow generated map series pages for Australian locations and selected the appropriate UTM zone based on longitude.

For this project, the workflow was modified for California's State Plane Coordinate System (SPCS). Instead of calculating a projection zone from longitude, the script compares location point to California State Planes Polygon to assign an appropriate California State Plane zone, updates map frames and layout elements, and exports a multi-page PDF atlas of California cities.

The project demonstrates ArcPy map automation, spatial reference management, layout manipulation, and batch PDF export in ArcGIS Pro.

## Output/Images files

SPCSZones.pdf shows a sample output of the map series.

SPCSZones_Pro.png shows the layout, and layout elements within the map ArcPro Project.
