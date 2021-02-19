#!/usr/bin/env python
# python3
# -*- coding: utf-8 -*-
# @author : copolycube, 2020
"""
Get the current region,
get resource groups
    store the number of resources per rg.
"""

import boto3
import subprocess
from pprint import pprint

DryRun = True
# DryRun = False


def get_current_default_region():
    sess = boto3.session.Session()
    return sess.region_name


# ec2_rsrc = boto3.resource('ec2', region_name=get_current_default_region())
# ec2_client = boto3.client('ec2', region_name=get_current_default_region())


# for instance in get_all_ec2_instances():
#     # if instance['id'] != 'i-007dfe23abe6d1855':
#     #     continue
#     tags_to_add = {}
#     print("--- {}".format(instance['id']))
#     print("--- {} {} {} ".format(instance['id'],
#                                  get_instance_name(instance['id']),
#                                  check_if_jira_installed_from_private_ip(instance['private-ip'])
#                                  ))
#     rg_os_ver: str = (str(check_if_jira_installed_from_private_ip(instance['private-ip'])))
#     print(rg_os_ver)
#     tags_to_add[DestinationTag] = rg_os_ver
#     # if "Ubuntu" in rg_os_ver:
#     #     tags_to_add[DestinationTagPatchGroup] = "patch-group-ubuntu"
#     # if "Ubuntu 14" in rg_os_ver:
#     #     tags_to_add[DestinationTagPatchGroup] = "patch-group-ubuntu"
#     set_tags_to_instance(instance['id'], tags_to_add)
#     pprint(get_instance_tags(instance['id']))


all_reg_all_rg = {}
all_reg_all_rg_names = []


def list_resgroups_res(reg, rg_client, rg_arn, rg_name):
    response = rg_client.list_group_resources(
        GroupName=rg_name,
        # Group=rg_arn,
        Filters=[{"Name": "resource-type", "Values": ["AWS::EC2::Instance"]}],
    )
    # pprint(response['ResourceIdentifiers'])
    return len(response["ResourceIdentifiers"])


def list_resgroups(region, rg_client):
    response = rg_client.list_groups(
        Filters=[
            {"Name": "resource-type", "Values": ["AWS::EC2::Instance"]},
        ]
    )

    pprint(len(response["GroupIdentifiers"]))
    this_reg_all_rg = {}
    this_reg_all_rg.setdefault(0)
    for i in response["GroupIdentifiers"]:
        # this_reg_all_rg.append(['GroupName'])
        # print("{} {}".format(reg, i['GroupArn']))
        # print("{} {}".format(reg, i['GroupName']))
        all_reg_all_rg_names.append(i["GroupName"])
        this_reg_all_rg[i["GroupName"]] = list_resgroups_res(
            region, rg_client, i["GroupArn"], i["GroupName"]
        )
        this_reg_all_rg.setdefault(0)
        del this_reg_all_rg[0]
    all_reg_all_rg[reg] = this_reg_all_rg
    # pprint({(k,v) for (k,v) in response['GroupIdentifiers']})


def run_on_this_region(reg, rg_client):
    list_resgroups(reg, rg_client)
    # dict rg=list_resgroups(rg_client)


# ---- Now we do to the work

client = boto3.client("ec2")
# regions = [region['RegionName'] for region in client.describe_regions()['Regions']]
regions = [
    "eu-west-1",
    "eu-west-2",
    "eu-west-3",
    "eu-central-1",
    "ca-central-1",
    "us-east-1",
    "eu-north-1",
    "us-east-2",
]
# regions = ['eu-north-1', 'us-east-2']


print(regions)

for reg in regions:
    rg_client = boto3.client("resource-groups", region_name=reg)
    print("region:{}".format(reg))
    run_on_this_region(reg, rg_client)

pprint(all_reg_all_rg)
# pprint(list(all_reg_all_rg.keys()))
# pprint(['ResGroupName'] + list(all_reg_all_rg.keys()))

# pprint(set(all_reg_all_rg_names))

from prettytable import PrettyTable

x = PrettyTable()
x.field_names = ["ResGroupName"] + regions

for rsg_name in set(all_reg_all_rg_names):
    x.add_row(
        [rsg_name] + [all_reg_all_rg.get(r).get(rsg_name, "n/a") for r in regions]
    )

# x.add_rows(list(all_reg_all_rg.items()))
print(x)
