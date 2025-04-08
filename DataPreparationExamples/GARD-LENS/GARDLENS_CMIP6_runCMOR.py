import cmor
import xcdat as xc
import xarray as xr
import cftime
import numpy as np
import sys, os, glob
from datetime import datetime

# %% Get current script path, append src dir
current_dir = os.path.dirname(os.path.abspath(__file__))
new_path = os.path.join(current_dir, "..", "..", "src")
sys.path.append(new_path)
from DRCDPLib import writeUserJson

### RUNNING PARALLEL VIA jobs.txt
multi  = False 
if multi == True:
 vari = sys.argv[1]
 domain = sys.argv[2]
 modi = sys.argv[3]
 rn = sys.argv[4]
 outputVarName = vari
 if vari == 'pr': outputUnits = 'kg m-2 s-1'
 if vari == 'tasmax': outputUnits = 'K'
 if vari == 'tasmin': outputUnits = 'K'

# TEST
vari = 'pcp'
domain = 'CONUS'
mod = 'ecearth3'
rn = 'r150i1p1f1'
outputVarName = 'pr' 
outputUnits = 'kg m-2 s-1'

# CMOR TABLES
cmorTable = '../../Tables/DRCDP_APday.json'
inputJson = 'GARDLENS_CMIP6_input.json'

inFile = '/global/cfs/projectdirs/m2637/GARDLENS/' + vari + '/GARDLENS_' + mod + '_' + rn + '_' + vari + '_1970_2100_' + domain + '.nc'

start_time = datetime.now()
#fc = xc.open_mfdataset(inFile,decode_times=True,use_cftime=True, preprocess=extract_date)
fc = xc.open_dataset(inFile,decode_times=False,use_cftime=False)
fc = fc.isel(time=slice(0,100))  # test 100 time steps
d = fc[vari]

lat = fc.lat.values  
lon = fc.lon.values  
time = fc.time.values 
tunits = fc.time.units 

fc = fc.bounds.add_bounds("X") 
fc = fc.bounds.add_bounds("Y")
fc = fc.bounds.add_bounds("T")

##### CMOR setup
cmor.setup(inpath='./',netcdf_file_action=cmor.CMOR_REPLACE_4,logfile= vari + '_' + mod + '-' + rn + '-'+'cmorLog.txt')
cmor.dataset_json(writeUserJson(inputJson, cmorTable))
cmor.load_table(cmorTable)

# SET CMIP MODEL SPECIFIC ATTRIBUTES 
#cmor.set_cur_dataset_attribute("source_id","LOCA2--" + mod)
cmor.set_cur_dataset_attribute("driving_source_id",mod)
cmor.set_cur_dataset_attribute("driving_variant_label",rn)
cmor.set_cur_dataset_attribute("driving_experiment_id",'historical')

# Create CMOR axes
cmorLat = cmor.axis("latitude", coord_vals=lat[:], cell_bounds=fc.lat_bnds.values, units="degrees_north")
cmorLon = cmor.axis("longitude", coord_vals=lon[:], cell_bounds=fc.lon_bnds.values, units="degrees_east")
cmorTime = cmor.axis("time", coord_vals=time[:], cell_bounds=fc.time_bnds.values[:], units= tunits)
cmoraxes = [cmorTime,cmorLat, cmorLon]

# Setup units and create variable to write using cmor - see https://cmor.llnl.gov/mydoc_cmor3_api/#cmor_set_variable_attribute
varid   = cmor.variable(outputVarName,outputUnits,cmoraxes,missing_value=1.e20)
values  = np.array(d[:],np.float32)

cmor.set_deflate(varid,1,1,1) ; # shuffle=1,deflate=1,deflate_level=1 - Deflate options compress file data
cmor.write(varid,values,len(time)) ; # Write variable with time axis
cmor.close()
f.close()
fc.close()
end_time = datetime.now()
print('done cmorizing ',mod, rn, vari,' process time: {}'.format(end_time-start_time))
                                                          
