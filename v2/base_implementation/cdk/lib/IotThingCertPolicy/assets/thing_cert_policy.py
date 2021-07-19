# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import os
import sys
import json
import logging as logger
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes

import time

logger.getLogger().setLevel(logger.INFO)

temp_event = {
    "RequestType": "Create",
    "ServiceToken": "arn:aws:lambda:us-west-2:904880203774:function:test1-IotThingCertPolicyFunctionframeworkonEvent86-sPwcDc5WWA1e",
    "ResponseURL": "https://cloudformation-custom-resource-response-uswest2.s3-us-west-2.amazonaws.com/arn%3Aaws%3Acloudformation%3Aus-west-2%3A904880203774%3Astack/test1/d92d29d0-e89c-11eb-bd43-0a0fbc569219%7CGreengrassCoreIotThingCertPolicyFunctionA5730834%7C3ec9952f-3339-49ac-a7f1-44af6561f751?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20210719T142454Z&X-Amz-SignedHeaders=host&X-Amz-Expires=7200&X-Amz-Credential=AKIA54RCMT6SKBOPMYGJ%2F20210719%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Signature=6ca872aaf6e32362a505f3a033dea0121c99ea1bf2a218768854224ed1e1c1fa",
    "StackId": "arn:aws:cloudformation:us-west-2:904880203774:stack/test1/d92d29d0-e89c-11eb-bd43-0a0fbc569219",
    "RequestId": "3ec9952f-3339-49ac-a7f1-44af6561f751",
    "LogicalResourceId": "GreengrassCoreIotThingCertPolicyFunctionA5730834",
    "ResourceType": "AWS::CloudFormation::CustomResource",
    "ResourceProperties": {
        "ServiceToken": "arn:aws:lambda:us-west-2:904880203774:function:test1-IotThingCertPolicyFunctionframeworkonEvent86-sPwcDc5WWA1e",
        "ThingName": "test1-greengrass-core-wP7iXabb",
        "IotPolicy": '"{\\n  Version: \\"2012-10-17\\",\\n  Statement: [\\n    {\\n      Effect: \\"Allow\\",\\n      Action: [\\"iot:Connect\\"],\\n      Resource: \\"arn:aws:iot:us-west-2:904880203774:client/greengrass-core*\\"\\n    },\\n    {\\n      Effect: \\"Allow\\",\\n      Action: [\\"iot:Receive\\", \\"iot:Publish\\"],\\n      Resource: [\\n        \\"arn:aws:iot:us-west-2:904880203774:topic/$aws/things/greengrass-core*/greengrass/health/json\\",\\n        \\"arn:aws:iot:us-west-2:904880203774:topic/$aws/things/greengrass-core*/greengrassv2/health/json\\",\\n        \\"arn:aws:iot:us-west-2:904880203774:topic/$aws/things/greengrass-core*/jobs/*\\",\\n        \\"arn:aws:iot:us-west-2:904880203774:topic/$aws/things/greengrass-core*/shadow/*\\"\\n      ]\\n    },\\n    {\\n      Effect: \\"Allow\\",\\n      Action: [\\"iot:Subscribe\\"],\\n      Resource: [\\n        \\"arn:aws:iot:us-west-2:904880203774:topicfilter/$aws/things/greengrass-core*/jobs/*\\",\\n        \\"arn:aws:iot:us-west-2:904880203774:topicfilter/$aws/things/greengrass-core*/shadow/*\\"\\n      ]\\n    },\\n    {\\n      Effect: \\"Allow\\",\\n      Action: [\\"iot:GetThingShadow\\", \\"iot:UpdateThingShadow\\", \\"iot:DeleteThingShadow\\"],\\n      Resource: [\\"arn:aws:iot:us-west-2:904880203774:thing/greengrass-core*\\"]\\n    },\\n    {\\n      Effect: \\"Allow\\",\\n      Action: \\"iot:AssumeRoleWithCertificate\\",\\n      Resource: \\"arn:aws:iot:us-west-2:904880203774:rolealias/test1-GreengrassV2TokenExchangeRole-37cW5k8U\\"\\n    },\\n    {\\n      Effect: \\"Allow\\",\\n      Action: [\\"greengrass:GetComponentVersionArtifact\\", \\"greengrass:ResolveComponentCandidates\\", \\"greengrass:GetDeploymentConfiguration\\"],\\n      Resource: \\"*\\"\\n    }\\n  ]\\n}"',
        "StackName": "test1",
    },
}

temp_environment = {
    "AWS_LAMBDA_FUNCTION_VERSION": "$LATEST",
    "LAMBDA_TASK_ROOT": "/var/task",
    "AWS_LAMBDA_LOG_GROUP_NAME": "/aws/lambda/test1-CreateIoTRoleAliasProviderA5DE3E61-rLnc8JosvWjj",
    "LD_LIBRARY_PATH": "/var/lang/lib:/lib64:/usr/lib64:/var/runtime:/var/runtime/lib:/var/task:/var/task/lib:/opt/lib",
    "AWS_LAMBDA_LOG_STREAM_NAME": "2021/07/16/[$LATEST]08359e000221485b8a001f401ee9f9b3",
    "AWS_LAMBDA_RUNTIME_API": "127.0.0.1:9001",
    "AWS_EXECUTION_ENV": "AWS_Lambda_python3.8",
    "AWS_LAMBDA_FUNCTION_NAME": "test1-CreateIoTRoleAliasProviderA5DE3E61-rLnc8JosvWjj",
    "AWS_XRAY_DAEMON_ADDRESS": "169.254.79.2:2000",
    "PATH": "/var/lang/bin:/usr/local/bin:/usr/bin/:/bin:/opt/bin",
    "AWS_DEFAULT_REGION": "us-west-2",
    "PWD": "/var/task",
    "LAMBDA_RUNTIME_DIR": "/var/runtime",
    "LANG": "en_US.UTF-8",
    "AWS_LAMBDA_INITIALIZATION_TYPE": "on-demand",
    "TZ": ":UTC",
    "AWS_REGION": "us-west-2",
    "SHLVL": "0",
    "_AWS_XRAY_DAEMON_ADDRESS": "169.254.79.2",
    "_AWS_XRAY_DAEMON_PORT": "2000",
    "AWS_XRAY_CONTEXT_MISSING": "LOG_ERROR",
    "_HANDLER": "role_alias.handler",
    "AWS_LAMBDA_FUNCTION_MEMORY_SIZE": "128",
    "PYTHONPATH": "/var/runtime",
    "_X_AMZN_TRACE_ID": "Root=1-60f1f774-66292ad5566a122178506fac;Parent=229af0ed792cd611;Sampled=0",
}


def get_aws_client(name):
    return boto3.client(
        name,
        config=Config(retries={"max_attempts": 10, "mode": "standard"}),
    )


def create_resources(thing_name: str, iot_policy: str):
    """Create AWS IoT thing, certificate and attach certificate with policy and thing.
        Returns the Arns for the values and a Parameter Store Arn for the private key

    :param thing_name: thingName to create, defaults to None
    :type thing_name: str, required
    :param iot_policy: AWS IoT policy to be created and stringified JSON
    :type iot_policy: str
    """
    c_iot = get_aws_client("iot")

    response = {}

    # thing
    try:
        result = c_iot.create_thing(thingName=thing_name)
    except ClientError as e:
        logger.error(f"Error creating thing {thing_name}, {e}")
        sys.exit(1)
    response["ThingArn"] = result["thingArn"]
    response["ThingName"] = result["thingName"]

    # cert
    # Create certificate and private key
    key = ec.generate_private_key(curve=ec.SECP256R1(), backend=default_backend())
    private_key = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode("utf-8")

    # Generate a CSR and set subject (CN=dispenserId)
    csr = (
        x509.CertificateSigningRequestBuilder()
        .subject_name(
            x509.Name(
                [
                    # Provide various details about who we are.
                    x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
                    x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "CO"),
                    x509.NameAttribute(NameOID.LOCALITY_NAME, "Denver"),
                    x509.NameAttribute(
                        NameOID.ORGANIZATION_NAME, "Greengrass Accelerator Testing"
                    ),
                    x509.NameAttribute(NameOID.COMMON_NAME, thing_name),
                ]
            )
        )
        .sign(key, hashes.SHA256(), default_backend())
    )
    try:
        result = c_iot.create_certificate_from_csr(
            certificateSigningRequest=str(
                csr.public_bytes(serialization.Encoding.PEM), "utf-8"
            ),
            setAsActive=True,
        )
    except ClientError as e:
        logger.error(f"Error creating certificate, {e}")
        sys.exit(1)
    response["CertificateArn"] = result["certificateArn"]
    # policy
    # attach cert-pol
    # attach cert-thing
    # store pk in SSM param store

    # return stuff

    return response


def delete_resources(thing_name, certificate_arn):
    """Delete thing, certificate, and policy in reverse order. Check for modifications
    since create (policy versions, etc)"""

    c_iot = get_aws_client("iot")

    # delete ssm param store
    # detach cert-thing
    # detach cert-pol
    # delete policy versions
    # delete policy

    # delete cert
    # detach all policies and things from cert
    try:
        response = c_iot.list_principal_things(principal=certificate_arn)
        for thing in response["things"]:
            c_iot.detach_thing_principal(thingName=thing, principal=certificate_arn)
        response = c_iot.list_attached_policies(target=certificate_arn)
        for policy in response["policies"]:
            c_iot.detach_policy(policyName=policy, target=certificate_arn)
    except ClientError as e:
        logger.error(
            f"Unable to list or detach things or policies from certificate {certificate_arn}, {e}"
        )
    try:
        c_iot.update_certificate(
            certificateId=certificate_arn.split("/")[-1], newStatus="REVOKED"
        )
        c_iot.delete_certificate(certificateId=certificate_arn.split("/")[-1])
    except ClientError as e:
        logger.error(f"Unable to delete certificate {certificate_arn}, {e}")

    # delete thing
    # Check and detach principals attached to thing
    try:
        response = c_iot.list_thing_principals(thingName=thing_name)
        for principal in response["principals"]:
            c_iot.detach_thing_principal(thingName=thing_name, principal=principal)
    except ClientError as e:
        logger.error(f"Unable to list or detach principals from {thing_name}, {e}")
    try:
        print(f"test delete {thing_name}")
        c_iot.delete_thing(thingName=thing_name)
    except ClientError as e:
        logger.error(f"Unable to delete thing {thing_name}, {e}")


def handler(event, context):
    logger.info("Received event: %s", json.dumps(event, indent=2))
    logger.info("Environment: %s", dict(os.environ))
    props = event["ResourceProperties"]
    physical_resource_id = ""
    try:
        # Check if this is a Create and we're failing Creates
        if event["RequestType"] == "Create" and event["ResourceProperties"].get(
            "FailCreate", False
        ):
            raise RuntimeError("Create failure requested, logging")
        elif event["RequestType"] == "Create":
            logger.info("Request CREATE")
            resp = create_resources(
                thing_name=props["ThingName"], iot_policy=props["IotPolicy"]
            )

            # set response data (PascalCase key)
            # TODO: ThingArn, CertificateArn, CertificatePem, PrivateKeySecretArn
            response_data = {
                "ThingArn": resp["ThingArn"],
                "CertificateArn": resp["CertificateArn"],
            }
            physical_resource_id = response_data["CertificateArn"]
        elif event["RequestType"] == "Update":
            logger.info("Request UPDATE")
            response_data = {}
        elif event["RequestType"] == "Delete":
            logger.info("Request DELETE")
            resp = delete_resources(
                thing_name=props["ThingName"],
                certificate_arn=event["PhysicalResourceId"],
            )
            response_data = {}
            physical_resource_id = event["PhysicalResourceId"]
        else:
            logger.info("Should not get here in normal cases - could be REPLACE")

        output = {"PhysicalResourceId": physical_resource_id, "Data": response_data}
        logger.info("Output from Lambda: %s", json.dumps(output, indent=2))
        return output
    except Exception as e:
        logger.exception(e)


if __name__ == "__main__":
    for env in temp_environment:
        os.environ[env] = temp_environment[env]

    # create
    print("running CREATE")
    response = handler(temp_event, {})
    time.sleep(2)
    temp_event["RequestType"] = "Delete"
    response = handler(temp_event, {})