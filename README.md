# GCP Asset Worksheet Tool

This tool uses the GCP Asset Inventory API to gather up desired resources and put them into an inventory worksheet that can be shared with external auditors and angencies for compliance and certification. 

## Supported Formats

Currently this tool can create the (FedRAMP Attachment 13 Template)[https://www.fedramp.gov/assets/resources/templates/SSP-A13-FedRAMP-Integrated-Inventory-Workbook-Template.xlsx]. For additional formats, please submit an RFE at in this repository. 

## Using the tool. 

A config file is required to use the Asset Worksheet Tool. The default filename is `.assetWorksheet.conf` in the current directory. This file name and location can be overwritten using a command-line switch. 

## Building

From the root directory: 

```
python3 -m build
```

## Installation 

The tool is available in PyPi. 

```
pip3 install assetWorksheet
```

### Config File Format

An example configuration file to create FedRAMP Attachment 13 inventories. The header fields can be manipulated  

```
[general]

company = CustomerName
cloud = Google Cloud Platform

[attachment]
outfile = gcp-inventory.csv

# The header fields to include in the FedRAMP Attachement 13
# report.
headerFields = 
  UNIQUE ASSET IDENTIFIER
  IPv4 or IPv6 Address	
  Physical/Virtual	
  Public	DNS Name or URL	
  NetBIOS Name	
  MAC Address	
  Authenticated Scan	
  Baseline Configuration 
  Name	
  OS Name and Version	
  Location	
  Asset Type	
  Hardware Make/Model	
  In Latest Scan	
  Software/Database Vendor	
  Software/Database Name & Version	
  Patch Level	
  Function	
  Comments	
  Serial No. /Asset Tag	
  VLAN/Network ID	
  System Administrator/Owner	
  Application Administrator/Owner

[asset]
# Scope to search under. 
# https://cloud.google.com/sdk/gcloud/reference/asset/search-all-resources
# Valid scopes
# projects/{PROJECT_ID} (e.g., projects/foo-bar)
# projects/{PROJECT_NUMBER} (e.g., projects/12345678)
# folders/{FOLDER_NUMBER} (e.g., folders/1234567)
# organizations/{ORGANIZATION_NUMBER} (e.g. organizations/123456)
scope = projects/myProject

# asset types to be included in the inventory attachment
# support asset types are documented at 
# https://cloud.google.com/asset-inventory/docs/supported-asset-types#searchable_asset_types
# k8s.io/Node and compute.googleapis.com/Instance create duplicate entries. 
# You should only pick one.
assetTypes = 
  appengine.googleapis.com/Service
  artifactregistry.googleapis.com/Repository	
  artifactregistry.googleapis.com/DockerImage
  run.googleapis.com/Service
  dns.googleapis.com/ManagedZone
  pubsub.googleapis.com/Topic
  pubsub.googleapis.com/Subscription
  storage.googleapis.com/Bucket
  compute.googleapis.com/Instance
  container.googleapis.com/Cluster
  k8s.io/Pod
```

### Command Line Options 

Several configurations can be set on the command line. These overwrite values in the configuration file. 

```
Usage: assetWorksheet [options]
Options:
  -h, --help            show this help message and exit
  -c CONFIG, --config=CONFIG
                        CONFIG file to read from. This can contain all
                        options. default: .assetWorksheet.conf
  -s SCOPE, --scope=SCOPE
                        SCOPE to run report for. Can be a project,
                        organization or folder. See
                        https://cloud.google.com/asset-inventory/docs/referenc
                        e/rest/v1/TopLevel/searchAllResources#path-parameters
                        for options
  -o OUTFILE, --outfile=OUTFILE
                        location to write attachment 13 report
  -t TYPE, --type=TYPE  type of worksheet to create. currently supported:
                        fedramp
```

## Contributing 

see (CONTRIBUTING)[CONTRIBUTING]