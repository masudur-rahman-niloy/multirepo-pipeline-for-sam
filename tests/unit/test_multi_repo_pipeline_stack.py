import aws_cdk as core
import aws_cdk.assertions as assertions

from multi_repo_pipeline.multi_repo_pipeline_stack import MultiRepoPipelineStack

# example tests. To run these tests, uncomment this file along with the example
# resource in multi_repo_pipeline/multi_repo_pipeline_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = MultiRepoPipelineStack(app, "multi-repo-pipeline")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
