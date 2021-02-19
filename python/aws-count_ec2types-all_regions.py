#! /usr/bin/python

# What : for all the regions, count the number of ec2 instance of each type
# Requirement : boto3 installed and authenticated

import boto3
from pprint import pprint

client = boto3.client('ec2')
regions = [region['RegionName'] for region in client.describe_regions()['Regions']]


def extract_data_for_one_region(answer):
    for instance in answer['Reservations']:
        # print("\n\n\n#################### ####################\n\n\n")
        this_instance_type = instance['Instances'][0]['InstanceType']
        this_instance_state = instance['Instances'][0]['State']['Name']
        pprint(instance['Instances'])

        print("####################")
        print(this_instance_type)
        print(this_instance_state)
        print(len(instance['Instances']))
        # print("#################### \n\n\n")
        ec2InstanceTypes[this_instance_type] = ec2InstanceTypes.get(this_instance_type, 0) + 1


for r in regions:
    ec2 = boto3.client('ec2', region_name=r)
    response = ec2.describe_instances()

    ec2InstanceTypes = {}
    # for i in response['Reservations'] :
    #     this_it = i['Instances'][0]['InstanceType']
    #     ec2InstanceTypes[this_it] = ec2InstanceTypes.get(this_it, 0) +1

    extract_data_for_one_region(response)

    for k, v in ec2InstanceTypes.items():
        print("%-20s%-20s%-20s" % (r, k, v))
