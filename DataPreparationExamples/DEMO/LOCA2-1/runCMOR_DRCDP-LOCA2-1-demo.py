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
inputJson = "DRCDP-LOCA2-1-demo_user_input.json"  # Update contents of this file to set your global_attributes
inputFilePath = "DRCDP-LOCA2-1_demo_data.nc"
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
cmor.load_table(cmorTable)

# Create CMOR axes
cmorLat = cmor.axis(
    "latitude", coord_vals=lat[:], cell_bounds=f.lat_bnds.values, units="degrees_north"
)
cmorLon = cmor.axis(
    "longitude", coord_vals=lon[:], cell_bounds=f.lon_bnds.values, units="degrees_east"
)
cmorTime = cmor.axis("time", coord_vals=time[:], cell_bounds=tbds, units=f.time.units)
cmoraxes = [cmorTime, cmorLat, cmorLon]

# Create CMOR variable to write - see https://cmor.llnl.gov/mydoc_cmor3_api/#cmor_set_variable_attribute
varid = cmor.variable(outputVarName, outputUnits, cmoraxes, missing_value=1.0e20)
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
cmor.write(varid, d, len(time))
cmor.close()
f.close()
