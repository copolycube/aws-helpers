#!/usr/bin/env python
# python3
# -*- coding: utf-8 -*-
# @author : copolycube

"""
Get all regions
    Get all instances
        from (by priority): tag['env'] > tag['Name']
        decide if ENV ={ production, staging, other }
        write this decision in a specific tag of the instance
"""
import boto3
from pprint import pprint
import re
from botocore.exceptions import ClientError

# DryRun=True
DryRun = False

# Which tag are we gonna use
DestinationTag = "ResGroup_ENV"


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


def get_instance_tags(ec2_resrc, instance_id):
    # ec2_rsrc = boto3.resource('ec2', region_name=get_current_default_region())
    ec2instance = ec2_resrc.Instance(instance_id)
    return t2d(ec2instance.tags)


def add_tag_to_instance(ec2_resrc, tag_name, tag_value, instance_id):
    tag_dict = {tag_name: tag_value}
    return ec2_resrc.create_tags(
        Resources=[instance_id], Tags=d2t(tag_dict), DryRun=DryRun
    )


def get_all_ec2_instances_resrc(ec2_resrc, region):
    # create filter for instances in running state
    filters = [{"Name": "instance-state-name", "Values": ["running"]}]
    # filter the instances based on filters() above
    instances = ec2_resrc.instances.filter(Filters=filters)

    # instantiate empty array
    running_instances = []

    for instance in instances:
        # for each instance, append to array and print instance id
        try:
            running_instances.append({"id": instance.id})
        except ClientError as e:
            print("{} {} {}".format(e.response["Error"]["Code"], region, instance.id))

    return running_instances


def decide_env(tested_env_string):
    """
    Test an input string to decide if it seems to be production or staging
    :return: production, staging, other
    """
    staging = re.match(".*staging.*", tested_env_string, re.IGNORECASE)
    production = re.match(".*prod.*", tested_env_string, re.IGNORECASE)
    if staging and production:
        return "other"
    elif staging:
        return "staging"
    elif production:
        return "production"
    else:
        return "other"


def from_instance_to_env(ec2_resrc, instance_id):
    tag_dict = get_instance_tags(ec2_resrc, instance_id)
    inst_tag_name = tag_dict.get("Name", "")
    inst_tag_env = tag_dict.get("env", "")

    if DestinationTag in tag_dict:
        print("# already set, return the same \n{} \n{}".format(instance_id, tag_dict))
        return tag_dict.get(DestinationTag)
    if "env" in tag_dict:
        # if we have an env, we just make the decision based on this value
        inst_tag_env = tag_dict["env"]

        if "Name" in tag_dict and decide_env(inst_tag_name) != decide_env(inst_tag_env):
            print(
                " !!non-coherent-env-and-Name!! for instance_id, we chose the ENV : {} \n   env {} \n   name {}".format(
                    instance_id, decide_env(inst_tag_env), decide_env(inst_tag_name)
                )
            )
        return decide_env(inst_tag_env)
    elif "Name" in tag_dict:
        # means we have no env tag
        inst_tag_name = tag_dict["Name"]
        return decide_env(inst_tag_name)
    else:
        print(
            "# no Tag:Name, no Tag:env : this shouldn't not happen ! \n{} \n{}".format(
                instance_id, tag_dict
            )
        )
        return "other-undefined"


def run_on_this_region(ec2_resource, region):
    """
    basic stub to run over all AWS regions
    :param ec2_resource:
    :return:
    """
    print(region)
    for instance in get_all_ec2_instances_resrc(ec2_resource, region):
        # pprint(instance)
        # pprint(get_instance_tags(ec2_resource, instance['id']))

        tags_present = get_instance_tags(ec2_resource, instance["id"])
        inst_name = tags_present.get("Name", "")
        inst_env = tags_present.get("env", "")
        print(
            "--- {:15} {:20} {:70} {:20} {:20} ".format(
                region,
                instance["id"],
                inst_name,
                inst_env,
                from_instance_to_env(ec2_resource, instance["id"]),
            )
        )
        add_tag_to_instance(
            ec2_resource,
            DestinationTag,
            from_instance_to_env(ec2_resource, instance["id"]),
            instance["id"],
        )


# ---- Now we do to the work

client = boto3.client("ec2")
regions = [region["RegionName"] for region in client.describe_regions()["Regions"]]
# regions = ['eu-west-2']
print(regions)

for reg in regions:
    ec2 = boto3.resource("ec2", region_name=reg)
    run_on_this_region(ec2, reg)
