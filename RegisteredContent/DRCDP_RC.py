import json

source_id = {}
source_id['source_id'] = {}
########################################################
### ADD NEW ENTRIES HERE
key = 'LOCA2'
source_id['source_id'][key] = {}
source_id['source_id'][key]['source_name'] = 'LOCA'
source_id['source_id'][key]['source_version_number'] = '2'
source_id['source_id'][key]['institution_id'] = 'UCSD-SIO'
source_id['source_id'][key]['region'] = ['north_america']

key = 'LOCA2.1'
source_id['source_id'][key] = {}
source_id['source_id'][key]['source_name'] = 'LOCA'
source_id['source_id'][key]['source_version_number'] = '2.1'
source_id['source_id'][key]['institution_id'] = 'UCSD-SIO'
source_id['source_id'][key]['region'] = ['north_america']

key = 'MACAV3'
source_id['source_id'][key] = {}
source_id['source_id'][key]['source_name'] = 'MACA'
source_id['source_id'][key]['source_version_number'] = 'V3'
source_id['source_id'][key]['institution_id'] = 'UCM-ACSL'
source_id['source_id'][key]['region'] = ['north_america']

key = 'STAR-ESDM-v1'
source_id['source_id'][key] = {}
source_id['source_id'][key]['source_name'] = 'STAR-ESDM'
source_id['source_id'][key]['source_version_number'] = 'v1'
source_id['source_id'][key]['institution_id'] = 'TTU'
source_id['source_id'][key]['region'] = ['north_america']
##########################################################
json_object = json.dumps(source_id, indent=4)
with open("DRCDP-RegisteredContent.json", "w") as outfile:
    outfile.write(json_object)

