# Copyright 2022 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#  
# Requirements: VM Manager & Container Analysis for OS information

from optparse import OptionParser
import configparser
from google.cloud import asset_v1
import csv


class fedRampAttachment13:

  def __init__(self, options):

    self.config = self._loadConfigFile(options.config)

    # CLI override of config scope
    if options.scope is not None:
      self.config['asset']['scope'] == options.scope

    # CLI override of config outfile
    if options.outfile is not None:
      self.config['attachment']['outfile'] = options.outfile

  def _loadConfigFile(self, configFile):
    '''returns a config object'''

    try:
      config = configparser.ConfigParser()
      config.read(configFile)

      if self._checkConfigs(config):
        return config

    except Exception as e:
      print("Unable to load Config File {}".format(configFile))
      print(e)
      raise e

  def _checkConfigs(self, config):
    ''' Runs some basic checks for the loaded config file to make sure 
    the basics are in order. 
    '''

    # check for proper sections
    required_sections = ['general', 'attachment', 'asset']
    if config.sections() != required_sections:
      raise("Config Error - Required sections not present in config file")

    # if config['attachment']['bucket']:
    #   # attachment bucket is defined, but not a valid bucket name
    #   if not "gs://" in config['attachment']['bucket']:
    #     raise("Config Error - Attachment Bucket is not a valid bucket name")

    # attachment filename is not defined 
    if not config['attachment']['outfile']:
      raise("Config Error - No attachment filename configured")

    # asset scope is not defined
    if not config['asset']['scope']:
      raise("Config Error - No asset search scope identified")

    # everything checks out and it's OK to proceed
    return True

  def _getGcpAssets(self):
    '''Returns a list of assets as a google.cloud.asset_v1.types.asset_service.ListAssetsResponse object'''

    scope = self.config['asset']['scope']    
    asset_types = self.config['asset']['assettypes'].splitlines()[1:]
    client = asset_v1.AssetServiceClient()

    data = client.search_all_resources(
      request={
        "scope": scope,
        "asset_types": asset_types,
      }
    )
    
    return list(data)

  def _createAtt13Header(self):
    '''Returns a list object of column names for an Attachment 13 worksheet'''
    
    header = self.config['attachment']['headerFields'].splitlines()[1:]

    return header
  
  def createWorksheet(self):
    '''Takes a list of Assets and forms the 2D array to be turned into the attachment'''

    # the primary data object that we'll return. We'll build it all out with None values
    # to get it started, and we'll populate them in coming steps.
    data = list()

    # get the assets
    assets = self._getGcpAssets()

    # add the data values for each column
    data.append(self._createAtt13Header())
    for asset in assets:
        data.append(self._mapAsset(asset))
    
    self.createOutFile(data)
      
  def createOutFile(self, data):
    '''Writes worksheet to a local file'''
    
    attachmentDest = self.config['attachment']['outfile']

    fh = open(attachmentDest, 'w')
    wr = csv.writer(fh)
    wr.writerows(data)
    fh.close()
    
  def _uploadToGcs(self, data):
    
    pass

  def _mapAsset(self, asset):
    '''Takes the Attachment 13 header and maps asset values to them and returns a dictionary of header:value pairs
      This is a main function that will call multiple functions based on asset type'''

    # pull in a few configs
    company = self.config['general']['company']
    cloud = self.config['general']['cloud']

    # create a list of the proper length with placeholder objects
    data = [None]*23

    data[0] = asset.name
    data[2] = 'Virtual'
    data[4] = 'N/A'
    data[5] = 'N/A' # https://issuetracker.google.com/124605415
    data[6] = 'N/A'
    data[7] = 'N/A'
    data[8] = asset.display_name
    data[10] = asset.location
    data[11] = asset.asset_type
    data[13] = 'Yes'
    data[14] = cloud
    data[15] = cloud
    data[17] = asset.asset_type.split('/')[-1]
    data[21] = "{} Operationss".format(company)
    data[22] = company

    # Data is potentially different for datatypes for columns
    # 1,3,9,12,16,18,19,20

    match asset.asset_type:
      # VM Instance/GKE Node
      case 'compute.googleapis.com/Instance':
        # 1 IPv4 or IPv6 Address
        if 'externalIPs' in asset.additional_attributes.keys():
          #TODO: handle multiple external IPs
          data[1] = asset.additional_attributes['externalIPs'][0]
        else:
          data[1] = 'N/A'
        # 3 Public	DNS Name or URL
        data[3] = 'N/A'
        # 9 OS Name and Version	
        data[9] = asset.additional_attributes['osLongName']
        # 12 Hardware Make/Model
        data[12] = asset.additional_attributes['machineType']
        # 18 Comments
        data[18] = 'GCE VM Instance'
        # 19 Serial/Asset Tag#
        data[19] = asset.additional_attributes['id']
        # 20 VLAN/Network ID
        data[20] = asset.additional_attributes['networkInterfaceNetworks'][0].split('/')[-1]
      
      # GKE Cluster
      case 'container.googleapis.com/Cluster':
        data[1] = asset.additional_attributes['endpoint']
        data[3] = 'N/A'
        data[12] = 'GKE Kubernetes Cluster'
        data[18] = asset.description
        data[20] = 'N/A'
        
      # GCS Bucket
      case 'storage.googleapis.com/Bucket':
        data[1] = 'N/A'
        data[3] = 'N/A'
        data[9] = 'N/A'
        data[12] = 'Cloud Storage Bucket'
        data[18] = 'N/A'
        data[19] = asset.name
        data[20] = 'N/A'
        
      # K8s Pod
      case 'k8s.io/Pod':
        data[1] = 'N/A'
        data[3] = 'N/A'
        data[9] = 'N/A'
        data[12] = 'Kubernetes Pod'
        data[18] = asset.description
        data[19] = asset.name
        data[20] = 'N/A'

    ''' FedRamp attachment Mapping
    0 UNIQUE ASSET IDENTIFIER
    1 IPv4 or IPv6 Address	
    2 Physical/Virtual
    3 Public	DNS Name or URL	
    4 NetBIOS Name	
    5 MAC Address	
    6 Authenticated Scan	
    7 Baseline Configuration 
    8 Name	
    9 OS Name and Version	
    10 Location	
    11 Asset Type	
    12 Hardware Make/Model	
    13 In Latest Scan	
    14 Software/Database Vendor	
    15 Software/Database Name & Version	
    16 Patch Level	
    17 Function	
    18 Comments	
    19 Serial/Asset Tag#	
    20 VLAN/Network ID	
    21 System Administrator/Owner	
    22 Application Administrator/Owner
    '''

    return data

def loadCliOptions():
  
  usage = "usage: %prog [options]"
  parser = OptionParser(usage=usage)
  parser.add_option("-c", "--config", dest="config", metavar="CONFIG", default=".assetWorksheet.conf",
                    help="CONFIG file to read from. This can contain all options. default: .assetWorksheet.conf")
  parser.add_option("-s", "--scope", dest="scope", metavar="SCOPE",
                    help="SCOPE to run report for. Can be a project, organization or folder. See https://cloud.google.com/asset-inventory/docs/reference/rest/v1/TopLevel/searchAllResources#path-parameters for options")
  parser.add_option("-o", "--outfile", dest="outfile", metavar="OUTFILE", 
                    help="location to write attachment 13 report")
  parser.add_option("-t", "--type", dest="type", metavar="TYPE", default="fedramp",
                    help="type of worksheet to create. currently supported: fedramp")
  
  return parser.parse_args()
  
def createWorksheet():
  '''primary entrypoint for CLI tools'''
  
  options, args = loadCliOptions()
  
  # handles fedramp worksheets.
  if options.type == "fedramp":
    data = fedRampAttachment13(options)
    data.createWorksheet()
  
if __name__ == '__main__':
    createWorksheet() 
