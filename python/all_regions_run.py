#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author : copolycube, 2020


import boto3
from pprint import pprint


def run_on_this_region(ec2_client):
    """
    basic stub to run over all AWS regions
    :param ec2_client:
    :return:
    """
    pass


client = boto3.client('ec2')
regions = [region['RegionName'] for region in client.describe_regions()['Regions']]
print(regions)

for reg in regions:
    ec2 = boto3.client('ec2', region_name=reg)
    run_on_this_region(ec2)
