from aws_cdk import (
    Stack,
    RemovalPolicy,
    aws_cognito as cognito
)
from constructs import Construct

class ToDoListStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_cognito/UserPool.html
        # Creating user pool
        user_pool = cognito.UserPool(self, "todopool",
            user_pool_name = "todopool",
            self_sign_up_enabled = True,
            sign_in_aliases = cognito.SignInAliases(username=True, email=True),
            auto_verify = cognito.AutoVerifiedAttrs(email=True, phone=True),
            password_policy = cognito.PasswordPolicy(min_length=6),
            account_recovery = cognito.AccountRecovery.EMAIL_ONLY
            )
        user_pool.apply_removal_policy(RemovalPolicy.DESTROY)
        
        # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_cognito/UserPoolClient.html
        # App Client for userpools
        user_pool_client = cognito.UserPoolClient(self, "todopoolclient",
            user_pool = user_pool,
            auth_flows = {
                'admin_user_password': True,
                'user_password': True,
                'custom': True,
                'user_srp': True},
            # Authentication flows allow users on a client to be authenticated with a user pool.
            o_auth = cognito.OAuthSettings(flows = cognito.OAuthFlows(implicit_code_grant = True, 
                        authorization_code_grant = True),
                callback_urls = ["http://localhost:8000/logged_in.html"],
                logout_urls = ["http://localhost:8000/index.html"]),
            supported_identity_providers = [cognito.UserPoolClientIdentityProvider.COGNITO],
            user_pool_client_name = "todopoolclient"
            )
        user_pool_client.apply_removal_policy(RemovalPolicy.DESTROY)
