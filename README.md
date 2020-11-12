## Background

Landsat Level 2 scenes come with a quality assessment band (...pixel_qa.tif) that shows various forms of atmospheric and other interference present in the image.

The accompanying pixel_qa file is a GeoTIFF with bit-packed values corresponding to an internal USGS numbering scheme. You can learn about these values and the pixel_qa band in general by reading the USGS overview located [here](https://prd-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/atoms/files/LSDS-1368_L8_C1-LandSurfaceReflectanceCode-LASRC_ProductGuide-v3.pdf). There is also a more in-depth PDF titled 'Landsat Quality Assessment (QA) Tools User's Guide'.

## Usage

This CLI tool may be useful to you if you are working with Landsat quality assessment data in Python 3.

This tool is written to search the directory where it is run, and all sub-directories for Landsat pixel_qa bands. It then 'unpacks' the bit packed pixel_qa raster and creates a new GeoTIFF for each USGS quality measure that the user specifies. Finally, the tool takes the new quality bands for each scene and creates a composite image stack for each quality control measure.

For example, you can take a directory of Landsat scenes, pull out all cloudy pixels, and create a composite image showing all cloudy pixels in the stack.

This is helpful for time series analysis because you can identify atmospheric interference over time.

Flags correspond to each quality assessment layer identified by USGS.
The following will produce individual pixel_qa band files for every quality assessment type identified by USGS and then build composites from each quality assessment type.

```commandline
cd /filepath/to/top_dir_for_landsat_scenes
landsat_L1_qa_tool -c -f -t -cl -cc -cs -ci -s -w
```

Quality assessment types:
```commandline
-c --clear-terrain
-f --fill
-t --terrain-occlusion
-cl --clouds
-cc --cloud-confidence
-cs --cloud-shadow
-ci --cirrus
-s --snow-ice
-w --water
```

## Why this tool?

The USGS took down their repos from Github for some reason:https://www.usgs.gov/core-science-systems/nli/landsat/espa-and-product-related-code-repository-location-changes

Among the repos taken down and not re-released are tools for processing Level 2 QA files.

If you use ArcMap (maybe this works with ArcPro too?) you can use https://code.usgs.gov/espa/landsat-qa-arcgis-toolbox for individual files.

Rasterio's Landsat QA tools is [here](https://github.com/mapbox/rio-l8qa). I didn't adapt this repo because it is older.

## Thanks!
To and-viceversa https://github.com/and-viceversa/landsat_L1_qa_tool for the original code which processes level 1 band qa information.