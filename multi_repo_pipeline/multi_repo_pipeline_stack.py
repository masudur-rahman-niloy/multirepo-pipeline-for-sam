from typing import List

from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_codecommit as codecommit,
    aws_codepipeline as codepipeline,
    aws_codepipeline_actions as codepipeline_actions,
    aws_iam as iam,
    aws_codebuild as codebuild,
    aws_lambda as lambda_,
    aws_events_targets as targets,
)
import aws_cdk as cdk
from constructs import Construct

from .policy_statements import iam_pass_policy, iam_codecommit_policy, iam_other_policy, iam_lambda_policy, \
    iam_cloudformation_policy
from .repositories import repositories
import os
import yaml


class MultiRepoPipelineStack(Stack):
    source_bucket_name = "my-source-code-bucket"
    pipeline_bucket_name = "my-codepipeline-bucket"
    stack_name = '#{CustomNameSpace.RepositoryName}-#{CustomNameSpace.BranchName}'
    template_configuration = 'template_conf_#{CustomNameSpace.BranchName}.json'
    change_set_name = 'changeset'
    key_name = 'source.zip'
    pipeline_name = 'my-pipeline'
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        source_bucket = s3.Bucket(
            self,
            "SourceBucket",
            bucket_name=self.source_bucket_name,
            versioned=True,
            auto_delete_objects=True,
            removal_policy=cdk.RemovalPolicy.DESTROY,
        )
        pipeline_bucket = s3.Bucket(
            self,
            "PipelineBucket",
            bucket_name=self.pipeline_bucket_name,
            auto_delete_objects=True,
            removal_policy=cdk.RemovalPolicy.DESTROY,
        )

        pipeline_role = iam.Role(
            self,
            "PipelineRole",
            assumed_by=iam.ServicePrincipal("codepipeline.amazonaws.com"),
        )

        codebuild_role = iam.Role(
            self,
            "CodeBuildRole",
            assumed_by=iam.ServicePrincipal("codebuild.amazonaws.com"),
        )

        lambda_role = iam.Role(
            self,
            "LambdaRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
        )
        cloudformation_role = iam.Role(
            self,
            "CloudFormationRole",
            assumed_by=iam.ArnPrincipal(pipeline_role.role_arn)
        )

        pipeline_role.add_to_policy(iam_pass_policy)
        pipeline_role.add_to_policy(iam_codecommit_policy)
        pipeline_role.add_to_policy(iam_other_policy)
        pipeline_role.grant_assume_role(cloudformation_role)

        codebuild_role.add_to_policy(iam_codecommit_policy)
        codebuild_role.add_to_policy(iam_other_policy)

        lambda_role.add_to_policy(iam_lambda_policy)
        lambda_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name(
            'service-role/AWSLambdaBasicExecutionRole'
        ))

        cloudformation_role.add_to_policy(iam_cloudformation_policy)


        codecommit_to_s3_codebuild_project = codebuild.Project(
            self,
            "CodeCommitToS3CodeBuildProject",
            role=codebuild_role,
            build_spec=codebuild.BuildSpec.from_object(read_codecommit_s3_buildspec()),
            environment=codebuild.BuildEnvironment(
                build_image=codebuild.LinuxBuildImage.AMAZON_LINUX_2_3
            )

        )

        start_codebuild_function = lambda_.Function(
            self,
            "StartCodebuildFunction",
            code=lambda_.Code.from_asset(os.path.join(__file__, "../../functions/")),
            handler="start_code_build.lambda_handler",
            environment={
                'PROJECT_NAME': codecommit_to_s3_codebuild_project.project_name,
                'ZIP_SOURCE_FILE_NAME':  self.key_name,
                'BUCKET': source_bucket.bucket_name,

            },
            role=lambda_role,
            runtime=lambda_.Runtime.PYTHON_3_8,
        )

        for repository in repositories:
            codecommit_repo = codecommit.Repository(
                self,
                repository.name,
                repository_name=repository.name,
                description=repository.description
            )
            codecommit_repo.on_commit(
                'CommitToBranch',
                target=targets.LambdaFunction(
                    handler=start_codebuild_function,
                ),
                # branches=['qa', 'stage', 'master']  # we can specify branches if needed

            )

            cdk.CfnOutput(
                self,
                f'Repo-{repository.name}',
                value=codecommit_repo.repository_clone_url_http
            )

        pipeline = codepipeline.Pipeline(
            self,
            "Pipeline",
            pipeline_name=self.pipeline_name,
            artifact_bucket=pipeline_bucket,
            role=pipeline_role,
        )

        source_artifact = codepipeline.Artifact('SourceArtifact')
        source_action = codepipeline_actions.S3SourceAction(
            action_name="S3Source",
            bucket=source_bucket,
            bucket_key=self.key_name,
            output=source_artifact,
            trigger=codepipeline_actions.S3Trigger.EVENTS,
            variables_namespace='SourceVariables',
        )

        source_stage = pipeline.add_stage(
            stage_name='Source',
            actions=[
                source_action
            ]
        )

        build_artifact = codepipeline.Artifact('BuildArtifact')
        codebuild_project = codebuild.PipelineProject(
            self,
            "CodeBuildProject",
            role=codebuild_role,
            build_spec=codebuild.BuildSpec.from_source_filename('buildspec.yaml'),
            environment=codebuild.BuildEnvironment(
                build_image=codebuild.LinuxBuildImage.AMAZON_LINUX_2_3
            )
        )

        build_action = codepipeline_actions.CodeBuildAction(
            action_name="Build",
            role=pipeline_role,
            input=source_artifact,
            project=codebuild_project,
            variables_namespace='BuildVariables',
            outputs=[build_artifact],
            environment_variables={
                'BUILD_OUTPUT_BUCKET': codebuild.BuildEnvironmentVariable(value=pipeline_bucket.bucket_name)
            }
        )
        pipeline.add_stage(
            stage_name='Build',
            actions=[
                build_action
            ]
        )

        transform_lambda_function = lambda_.Function(
            self,
            "TransformLambdaFunction",
            code=lambda_.Code.from_asset(os.path.join(__file__, "../../functions/")),
            handler="transform_parameters.lambda_handler",
            role=lambda_role,
            runtime=lambda_.Runtime.PYTHON_3_8,
        )

        pipeline_transform_function = codepipeline_actions.LambdaInvokeAction(
            action_name="Transform",
            lambda_=transform_lambda_function,
            variables_namespace='CustomNameSpace',
            run_order=1,
            inputs=[
                source_artifact
            ]
        )

        create_changeset = codepipeline_actions.CloudFormationCreateReplaceChangeSetAction(
            action_name="CreateChanges",
            stack_name=self.stack_name,
            change_set_name=self.change_set_name,
            admin_permissions=True,
            template_path=build_artifact.at_path("package.yaml"),
            run_order=2,
            role=cloudformation_role,
            template_configuration=build_artifact.at_path(self.template_configuration),
        )

        execute_changeset = codepipeline_actions.CloudFormationExecuteChangeSetAction(
            action_name="ExecuteChanges",
            stack_name=self.stack_name,
            change_set_name=self.change_set_name,
            run_order=3,
            role=cloudformation_role
        )

        pipeline.add_stage(
            stage_name='Deploy',
            actions=[
                pipeline_transform_function,
                create_changeset,
                execute_changeset

            ]
        )


def read_codecommit_s3_buildspec():
    filename = 'codecommit-s3-buildspec.yaml'
    with open(filename) as f:
        return yaml.load(f.read(), Loader=yaml.FullLoader)
