import cmor
import os
import sys
import numpy as np
import xcdat as xc

#%% Notes
# to-do
# add  "Header":{ ... "table_id": "Table grids", to ../../Tables/DRCDP_grids.json 

# %% Get current script path, append src dir
current_dir = os.path.dirname(os.path.abspath(__file__))
new_path = os.path.join(current_dir, "..", "..", "src")
sys.path.append(new_path)
from DRCDPLib import writeUserJson

# %% start user input below

cmorTable = "../../Tables/DRCDP_APday.json"  # APday, APmon,LPday, LPmon - Load target table, axis info (coordinates, grid*) and CVs
inputJson = "DRCDP-MACA3-0-demo_user_input.json"  # Update contents of this file to set your global_attributes
# inputFilePath = "macav3_ACCESS-CM2_historical_2009.nc"
inputFilePath = "tasmax_macav3_ACCESS-CM2_historical_20090101-20090107.nc"
inputVarName = "tasmax"
outputVarName = "tasmax"
outputUnits = "K"

# Open and read input netcdf file, get coordinates and add bounds
f = xc.open_dataset(inputFilePath, decode_times=False)
d = f[inputVarName]
lat = f.lat.values
lon = f.lon.values
time = f.time.values
f = f.bounds.add_missing_bounds(axes=["X", "Y"])
f = f.bounds.add_bounds("T")
tbds = f.time_bnds.values
d = np.where(np.isnan(d), 1.0e20, d)

# Initialize and run CMOR. For more information see https://cmor.llnl.gov/mydoc_cmor3_api/
cmor.setup(
    inpath="./", netcdf_file_action=cmor.CMOR_REPLACE_4
)  # ,logfile='cmorLog.txt')
cmor.dataset_json(
    writeUserJson(inputJson, cmorTable)
)  # use function to add CMOR and DRCDP required arguments

# Prepare crs variable
gridTable = cmor.load_table("../../Tables/DRCDP_grids.json")
cmor.set_table(gridTable)
latGrid, lonGrid = np.broadcast_arrays(
    np.expand_dims(lat[:], 0), np.expand_dims(lon[:], 1)
)
crs_wkt = "".join(
    [
        'GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,',
        '298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG",',
        '"6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],',
        'UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],',
        'AUTHORITY["EPSG","4326"]]',
    ]
)
crs_params = {
    "grid_mapping_name": "latitude_longitude",
    "longitude_of_prime_meridian": np.float64(0.0),
    "semi_major_axis": np.float64(6378137.0),
    "long_name": "WGS 84",
    "inverse_flattening": np.float64(298.257223563),
    "GeoTransform": "-179.5 0.1 0 74.5 0.1",
    "crs_wkt": crs_wkt,
}
grid_params = {
    "longitude_of_prime_meridian": [np.float64(0.0), "degrees_east"],
    "semi_major_axis": {"value": np.float64(6378137.0), "units": "meters"},
    "long_name": "WGS 84",
    "inverse_flattening": (np.float64(298.257223563), ""),
    "GeoTransform": "-179.5 0.1 0 74.5 0.1",
    "crs_wkt": crs_wkt,
}

# Create CMOR spatial axes
cmorLat = cmor.axis(
    "latitude", coord_vals=lat[:], cell_bounds=f.lat_bnds.values, units="degrees_north"
)
cmorLon = cmor.axis(
    "longitude", coord_vals=lon[:], cell_bounds=f.lon_bnds.values, units="degrees_east"
)

# Load CMOR tables
cmor.load_table(cmorTable)

# Create CMOR time axis
cmorTime = cmor.axis("time", coord_vals=time[:], cell_bounds=tbds, units=f.time.units)
cmoraxes = [cmorTime, cmorLat, cmorLon]

## gridId = cmor.grid(axis_ids=cmoraxes, latitude=latGrid, longitude=lonGrid)
gridId = cmor.grid(axis_ids=[cmorLat, cmorLon], latitude=latGrid, longitude=lonGrid)
# cmoraxes.append(gridId)

# Call cmor.set_crs
cmor.set_crs(
    grid_id=gridId,
    mapping_name=crs_params["grid_mapping_name"],
    parameter_names=grid_params,
)

# Create CMOR variable to write - see https://cmor.llnl.gov/mydoc_cmor3_api/#cmor_set_variable_attribute
##varid = cmor.variable(outputVarName, outputUnits, cmoraxes, missing_value=1.0e20)
varid = cmor.variable(
    outputVarName, outputUnits, [cmorTime, gridId], missing_value=1.0e20
)
values = np.array(d, np.float32)[:]

# Append valid_min and valid_max attributes to variable - see https://cmor.llnl.gov/mydoc_cmor3_api/#cmor_set_variable_attribute
# cmor.set_variable_attribute(varid,'valid_min','f',2.0)
# cmor.set_variable_attribute(varid,'valid_max','f',3.0)

# Prepare variable (quantization [commented] and compression), write and close file - see https://cmor.llnl.gov/mydoc_cmor3_api/#cmor_set_variable_attribute
# cmor.set_quantize(
#    varid, 1, 1
# )  # https://cmor.llnl.gov/mydoc_cmor3_api/#cmor_set_quantize
cmor.set_deflate(
    varid, 1, 1, 1
)  # shuffle=1,deflate=1,deflate_level=1 - Deflate options compress file data
# cmor.write(varid, d, len(time))  # ! Warning: You defined variable "tasmax" (table APday) with a missing value of type "f",
#                                     but you are now writing data of type: "d" this may lead to some spurious handling of the missing values
cmor.write(
    varid, values, len(time)
)  # fix issue with non-rewritten type (also fix in LOCA2-1 demo)
cmor.close()
f.close()
