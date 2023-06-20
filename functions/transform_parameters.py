import boto3

client = boto3.client('codepipeline')
s3 = boto3.client('s3')


def lambda_handler(event, context):
    try:
        s3Location = event['CodePipeline.job']['data']['inputArtifacts'][0]['location']['s3Location']
        bucket = s3Location['bucketName']
        key = s3Location['objectKey']
        response = s3.get_object_tagging(
            Bucket=bucket,
            Key=key
        )
        item_obj = {}
        for tag in response['TagSet']:
            item_obj[tag['Key']] = tag['Value']

        response = client.put_job_success_result(
            jobId=event['CodePipeline.job']['id'],
            outputVariables={
                "RepositoryName": item_obj.get('repository', 'test'),
                "BranchName": item_obj.get('branch', 'dev')
            }
        )
    except Exception as e:
        response = client.put_job_failure_result(
            jobId=event['CodePipeline.job']['id']
        )
