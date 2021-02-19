# python3
# -*- coding: utf-8 -*-
# @author : copolycube 2020
""" This file does nothing, it's just a bunch of helpers used around... """

import boto3
import pprint

from botocore.exceptions import ClientError


def get_current_default_region():
    sess = boto3.session.Session()
    return sess.region_name


def get_instance_name(instance_id):
    # When given an instance ID as str e.g. 'i-1234567', return the instance 'Name' from the name tag.
    ec2_resrc = boto3.resource('ec2', region_name=get_current_default_region())
    ec2instance = ec2_resrc.Instance(instance_id)
    for tags in ec2instance.tags:
        if tags["Key"] == 'Name':
            return tags["Value"]


# tag helpers
def t2d(tags) -> dict:
    """Convert a tag list to a dictionary.

    Example:
        >>> t2d([{'Key' : 'Name','Value' : 'foobar'}])
        {'Name': 'foobar'}
    """
    if tags is None:
        return {}
    return dict((el['Key'], el['Value']) for el in tags)


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
    return [{'Key': k, 'Value': v} for k, v in tag_dict.items()]


def set_tags_to_instance(instance_id, tag_dict):
    """
    This will not remove existing tags, but will  overwrite existing if present in tag_dict
    :param instance_id: instance id
    :param tag_dict: python dict containing tag Name as keys, and tag Value as values
    :return: pprint the response and returns it
    """
    ec2_resrc = boto3.resource('ec2', region_name=get_current_default_region())
    response = ec2_resrc.create_tags(Resources=[instance_id], Tags=d2t(tag_dict), DryRun=DryRun)
    pprint(response)
    return response


def add_tag_to_instance(ec2_resrc, tag_name, tag_value, instance_id):
    """

    :param ec2_resrc: boto3.resource('ec2', region_name=...) already initialized
    :param tag_name:
    :param tag_value:
    :param instance_id:
    :return:
    """
    tag_dict = {tag_name: tag_value}
    response = ec2_resrc.create_tags(Resources=[instance_id], Tags=d2t(tag_dict), DryRun=DryRun)
    pprint(response)
    return response


def get_instance_tags(instance_id):
    ec2_resrc = boto3.resource('ec2', region_name=get_current_default_region())
    ec2instance = ec2_resrc.Instance(instance_id)
    return t2d(ec2instance.tags)


# other helpers
def get_ec2_id_from_private_ip(instance_ip_value):
    """

    :param instance_ip_value:
    :return: instance ID
    """
    ec2_resrc = boto3.resource('ec2', region_name=get_current_default_region())

    # instance_id = '10.115.121.183'
    try:
        for instance in ec2_resrc.instances.all():
            if instance.private_ip_address == instance_ip_value:
                print("Instance ID: " + instance.instance_id)
                return instance.instance_id
    except ClientError as e:
        print("Error", e)
