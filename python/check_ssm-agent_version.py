#!/bin/python3
# output would be a table with each line like :
# <region> <ec2id> <ssm agent version> <ec2 name> 


import boto3
import os
import sys

client = boto3.client("ec2")
list_regions = [region['RegionName'] for region in client.describe_regions()['Regions']]

def ssm_version(id):
    response_ssm = client_ssm.describe_instance_information(
        Filters=[
            {
                'Key': 'InstanceIds',
                'Values': [
                    id,
                ]
            },
        ],
    )
    agent = response_ssm['InstanceInformationList'][0]['AgentVersion']
    return (id, agent)

def tag_name(tags):
    for tag in tags:
        if tag['Key'] == 'Name':
            return tag['Value']

if __name__ == '__main__':
    for region in list_region:
        try:
            client_ssm = boto3.client('ssm', region_name=region)
            resource_ec2 = boto3.resource('ec2', region_name=region)
            for instance in resource_ec2.instances.all():
                try:
                    #print(tags(instance.tags))
                    ssm = ssm_version(instance.id)
                    vartag_name = tag_name(instance.tags)
                    
                    original_stdout = sys.stdout # Save a reference to the original standard output

                    with open('output_version_ssm.txt', 'a') as f:
                        sys.stdout = f # Change the standard output to the file we created.
                        print("%s %s %s %s ResGroup_ENV:%s ResGroup_OS:%s" %(region, ssm[0], ssm[1], vartag_name, vartag_resenv, vartag_resos))
                        sys.stdout = original_stdout # Reset the standard output to its original value   
                except:
                    pass
                continue
        except:
            pass
        continue
        
  
