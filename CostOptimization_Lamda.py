import boto3
import json

def lambda_handler(event, context):
    # TODO implement
    ec2 = boto3.client('ec2')
    EC2instances = set()

    responseSnapshot = ec2.describe_snapshots(
    OwnerIds=['self']
    )

    for j in range(0, len(responseSnapshot['Snapshots'])):
        SnapshotID = responseSnapshot['Snapshots'][j]['SnapshotId']
        VolumeId = responseSnapshot['Snapshots'][j]['VolumeId']
        if not VolumeId:
            ec2.delete_snapshot(SnapshotId=SnapshotID)
            print("Deleted EBS snapshot ",SnapshotID," as it was not attached to any volume.")
        else:
            try:
                #when multiple volumes are attached to signle ec2 isntance but later on the volume got detached
                responseVolume = ec2.describe_volumes(VolumeIds=[VolumeId])
                if not responseVolume['Volumes'][0]['Attachments'][0]['InstanceId']:
                    ec2.delete_snapshot(SnapshotId=SnapshotID)
                    print("Deleted EBS snapshot ",SnapshotID," as it's volume was not attached to any instance.")
            except ec2.exceptions.ClientError as e:
                #when single volume was attached to ec2 instance and now the volume is not present
                if e.response['Error']['Code'] == 'InvalidVolume.NotFound':
                    ec2.delete_snapshot(SnapshotId=SnapshotID)
                    print("Deleted EBS snapshot ",SnapshotID," as its associated volume was not found.")        
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
