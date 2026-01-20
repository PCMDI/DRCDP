import cmor
import os
import sys
import numpy as np
import xcdat as xc

# %% Notes - to-do

# %% Get current script path, append src dir
current_dir = os.path.dirname(os.path.abspath(__file__))
new_path = os.path.join(current_dir, "..", "..", "..", "src")
sys.path.append(new_path)
from DRCDPLib import writeUserJson

# %% start user input below

cmorTable = "../../../Tables/DRCDP_APday.json"  # APday, APmon,LPday, LPmon - Load target table, axis info (coordinates, grid*) and CVs
inputJson = "DRCDP-MACA3-0-demo_user_input.json"  # Update contents of this file to set your global_attributes
inputFilePath = "DRCDP-MACA3-0_demo_data.nc"
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
    inpath="../../../Tables", netcdf_file_action=cmor.CMOR_REPLACE_4
)  # ,logfile='cmorLog.txt')
cmor.dataset_json(
    writeUserJson(inputJson, cmorTable)
)  # use function to add CMOR and DRCDP required arguments

# Prepare crs variable
gridTable = cmor.load_table("../../../Tables/DRCDP_grids.json")
cmor.set_table(gridTable)
latGrid, lonGrid = np.broadcast_arrays(
    np.expand_dims(lat[:], 0), np.expand_dims(lon[:], 1)
)

crs_params = f.coords['crs'].attrs
for k, v in crs_params.items():
    if isinstance(v, np.floating):
        crs_params[k] = (v, "")
crs_params['crs_wkt'] = crs_params.pop('spatial_ref')

# Create CMOR spatial axes and grid
cmorLat = cmor.axis(
    "latitude", coord_vals=lat[:], cell_bounds=f.lat_bnds.values, units="degrees_north"
)
cmorLon = cmor.axis(
    "longitude", coord_vals=lon[:], cell_bounds=f.lon_bnds.values, units="degrees_east"
)
latVerts = np.concatenate((np.flip(f.lat_bnds.values, axis=1), f.lat_bnds.values), axis=1)
lonVerts = np.repeat(f.lon_bnds.values, 2, axis=1)
latVertsGrid, lonVertsGrid = np.broadcast_arrays(
    np.expand_dims(latVerts[:], 0), np.expand_dims(lonVerts[:], 1)
)
gridId = cmor.grid(axis_ids=[cmorLat, cmorLon], latitude=latGrid, longitude=lonGrid,
                   latitude_vertices=latVertsGrid, longitude_vertices=lonVertsGrid)

# Load CMOR tables
cmor.load_table(cmorTable)

# Create CMOR time axis
cmorTime = cmor.axis("time", coord_vals=time[:], cell_bounds=tbds, units=f.time.units)
# cmoraxes = [cmorTime, cmorLat, cmorLon]


# Call cmor.set_crs
cmor.set_crs(
    grid_id=gridId,
    mapping_name=crs_params["grid_mapping_name"],
    parameter_names=crs_params,
)

# Create CMOR variable to write - see https://cmor.llnl.gov/mydoc_cmor3_api/#cmor_set_variable_attribute
varId = cmor.variable(
    outputVarName, outputUnits, [cmorTime, gridId], missing_value=1.0e20
)
values = np.array(d, np.float32)[:]

# Append valid_min and valid_max attributes to variable - see https://cmor.llnl.gov/mydoc_cmor3_api/#cmor_set_variable_attribute
# cmor.set_variable_attribute(varId,'valid_min','f',2.0)
# cmor.set_variable_attribute(varId,'valid_max','f',3.0)

# Prepare variable (quantization [commented] and compression), write and close file - see https://cmor.llnl.gov/mydoc_cmor3_api/#cmor_set_variable_attribute
# cmor.set_quantize(
#    varId, 1, 1
# )  # https://cmor.llnl.gov/mydoc_cmor3_api/#cmor_set_quantize
cmor.set_deflate(
    varId, 1, 1, 1
)  # shuffle=1,deflate=1,deflate_level=1 - Deflate options compress file data - see https://cmor.llnl.gov/mydoc_cmor3_api/#cmor_set_deflate

# Write variable to netcdf file
# cmor.write(varId, d, len(time))  # ! Warning: You defined variable "tasmax" (table APday) with a missing value of type "f",
#                                     but you are now writing data of type: "d" this may lead to some spurious handling of the missing values
cmor.write(
    varId, values, len(time)
)  # fix issue with non-rewritten type (also fix in LOCA2-1 demo)
cmor.close()
f.close()
