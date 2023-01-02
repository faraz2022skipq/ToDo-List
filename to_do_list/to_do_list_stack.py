from aws_cdk import (
    Stack,
    Duration,
    RemovalPolicy,
    core as cdk,
    aws_iam as iam_,
    aws_lambda as lambda_,
    aws_cognito as cognito,
    aws_apigateway as gateway,
)
from constructs import Construct

class ToDoListStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Creating user pool
        # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_cognito/UserPool.html
        user_pool = cognito.UserPool(self, "todopool",
            user_pool_name = "todopool",
            self_sign_up_enabled = True,
            sign_in_aliases = cognito.SignInAliases(email=True),
            auto_verify = cognito.AutoVerifiedAttrs(email=True, phone=True),
            password_policy = cognito.PasswordPolicy(min_length=6),
            account_recovery = cognito.AccountRecovery.EMAIL_ONLY
            )
        user_pool.apply_removal_policy(RemovalPolicy.DESTROY)
        
        # App Client for userpools
        # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_cognito/UserPoolClient.html
        user_pool_client = cognito.UserPoolClient(self, "todopoolclient",
            user_pool = user_pool,
            auth_flows = {
                'admin_user_password': True,
                'user_password': True,
                'custom': True,
                'user_srp': True},
            # Authentication flows allow users on a client to be authenticated with a user pool.
            o_auth = cognito.OAuthSettings(flows = cognito.OAuthFlows(implicit_code_grant=True, 
                        authorization_code_grant=False),
                callback_urls = ["http://localhost:8000/logged_in.html"],
                logout_urls = ["http://localhost:8000/index.html"]),
            supported_identity_providers = [cognito.UserPoolClientIdentityProvider.COGNITO],
            user_pool_client_name = "todopoolclient"
            )
        user_pool_client.apply_removal_policy(RemovalPolicy.DESTROY)

        # Adding prefix for Cognito domain
        # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_cognito/CognitoDomainOptions.html
        user_pool.add_domain("CognitoDomain",
            cognito_domain = cognito.CognitoDomainOptions(
                domain_prefix = "hisenberg"
            )
        )
        """
                From here on API integration & Lambda is coded
        """
        # Cognito user pools based custom authorizer
        # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_apigateway/CognitoUserPoolsAuthorizer.html
        auth = gateway.CognitoUserPoolsAuthorizer(self, 'CognitoAuthorizer', cognito_user_pools=[user_pool])

        # Calling role funtion that will give Lambda "full cloudwatch access"
        lambda_role = self.apiLambdaRole()
        # Creating my API Lambda
        API_lambda = self.create_lambda("apiLambda", "./resources", "apiLambda.lambda_handler", lambda_role)
        # Applying removal policy to destroy instance
        API_lambda.apply_removal_policy(RemovalPolicy.DESTROY)

        #REST API
        api = gateway.LambdaRestApi(self, "todoAPI",
            handler = API_lambda,
            proxy = False
            )
        
        list = api.root.add_resource("list")
        list.add_method("GET", authorization_type = gateway.AuthorizationType.COGNITO,
            authorizer = auth)
        list.add_method("POST", authorization_type = gateway.AuthorizationType.COGNITO,
            authorizer = auth)
        list.add_method("PUT", authorization_type = gateway.AuthorizationType.COGNITO,
            authorizer = auth)
        list.add_method("DELETE", authorization_type = gateway.AuthorizationType.COGNITO,
            authorizer = auth)

        cdk.CfnOutput(self, 'UserPoolId', value=user_pool.user_pool_id)
        cdk.CfnOutput(self, 'UserPoolClientId', value=user_pool_client.user_pool_client_id)

    # Defining role for my lambda function
    # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_iam/Role.html
    def apiLambdaRole(self):
        '''
            This will give out Lambda full access to publish on cloudwatch
        '''
        apiLambda_role = iam_.Role(self, "apiLambda Role",
            assumed_by = iam_.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies = [
                    iam_.ManagedPolicy.from_aws_managed_policy_name("AmazonAPIGatewayInvokeFullAccess"),
                    iam_.ManagedPolicy.from_aws_managed_policy_name("CloudWatchFullAccess")
            ])
        return apiLambda_role

    # Defining my create_lembda function
    # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_lambda/README.html
    def create_lambda(self, id_, path, handler, role):
        '''
            This will take my desired action of Lambda function performing code 
            and will deploy it on cloud
        '''
        return lambda_.Function(self,
            id = id_,
            code = lambda_.Code.from_asset(path),
            handler = handler,
            runtime = lambda_.Runtime.PYTHON_3_8,
            role = role,
            timeout = Duration.seconds(15)
        )
