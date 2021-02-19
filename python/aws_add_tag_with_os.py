#!/usr/bin/env python
# python3
# -*- coding: utf-8 -*-
# @author : copolycube
"""
Get the current region,
get all instances
    get it's private ip
    connect with the private ip and get a string describing the OS
    work on that string
    write this back in the instance in a tag
"""

import boto3
import subprocess
from botocore.exceptions import ClientError
from pprint import pprint
import json
import re

DryRun=True
# DryRun = False

# Which tag are we gonna use
DestinationTag = "ResGroup_OS"
DestinationTagPatchGroup = "Patch Group"


# def get_ec2_id_from_private_ip(instance_id):
#     # instance_id = '10.115.121.183'
#     try:
#         for instance in ec2.instances.all():
#             if instance.private_ip_address == instance_id:
#                 print("Instance ID: " + instance.instance_id, '\n')
#     except ClientError as e:
#         print("Error", e)


# tag helpers
def t2d(tags) -> dict:
    """Convert a tag list to a dictionary.
    Example:
        >>> t2d([{'Key' : 'Name','Value' : 'foobar'}])
        {'Name': 'foobar'}
    """
    if tags is None:
        return {}
    return {el["Key"]: el["Value"] for el in tags}


def d2t(tag_dict=None, **kwargs) -> list:
    """Convert a dictionary to a tag list.
    Example:
        >>> d2t({'Name': 'foobar'}) == [{'Value': 'foobar', 'Key': 'Name'}]
        True
        >>> d2t(Name='foobar') == [{'Value': 'foobar', 'Key': 'Name'}]
        True
    """
    tag_dict = {} if tag_dict is None else dict(tag_dict)
    tag_dict.update(kwargs)
    return [{"Key": k, "Value": v} for k, v in tag_dict.items()]


def add_tag_to_instance(tag_name, tag_value, instance_id):
    tag_dict = {tag_name: tag_value}
    response = ec2_resrc.create_tags(Resources=[instance_id], Tags=d2t(tag_dict))
    pprint(response)


def get_current_default_region():
    sess = boto3.session.Session()
    return sess.region_name


def get_all_ec2_instances_running():
    list_ec2_id_ip = []
    response = ec2_client.describe_instances(
        Filters=[
            {
                "Name": "instance-state-code",
                "Values": [
                    "16",
                ],
            },
        ],
    )
    for i in response["Reservations"]:
        for ins in i["Instances"]:
            print("{} {}".format(ins["InstanceId"], ins["PrivateIpAddress"]))
            list_ec2_id_ip.append(
                {"id": ins["InstanceId"], "private-ip": ins["PrivateIpAddress"]}
            )
    return list_ec2_id_ip


ec2_resrc = boto3.resource("ec2", region_name=get_current_default_region())
ec2_client = boto3.client("ec2", region_name=get_current_default_region())


def get_instance_name(instance_id):
    # When given an instance ID as str e.g. 'i-1234567', return the instance 'Name' from the name tag.
    ec2_resource = boto3.resource("ec2", region_name=get_current_default_region())
    ec2instance = ec2_resource.Instance(instance_id)
    for tags in ec2instance.tags:
        if tags["Key"] == "Name":
            return tags["Value"]


def get_instance_tags(instance_id):
    # ec2_rsrc = boto3.resource('ec2', region_name=get_current_default_region())
    ec2instance = ec2_resrc.Instance(instance_id)
    return t2d(ec2instance.tags)


def get_os_from_lsb_release(instance_ip_value):
    # cmd = "uname -a"
    cmd = "lsb_release -d"
    # cmd = 'source /etc/os-release && echo $ID $VERSION_ID'
    conn = subprocess.Popen(
        ["ssh", instance_ip_value, cmd],
        shell=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    res = conn.stdout.readlines()
    if len(res) > 0:
        return res[0]
    else:
        return ""


def get_os_from_etc_release(instance_ip_value):
    # cmd = "uname -a"
    # cmd = "lsb_release -d"
    cmd = "source /etc/*-release && echo $ID $VERSION_ID"
    conn = subprocess.Popen(
        ["ssh", instance_ip_value, cmd],
        shell=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    res = conn.stdout.readlines()
    if len(res) > 0:
        return res[0]
    else:
        return ""


def get_os_from_private_ip(instance_ip_value):
    lsb = get_os_from_lsb_release(instance_ip_value)
    if len(lsb) > 0:
        return lsb
    etc_release = get_os_from_etc_release(instance_ip_value)
    if len(etc_release) > 0:
        return etc_release
    else:
        return "undefined"


def pretty_os_ubuntu(os_str):
    # from :
    # "b'Description:\tUbuntu 14.04.6 LTS"
    # extract :
    # 'Ubuntu 14'
    regex = ".*(Ubuntu) (\d\d).*"
    try:
        found = re.search(regex, os_str).group(1) + re.search(regex, os_str).group(2)
    except AttributeError:
        # AAA, ZZZ not found in the original string
        found = os_str.strip("b'Description:\t")  # apply your error handling
    return found


def set_tags_to_instance(instance_id, tag_dict):
    response = ec2_resrc.create_tags(
        Resources=[instance_id], Tags=d2t(tag_dict), DryRun=DryRun
    )
    pprint(response)


for instance in get_all_ec2_instances_running():
    # if instance['id'] != 'i-007dfe23abe6d1855':
    #     continue
    tags_to_add = {}
    print("--- {}".format(instance["id"]))
    print(
        "--- {} {} {} ".format(
            instance["id"],
            get_instance_name(instance["id"]),
            get_os_from_private_ip(instance["private-ip"]),
        )
    )
    get_os_string = str(get_os_from_private_ip(instance["private-ip"]))

    print(get_os_string)

    if "buntu" in get_os_string:
        tags_to_add[DestinationTag] = pretty_os_ubuntu(get_os_string)
        tags_to_add[DestinationTagPatchGroup] = "patch-group-ubuntu"

    else:
        tags_to_add[DestinationTag] = get_os_string

    # if "amzn" in get_os_string:
    #     tags_to_add[DestinationTagPatchGroup] = "patch-group-amzn"
    # if "cent" in get_os_string:
    #     tags_to_add[DestinationTagPatchGroup] = "patch-group-centos"
    set_tags_to_instance(instance["id"], tags_to_add)
    pprint(get_instance_tags(instance["id"]))
