ec2_params = {
    "DryRun": False,
    "LaunchSpecification": {
        "SecurityGroupIds": ["sg-023dd53350eb900fd"],
        "BlockDeviceMappings": [
            {
                "DeviceName": "/dev/sda1",
                "VirtualName": "ephemeral0",
                "Ebs": {
                    "DeleteOnTermination": True,
                    "VolumeSize": 8,
                    "VolumeType": "gp2",
                },
            }
        ],
        "ImageId": "ami-0e98568d8039d8fab",
        "InstanceType": "m5.large",
        # 'InstanceType': 't3a.nano', # testing instance size
        "KeyName": "mc-keypair-1",
        "Placement": {"AvailabilityZone": "us-east-1b"},
    },
    "SpotPrice": ".05",
    "Device": "/dev/sdf",
    "VolumeId": "vol-0c38f2407ef229915",
    "TagValue": "mc",
    "AvailabilityZone": "us-east-1",
}


discord_params = {"ChannelId": 715402186615422976}
