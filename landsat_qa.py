#!/usr/bin/env python
# Python 3.7

import argparse
import os
import sys

from osgeo import gdal
from osgeo import gdalconst


class QualityBandConverter:

    def __init__(self, args):
        self.args = args
        self.qa_dict = {}
        self.nodatavalue = gdal.GDT_UInt16

        if args.fill: self.fill_dict = {}

        if args.terrain_occlusion: self.terrain_occlusion_dict = {}

        if args.radiometric_saturation: self.rad_sat_dict = {}

        if args.clouds: self.clouds_dict = {}

        if args.cloud_confidence: self.cloud_conf_dict = {}

        if args.cloud_shadow: self.cloud_shadow_dict = {}

        if args.snow_ice: self.snow_ice_dict = {}

        if args.cirrus: self.cirrus_dict = {}

        if args.clear_terrain: self.clear_terrain_dict = {}

        if args.water: self.water_dict = {}

    def find_qa_files(self):
        print('Searching for Landsat qa files...')
        try:
            for root, dirs, files in os.walk('.'):
                for file in files:
                    if "pixel_qa.tif" in file:
                        self.qa_dict[root] = file
                        print(' Found ', os.path.join(root, file))

            if len(self.qa_dict.keys()) is 0: raise Exception

        except Exception as e:
            print('No QA files found.')
            print(e)
            quit()

    def split_qa_bands(self):

        print('Writing individual QA files...')

        # store all quality band integer values TODO fix radsat
        val_dict = {'f': [1],
                    't': [1346, 1348, 1350, 1352],
                    'r': [2724, 2728, 2732, 2804, 2808, 2812, 3748, 3752, 3756, 6820, 6824, 6828],
                    'c': [322, 386, 834, 898, 1346],
                    's': [336, 368, 400, 432, 848, 880, 912, 944, 1352],
                    'cl': [352, 368, 416, 432, 480, 864, 880, 928, 944, 992],
                    'cc': [322, 324, 328, 336, 352, 368, 834, 836, 840, 848, 864, 880, 386, 388, 392, 400, 416, 432, 898, 900, 904, 928, 944, 480, 992],
                    'cs': [328, 392, 840, 904, 1350],
                    'ci': [322, 324, 328, 336, 352, 368, 386, 388, 392, 400, 416, 432, 480, 834, 836, 840, 848, 864, 880, 898, 900, 904, 912, 928, 944, 992],
                    'w': [324, 388, 836, 900, 1348]}

        for root in self.qa_dict:
            file_name = self.qa_dict[root]
            val_set = set()  # set of integer values from the QA band to search for
            print(' Reading', file_name)

            driver = gdal.GetDriverByName('GTiff')  # open GeoTIFF driver
            driver.Register()  # register driver

            # Get input file
            input_qa_dataset = gdal.Open(os.path.join(root, file_name), gdalconst.GA_ReadOnly)

            cols = input_qa_dataset.RasterXSize  # get required attributes
            rows = input_qa_dataset.RasterYSize
            projection = input_qa_dataset.GetProjection()
            metadata = input_qa_dataset.GetMetadata()
            geo_transform = input_qa_dataset.GetGeoTransform()

            input_qa_band = input_qa_dataset.GetRasterBand(1)  # get the qa band
            input_qa_data = input_qa_band.ReadAsArray(0, 0, cols, rows)  # read band into an Array

            # Initialize appropriate band files from command line arguments.
            if self.args.water:
                self.water_dict['dict'] = self.build_output('water', root, file_name, cols, rows)
                self.water_dict[root] = '/' + file_name[0:-4] + '_water.tif'
                for i in val_dict['w']:
                    val_set.add(i)

            if self.args.fill:
                self.fill_dict['dict'] = self.build_output('fill', root, file_name, cols, rows)
                self.fill_dict[root] = '/' + file_name[0:-4] + '_fill.tif'
                val_set.add(1)

            if self.args.terrain_occlusion:
                self.terrain_occlusion_dict['dict'] = \
                    self.build_output('terrain_occlusion', root, file_name, cols, rows)
                self.terrain_occlusion_dict[root] = '/' + file_name[0:-4] + '_terrain_occlusion.tif'
                val_set.add(2)

            if self.args.radiometric_saturation:
                self.rad_sat_dict['dict'] = self.build_output('rad_sat', root, file_name, cols, rows)
                self.rad_sat_dict[root] = '/' + file_name[0:-4] + '_rad_sat.tif'
                for i in val_dict['r']:
                    val_set.add(i)

            if self.args.clouds:
                self.clouds_dict['dict'] = self.build_output('clouds', root, file_name, cols, rows)
                self.clouds_dict[root] = '/' + file_name[0:-4] + '_clouds.tif'
                for i in val_dict['cl']:
                    val_set.add(i)

            if self.args.cloud_confidence:
                self.cloud_conf_dict['dict'] = self.build_output('cloud_conf', root, file_name, cols, rows)
                self.cloud_conf_dict[root] = '/' + file_name[0:-4] + '_cloud_conf.tif'
                for i in val_dict['cc']:
                    val_set.add(i)

            if self.args.cloud_shadow:
                self.cloud_shadow_dict['dict'] = self.build_output('cloud_shadow', root, file_name, cols, rows)
                self.cloud_shadow_dict[root] = '/' + file_name[0:-4] + '_cloud_shadow.tif'
                for i in val_dict['cs']:
                    val_set.add(i)

            if self.args.snow_ice:
                self.snow_ice_dict['dict'] = self.build_output('snow_ice', root, file_name, cols, rows)
                self.snow_ice_dict[root] = '/' + file_name[0:-4] + '_snow_ice.tif'
                for i in val_dict['s']:
                    val_set.add(i)

            if self.args.cirrus:
                self.cirrus_dict['dict'] = self.build_output('cirrus', root, file_name, cols, rows)
                self.cirrus_dict[root] = '/' + file_name[0:-4] + '_cirrus.tif'
                for i in val_dict['ci']:
                    val_set.add(i)

            if self.args.clear_terrain:
                self.clear_terrain_dict['dict'] = self.build_output('clear_terrain', root, file_name, cols, rows)
                self.clear_terrain_dict[root] = '/' + file_name[0:-4] + '_clear_terrain.tif'
                for i in val_dict['c']:
                    val_set.add(i)

            # Traverse entire input qa image, assign values in the new QA bands.
            for y in range(0, rows):
                for x in range(0, cols):
                    val = int(input_qa_data[y][x])

                    if val in val_set:

                        if self.args.fill:
                            if val == 1:
                                self.fill_dict['dict']['fill_values'][y][x] = 1
                                continue

                        if self.args.terrain_occlusion:
                            if val in val_dict['t']:
                                self.terrain_occlusion_dict['dict']['terrain_occlusion_values'][y][x] = val
                                continue

                        if self.args.cloud_shadow:
                            if val in val_dict['cs']:
                                self.cloud_shadow_dict['dict']['cloud_shadow_values'][y][x] = val

                        if self.args.clear_terrain:
                            if val in val_dict['c']:
                                self.clear_terrain_dict['dict']['clear_terrain_values'][y][x] = val
                        
                        if self.args.water:
                            if val in val_dict['w']:
                                self.water_dict['dict']['water_values'][y][x] = val

                        if self.args.radiometric_saturation:
                            if val in (2724, 2728, 2732, 2804, 2808, 2812, 3748, 3752, 3756, 6820, 6824, 6828):
                                self.rad_sat_dict['dict']['rad_sat_values'][y][x] = val

                        if self.args.clouds:
                            if val in val_dict['cl']:
                                self.clouds_dict['dict']['clouds_values'][y][x] = val

                        if self.args.cloud_confidence:
                            if val in val_dict['cc']:
                                self.cloud_conf_dict['dict']['cloud_conf_values'][y][x] = val

                        if self.args.cirrus:
                            if val in val_dict['ci']:
                                self.cirrus_dict['dict']['cirrus_values'][y][x] = val

                        if self.args.snow_ice:
                            if val in val_dict['s']:
                                self.snow_ice_dict['dict']['snow_ice_values'][y][x] = val

            # Write value Arrays and other attributes.
            if self.args.fill:
                self.write_output('fill', self.fill_dict.pop('dict'), projection, geo_transform, metadata)

            if self.args.terrain_occlusion:
                self.write_output \
                    ('terrain_occlusion', self.terrain_occlusion_dict.pop('dict'), projection, geo_transform, metadata)

            if self.args.radiometric_saturation:
                self.write_output('rad_sat', self.rad_sat_dict.pop('dict'), projection, geo_transform, metadata)

            if self.args.clouds:
                self.write_output('clouds', self.clouds_dict.pop('dict'), projection, geo_transform, metadata)

            if self.args.cloud_confidence:
                self.write_output('cloud_conf', self.cloud_conf_dict.pop('dict'), projection, geo_transform, metadata)

            if self.args.cloud_shadow:
                self.write_output('cloud_shadow', self.cloud_shadow_dict.pop('dict'), projection, geo_transform,
                                  metadata)

            if self.args.snow_ice:
                self.write_output('snow_ice', self.snow_ice_dict.pop('dict'), projection, geo_transform, metadata)

            if self.args.cirrus:
                self.write_output('cirrus', self.cirrus_dict.pop('dict'), projection, geo_transform, metadata)

            if self.args.clear_terrain:
                self.write_output('clear_terrain', self.clear_terrain_dict.pop('dict'), projection, geo_transform,
                                  metadata)
            if self.args.water:
                self.write_output('water', self.water_dict.pop('dict'), projection, geo_transform,
                                  metadata)

    def build_output(self, band_name, root, file_name, cols, rows):
        driver = gdal.GetDriverByName('GTiff')  # open GeoTIFF driver
        driver.Register()  # register driver

        band_dict = {}

        band_dict['suffix'] = '/' + file_name[0:-4] + '_' + band_name + '.tif'
        band_dict[band_name + '_dataset'] = driver.Create(root + band_dict['suffix'], cols, rows, 1, gdal.GDT_UInt16)
        band_dict[band_name + '_band'] = band_dict[band_name + '_dataset'].GetRasterBand(1)
        band_dict[band_name + '_values'] = band_dict[band_name + '_band'].ReadAsArray(0, 0, cols, rows)

        return band_dict

    def write_output(self, band, band_dict, projection, geotransform, metadata):
        print('    Writing ', band_dict['suffix'])
        band_dict[band + '_band'].WriteArray(band_dict[band + '_values'], 0, 0)
        band_dict[band + '_band'].SetNoDataValue(self.nodatavalue)
        band_dict[band + '_dataset'].SetProjection(projection)
        band_dict[band + '_dataset'].SetGeoTransform(geotransform)
        band_dict[band + '_dataset'].SetMetadata(metadata)

    def build_composites(self):

        print('Building composites...')

        if self.args.fill:
            write_composites('fill', self.fill_dict)

        if self.args.terrain_occlusion:
            write_composites('terrain_occlusion', self.terrain_occlusion_dict)

        if self.args.clear_terrain:
            write_composites('clear_terrain', self.clear_terrain_dict)

        if self.args.radiometric_saturation:
            write_composites('radiometric_saturation', self.rad_sat_dict)

        if self.args.clouds:
            write_composites('clouds', self.clouds_dict)

        if self.args.cloud_confidence:
            write_composites('cloud_confidence', self.cloud_conf_dict)

        if self.args.cloud_shadow:
            write_composites('cloud_shadow', self.cloud_shadow_dict)

        if self.args.cirrus:
            write_composites('cirrus', self.cirrus_dict)

        if self.args.snow_ice:
            write_composites('snow_ice', self.snow_ice_dict)

        if self.args.water:
            write_composites('water', self.water_dict)


def write_composites(band, band_dict):
    print('Writing ' + band + ' composite...')
    image_list = []

    for key in band_dict:
        image_list.append(key + band_dict[key])

    out_vrt = './outvrt.vrt'
    out_image = './' + band + '_composite.tif'
    out_ds = gdal.BuildVRT(out_vrt, image_list, separate=True)
    out_ds = gdal.Translate(out_image, out_ds)
    os.system('rm ./outvrt.vrt')


def parse_args():
    parser = argparse.ArgumentParser(
        description='Search through current directory and all subdirectories. Unpack Landsat '
                    'quality bands based on flags of your choice, and then create a quality assessment '
                    'composite \'layer stack\' for each quality assessment measure you chose. \n')
# water 324, 388, 836, 900, 1348
    parser.add_argument('-c', '--clear-terrain',
                        action='store_const',
                        const='-c',
                        required=False,
                        help='The -c flag will create a new GeoTiff with clear terrain values '
                             '(322, 386, 834, 898, 1346)'
                             'from the Landsat qa band, and a composite image of the new GeoTiffs. '
                             'This band summarizes pixels with no detected atmospheric interference, but'
                             'may include radiometric saturation. '
                             'This flag alone is probably enough for most cases. \n')
    parser.add_argument('-f', '--fill',
                        action='store_const',
                        const='-f',
                        required=False,
                        help='The -f flag will create a new GeoTIFF with fill value (1) from the'
                             'Landsat qa band, and a composite image of the new GeoTiffs. '
                             'This is unnecessary for most uses. \n')
    parser.add_argument('-t', '--terrain-occlusion',
                        action='store_const',
                        const='-t',
                        required=False,
                        help='The -t flag will create a new GeoTIFF with terrain occlusion value (1346, 1348, 1350, 1352)'
                             'from the Landsat qa band, and a composite image of the new GeoTiffs. \n')
    # TODO, values in separate tif
    parser.add_argument('-r', '--radiometric-saturation',
                        required=False,
                        action='store_const',
                        const='-r',
                        help='The -r flag will create a new GeoTIFF with radiometric saturation values '
                             '(2724, 2728, 2732, 2804, 2808, 2812, 3748, 3752, 3756, 6820, 6824, 6828)'
                             'from the Landsat qa band, and a composite image of the new GeoTiffs. \n')
    parser.add_argument('-cl', '--clouds',
                        required=False,
                        action='store_const',
                        const='-cl',
                        help='The -cl flag will create a new GeoTIFF with cloud values '
                             '(352, 368, 416, 432, 480, 864, 880, 928, 944, 992) from the Landsat qa band, '
                             'and a composite image of the new GeoTiffs. \n')
    parser.add_argument('-cc', '--cloud-confidence',
                        required=False,
                        action='store_const',
                        const='-cc',
                        help='The -cc flag will create a new GeoTIFF with cloud confidence values'
                             '(322, 324, 328, 336, 352, 368, 834, 836, 840, 848, 864, 880, 386, 388, 392, 400, 416, 432, 898, 900, 904, 928, 944, 480, 992) from the Landsat qa band, '
                             'and a composite image of the new GeoTiffs. \n')
    parser.add_argument('-cs', '--cloud-shadow',
                        required=False,
                        action='store_const',
                        const='-cs',
                        help='The -cs flag will create a new GeoTIFF with cloud shadow values (328, 392, 840, 904, 1350)'
                             'from the Landsat qa band, and a composite image of the new GeoTiffs. \n')
    parser.add_argument('-ci', '--cirrus',
                        required=False,
                        action='store_const',
                        const='-ci',
                        help='The -ci flag will create a new GeoTIFF with cirrus cloud values '
                             '(s 322, 324, 328, 336, 352, 368, 386, 388, 392, 400, 416, 432, 480, 834, 836, 840, 848, 864, 880, 898, 900, 904, 912, 928, 944, 992) from the Landsat qa band, '
                             'and a composite image of the new GeoTiffs. \n')
    parser.add_argument('-s', '--snow-ice',
                        required=False,
                        action='store_const',
                        const='-s',
                        help='The -s flag will create a new GeoTIFF with snow and ice values '
                             '(336, 368, 400, 432, 848, 880, 912, 944, 1352) from the Landsat qa band, '
                             'and a composite image of the new GeoTiffs. \n')
    parser.add_argument('-w', '--water',
                        required=False,
                        action='store_const',
                        const='-w',
                        help='The -w flag will create a new GeoTIFF with water values '
                             '324, 388, 836, 900, 1348 from the Landsat qa band, '
                             'and a composite image of the new GeoTiffs. \n')
    args = parser.parse_args()

    if len(sys.argv) == 1:
        print('Type landsat_L1_qa_tool -h for help options')
        quit()

    return args


def main():
    args = parse_args()  # parse command line arguments
    qc = QualityBandConverter(args)  # initialize a QualityBandConverter
    qc.find_qa_files()  # find all Landsat qa files in current dir and all subdirs
    qc.split_qa_bands()  # make new quality bands based on command line args
    qc.build_composites()  # build QA band composites based on command line args
    print('Done!')


if __name__ == '__main__':
    main()
