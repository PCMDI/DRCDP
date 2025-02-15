import cmor
import xcdat as xc
import xarray as xr
import cftime
import numpy as np
import sys, os, glob
from datetime import datetime


multi  = False 
if multi == True:
 vari = sys.argv[1]
 domain = sys.argv[2]
 modi = sys.argv[3]
 rn = sys.argv[4]

 inputVarName = vari
 outputVarName = vari
 if vari == 'pr': outputUnits = 'kg m-2 s-1'
 if vari == 'tasmax': outputUnits = 'K'
 if vari == 'tasmin': outputUnits = 'K'


vari = 'pcp'
domain = 'CONUS'
mod = 'ecearth3'
rn = 'r150i1p1f1'

inputVarName = vari
outputVarName = 'pr' 
outputUnits = 'kg m-2 s-1'


cmorTable = '../Tables/Downscaling_Aday.json'
inputJson = 'GARDLENS_CMIP6_input.json'

inFile = '/global/cfs/projectdirs/m2637/GARDLENS/' + vari + '/GARDLENS_' + mod + '_' + rn + '_' + vari + '_1970_2100_' + domain + '.nc'

start_time = datetime.now()
#fc = xc.open_mfdataset(inFile,decode_times=True,use_cftime=True, preprocess=extract_date)
fc = xc.open_dataset(inFile,decode_times=False,use_cftime=False)

f = fc
f = fc.isel(time=slice(0,100))
d = f[inputVarName]

lat = f.lat.values  
lon = f.lon.values  
time = f.time.values 
tunits = "days since 1900-01-01"

f = f.bounds.add_bounds("X") 
f = f.bounds.add_bounds("Y")
f = f.bounds.add_bounds("T")

##### CMOR setup
cmor.setup(inpath='./',netcdf_file_action=cmor.CMOR_REPLACE_4,logfile= vari + '_' + mod + '-' + rn + '-'+'cmorLog.txt')
cmor.dataset_json(inputJson)
cmor.load_table(cmorTable)

# SET CMIP MODEL SPECIFIC ATTRIBUTES 
cmor.set_cur_dataset_attribute("source_id","LOCA2--" + mod)
cmor.set_cur_dataset_attribute("driving_source_id",mod)
cmor.set_cur_dataset_attribute("driving_variant_label",rn)
cmor.set_cur_dataset_attribute("driving_experiment_id",'historical')

# Create CMOR axes
cmorLat = cmor.axis("latitude", coord_vals=lat[:], cell_bounds=f.lat_bnds.values, units="degrees_north")
cmorLon = cmor.axis("longitude", coord_vals=lon[:], cell_bounds=f.lon_bnds.values, units="degrees_east")
#cmorTime = cmor.axis("time", coord_vals=cftime.date2num(time,tunits), cell_bounds=cftime.date2num(f.time_bnds.values,tunits), units= tunits)
cmorTime = cmor.axis("time", coord_vals=time[:], cell_bounds=f.time_bnds.values[:], units= tunits)
cmoraxes = [cmorTime,cmorLat, cmorLon]

# Setup units and create variable to write using cmor - see https://cmor.llnl.gov/mydoc_cmor3_api/#cmor_set_variable_attribute
varid   = cmor.variable(outputVarName,outputUnits,cmoraxes,missing_value=1.e20)
values  = np.array(d[:],np.float32)

cmor.set_variable_attribute(varid,'valid_min','f',2.0)
cmor.set_variable_attribute(varid,'valid_max','f',3.0)

cmor.set_deflate(varid,1,1,1) ; # shuffle=1,deflate=1,deflate_level=1 - Deflate options compress file data
cmor.write(varid,values,len(time)) ; # Write variable with time axis
cmor.close()
f.close()
fc.close()
end_time = datetime.now()
print('done cmorizing ',mod, rn, vari,' process time: {}'.format(end_time-start_time))
                                                          
