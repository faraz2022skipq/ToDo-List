import aws_cdk as core
import aws_cdk.assertions as assertions

from to_do_list.to_do_list_stack import ToDoListStack

# example tests. To run these tests, uncomment this file along with the example
# resource in to_do_list/to_do_list_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = ToDoListStack(app, "to-do-list")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
