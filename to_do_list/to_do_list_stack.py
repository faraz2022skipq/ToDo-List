from aws_cdk import (
    Stack,
    RemovalPolicy,
    aws_cognito as cognito
)
from constructs import Construct

class ToDoListStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        user_pool = cognito.UserPool(self, "todopool",
            user_pool_name = "todopool",
            removal_policy = RemovalPolicy.DESTROY,
            self_sign_up_enabled = True,
            sign_in_aliases = cognito.SignInAliases(username=True, email=True),
            auto_verify = cognito.AutoVerifiedAttrs(email=True, phone=True),
            password_policy = cognito.PasswordPolicy(min_length=6),
            account_recovery = cognito.AccountRecovery.EMAIL_ONLY
            )
        user_pool_client = cognito.UserPoolClient(self, "todopoolclient"
            user_pool = user_pool,
            )
