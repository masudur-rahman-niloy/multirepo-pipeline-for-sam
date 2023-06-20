from aws_cdk  import aws_iam as iam

iam_pass_policy = iam.PolicyStatement(
                actions=[
                    "iam:PassRole"
                ],
                resources=["*"],
                effect=iam.Effect.ALLOW,
                conditions={
                    "StringEqualsIfExists": {
                        "iam:PassedToService": [
                            "cloudformation.amazonaws.com",
                            "elasticbeanstalk.amazonaws.com",
                            "ec2.amazonaws.com",
                            "ecs-tasks.amazonaws.com"
                        ]
                    }

                }
            )

iam_codecommit_policy = iam.PolicyStatement(
                actions=[
                    "codecommit:*",
                ],
                resources=["*"],
                effect=iam.Effect.ALLOW,
            )


iam_other_policy = iam.PolicyStatement(
                actions=[
                    "codebuild:BatchGetBuilds",
                    "codebuild:StartBuild",
                    "codebuild:BatchGetBuildBatches",
                    "codebuild:StartBuildBatch",
                    "codedeploy:CreateDeployment",
                    "codedeploy:GetApplication",
                    "codedeploy:GetApplicationRevision",
                    "codedeploy:GetDeployment",
                    "codedeploy:GetDeploymentConfig",
                    "codedeploy:RegisterApplicationRevision",
                    "codestar-connections:UseConnection",
                    "elasticbeanstalk:*",
                    "ec2:*",
                    "elasticloadbalancing:*",
                    "autoscaling:*",
                    "cloudwatch:*",
                    "s3:*",
                    "sns:*",
                    "cloudformation:*",
                    "rds:*",
                    "sqs:*",
                    "ecs:*",
                    "lambda:InvokeFunction",
                    "lambda:ListFunctions",
                    "opsworks:CreateDeployment",
                    "opsworks:DescribeApps",
                    "opsworks:DescribeCommands",
                    "opsworks:DescribeDeployments",
                    "opsworks:DescribeInstances",
                    "opsworks:DescribeStacks",
                    "opsworks:UpdateApp",
                    "opsworks:UpdateStack",
                    "devicefarm:ListProjects",
                    "devicefarm:ListDevicePools",
                    "devicefarm:GetRun",
                    "devicefarm:GetUpload",
                    "devicefarm:CreateUpload",
                    "devicefarm:ScheduleRun",
                    "servicecatalog:ListProvisioningArtifacts",
                    "servicecatalog:CreateProvisioningArtifact",
                    "servicecatalog:DescribeProvisioningArtifact",
                    "servicecatalog:DeleteProvisioningArtifact",
                    "servicecatalog:UpdateProduct",
                    "ecr:DescribeImages",
                    "states:DescribeExecution",
                    "states:DescribeStateMachine",
                    "states:StartExecution",
                    "appconfig:StartDeployment",
                    "appconfig:StopDeployment",
                    "appconfig:GetDeployment"
                ],
                resources=["*"],
                effect=iam.Effect.ALLOW,
            )
iam_lambda_policy = iam.PolicyStatement(
    actions=[
        's3:GetObjectTagging',
        'codepipeline:PutJobSuccessResult',
        'codepipeline:PutJobFailureResult',
        'codebuild:*',
    ],
    resources=['*'],
    effect=iam.Effect.ALLOW

)

iam_cloudformation_policy = iam.PolicyStatement(
    actions=[
        's3:*',
        'cloudformation:*',
    ],
    resources=['*'],
    effect=iam.Effect.ALLOW

)

