import cmor
import os
import sys
import numpy as np
import xcdat as xc
import pyproj as pj

# %% Notes - to-do

# %% Get current script path, append src dir
current_dir = os.path.dirname(os.path.abspath(__file__))
new_path = os.path.join(current_dir, "..", "..", "..", "src")
sys.path.append(new_path)
from DRCDPLib import writeUserJson

# %% start user input below

cmorTable = "../../../Tables/DRCDP_AP1hr.json"  # AP1hr - Load target table, axis info (coordinates, grid*) and CVs
inputJson = "DRCDP-EDDE2-0-demo_user_input.json"  # Update contents of this file to set your global_attributes
inputFilePath = "DRCDP-EDDE2-0_demo_data.nc"
inputVarName = "PRECIP"
outputVarName = "pr"
outputUnits = "kg m-2 s-1"

# Open and read input netcdf file, get coordinates and add bounds
f = xc.open_dataset(inputFilePath, decode_times=False)
d = f[inputVarName]
x = f.x.values
y = f.y.values
latGrid = f.lat.values
lonGrid = f.lon.values
time = f.time.values
f = f.bounds.add_bounds("T")
tbds = f.time_bnds.values

# Initialize and run CMOR. For more information see https://cmor.llnl.gov/mydoc_cmor3_api/
cmor.setup(
    inpath="../../../Tables", netcdf_file_action=cmor.CMOR_REPLACE_4, logfile='cmorLog.txt'
)
cmor.dataset_json(
    writeUserJson(inputJson, cmorTable)
)  # use function to add CMOR and DRCDP required arguments

gridTable = cmor.load_table("../../../Tables/DRCDP_grids.json")
cmor.set_table(gridTable)

# Prepare crs variable
proj_str = f.attrs['CRS']
crs_proj = pj.CRS.from_string(proj_str)
crs_params = crs_proj.to_cf(wkt_version='WKT1_ESRI')
standard_parallel1, standard_parallel2 = crs_params.pop('standard_parallel')
crs_params['standard_parallel1'] = standard_parallel1
crs_params['standard_parallel2'] = standard_parallel2
for k, v in crs_params.items():
    if isinstance(v, float):
        crs_params[k] = {'value': v, 'units': ''}

# Convert longitude range from [-180, 180) to [0, 360)
lonGrid = lonGrid % 360.

# Create CMOR spatial axes and grid
cmorX = cmor.axis("x", coord_vals=x[:], units="m")
cmorY = cmor.axis("y", coord_vals=y[:], units="m")
gridId = cmor.grid(axis_ids=[cmorY, cmorX], latitude=latGrid, longitude=lonGrid)

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

# Convert precipitation amount to precipitation flux by dividing it by the number of seconds in an hour
pr = d / 3600.
pr = np.where(np.isnan(pr), 1.0e20, pr)
values = np.array(pr, np.float32)[:]

# Create CMOR variable to write - see https://cmor.llnl.gov/mydoc_cmor3_api/#cmor_set_variable_attribute
varId = cmor.variable(
    outputVarName, outputUnits, [cmorTime, gridId], missing_value=1.0e20
)

cmor.set_deflate(
    varId, 1, 1, 1
)  # shuffle=1,deflate=1,deflate_level=1 - Deflate options compress file data - see https://cmor.llnl.gov/mydoc_cmor3_api/#cmor_set_deflate

# Write variable to netcdf file
# cmor.write(varId, d, len(time))  # ! Warning: You defined variable "pr" (table AP1hr) with a missing value of type "f",
#                                     but you are now writing data of type: "d" this may lead to some spurious handling of the missing values
cmor.write(
    varId, values, len(time)
)
cmor.close()
f.close()
