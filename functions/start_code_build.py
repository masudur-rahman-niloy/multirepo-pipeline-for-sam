import boto3
import os

codebuild_client = boto3.client('codebuild')


def lambda_handler(event, context):
    project_name = os.environ.get('PROJECT_NAME')
    zip_source_file_name = os.environ.get('ZIP_SOURCE_FILE_NAME')
    bucket = os.environ.get('BUCKET')
    response = codebuild_client.start_build(
        projectName=project_name,
        environmentVariablesOverride=[
            {"name": "REFERENCE_NAME", "value": event['detail']['referenceName']},
            {"name": "REFERENCE_TYPE", "value": event['detail']['referenceType']},
            {"name": "REPOSITORY_NAME", "value": event['detail']['repositoryName']},
            {"name": "REPO_REGION", "value": event['region']},
            {"name": "ACCOUNT_ID", "value": event['account']},
            {"name": "ZIP_SOURCE_FILE_NAME", "value": zip_source_file_name},
            {"name": "BUCKET", "value": bucket},
        ]
    )
