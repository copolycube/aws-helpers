#!/bin/sh
EC2ID="$1"
aws ec2 describe-instances --filters "Name=instance-state-name,Values=running" "Name=instance-id,Values=$EC2ID" --query 'Reservations[*].Instances[*].[PrivateIpAddress]' --output text

# to use with the .bashrc function :
# sshi () { ssh $(~/repos/aws-helpers/ec2id_to_privateIp.sh $1) ; }
# so that sshi <ec2id> logs you directly...
