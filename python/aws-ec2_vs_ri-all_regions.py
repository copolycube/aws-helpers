#! /usr/bin/python

# What : for all the regions, count the number of ec2 RESERVED instance of each type
# Requirement : boto3 installed and authenticated

import boto3
from pprint import pprint

client = boto3.client('ec2')
regions = [region['RegionName'] for region in client.describe_regions()['Regions']]

print("%-20s%-20s%-20s%-20s%-20s%-20s%-20s"%('REGION','EC2_TYPE','#EC2','#RI','DIFF(ec2-ri)','COMMENT','RECO'))

for r in regions :
    ec2 = boto3.client('ec2', region_name = r)

    # RESERVED Instances
    reservations = ec2.describe_reserved_instances()

    ec2ri = {}
    for i in reservations['ReservedInstances'] :
        if i['State'] == 'active' :
            # pprint(i)
            this_it = i['InstanceType']
            ec2ri[this_it] = ec2ri.get(this_it, 0) +1
            # print("----------")

    # for k,v in ec2ri.items() :
    #     print("%-20s%-20s%-20s" %(r, k, v))


    # EC2 instances
    response = ec2.describe_instances()

    ec2InstanceTypes = {}
    for i in response['Reservations'] :
        this_it = i['Instances'][0]['InstanceType']
        ec2InstanceTypes[this_it] = ec2InstanceTypes.get(this_it, 0) +1
        
    # for k,v in ec2InstanceTypes.items() :
    #     print("%-20s%-20s%-20s" %(r, k, v))


    ##printing an matching
    # for k,v in ec2InstanceTypes.items() :
    #      print("%-20s%-20s%-20s" %(r, k, v))


# si RI mais pas Instance => alors RI pour rien
# si Instance mais pas RI => alors RI a faire

# si RI & Instance => 
#     si RI > Instance => RI pour rien
#     si RI < Instance => RI a faire
    for type in ec2ri :
        if type in ec2InstanceTypes :
            #print "EC2 & RI"
            if ec2InstanceTypes[type] > ec2ri[type] :
                print("%-20s%-20s%-20s%-20s%-20s%-20s%-20s"%(r, type, ec2InstanceTypes[type], ec2ri[type], ec2InstanceTypes[type]-ec2ri[type], 'nb_RI_missing', 'BOOK_THEM'))
            elif ec2InstanceTypes[type] < ec2ri[type] :
                print("%-20s%-20s%-20s%-20s%-20s%-20s%-20s"%(r, type,  ec2InstanceTypes[type], ec2ri[type], ec2InstanceTypes[type]-ec2ri[type], 'nb_RI_unused', 'Sell'))
            else :
                print("%-20s%-20s%-20s%-20s%-20s%-20s"%(r, type,  ec2InstanceTypes[type], ec2ri[type], 0,'OK_ec2=ri'))

    for type in ec2ri :
        if type not in ec2InstanceTypes :
            print("%-20s%-20s%-20s%-20s%-20s%-20s%-20s" %(r, type, 0, ec2ri[type], -ec2ri[type],'RI_but_No_EC2', 'Sell'))

    for type in ec2InstanceTypes :
        if type not in ec2ri :
            print("%-20s%-20s%-20s%-20s%-20s%-20s%-20s" %(r, type, ec2InstanceTypes[type], 0, ec2InstanceTypes[type], 'NO_RI_at_all', 'BOOK_THEM'))

