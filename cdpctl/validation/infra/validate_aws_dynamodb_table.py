#!/usr/bin/env python3
###
# CLOUDERA CDP Control (cdpctl)
#
# (C) Cloudera, Inc. 2021-2021
# All rights reserved.
#
# Applicable Open Source License: GNU AFFERO GENERAL PUBLIC LICENSE
#
# NOTE: Cloudera open source products are modular software products
# made up of hundreds of individual components, each of which was
# individually copyrighted.  Each Cloudera open source product is a
# collective work under U.S. Copyright Law. Your license to use the
# collective work is as provided in your written agreement with
# Cloudera.  Used apart from the collective work, this file is
# licensed for your use pursuant to the open source license
# identified above.
#
# This code is provided to you pursuant a written agreement with
# (i) Cloudera, Inc. or (ii) a third-party authorized to distribute
# this code. If you do not have a written agreement with Cloudera nor
# with an authorized and properly licensed third party, you do not
# have any rights to access nor to use this code.
#
# Absent a written agreement with Cloudera, Inc. (“Cloudera”) to the
# contrary, A) CLOUDERA PROVIDES THIS CODE TO YOU WITHOUT WARRANTIES OF ANY
# KIND; (B) CLOUDERA DISCLAIMS ANY AND ALL EXPRESS AND IMPLIED
# WARRANTIES WITH RESPECT TO THIS CODE, INCLUDING BUT NOT LIMITED TO
# IMPLIED WARRANTIES OF TITLE, NON-INFRINGEMENT, MERCHANTABILITY AND
# FITNESS FOR A PARTICULAR PURPOSE; (C) CLOUDERA IS NOT LIABLE TO YOU,
# AND WILL NOT DEFEND, INDEMNIFY, NOR HOLD YOU HARMLESS FOR ANY CLAIMS
# ARISING FROM OR RELATED TO THE CODE; AND (D)WITH RESPECT TO YOUR EXERCISE
# OF ANY RIGHTS GRANTED TO YOU FOR THE CODE, CLOUDERA IS NOT LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, PUNITIVE OR
# CONSEQUENTIAL DAMAGES INCLUDING, BUT NOT LIMITED TO, DAMAGES
# RELATED TO LOST REVENUE, LOST PROFITS, LOSS OF INCOME, LOSS OF
# BUSINESS ADVANTAGE OR UNAVAILABILITY, OR LOSS OR CORRUPTION OF
# DATA.
#
# Source File Name:  validate_aws_dynamodb_table.py
###
"""Validation of the AWS DynamoDB locations."""
from typing import Any, Dict

import pytest
from boto3_type_annotations.dynamodb import Client as DynamoDBClient

from cdpctl.validation import get_config_value, validator
from cdpctl.validation.aws_utils import get_client


@pytest.fixture(autouse=True, name="dynamodb_client")
def dynamodb_client_fixture(config: Dict[str, Any]) -> DynamoDBClient:
    """Return an AWS dynamodb client."""
    return get_client("dynamodb", config)


@pytest.mark.aws
@pytest.mark.infra
def aws_dynamodb_table_exists_validation(
    config: Dict[str, Any], dynamodb_client: DynamoDBClient
) -> None:  # pragma: no cover
    """DynamoDB table exists."""  # noqa: D401, D403
    aws_dynamodb_table_exists(config, dynamodb_client)


@validator
def aws_dynamodb_table_exists(
    config: Dict[str, Any], dynamodb_client: DynamoDBClient
) -> None:
    """Check that DynamoDB table exists."""
    dynamodb_table: str = get_config_value(
        config,
        "infra:aws:dynamodb:table_name",
        key_missing_message="No table name was defined for config option: {0}",
        data_expected_error_message="No table name was provided for config option: {0}",
    )

    try:
        dynamodb_client.describe_table(TableName=dynamodb_table)
    except dynamodb_client.exceptions.ResourceNotFoundException as e:
        code = e.response["Error"]["Code"]
        if code == "ResourceNotFoundException":
            pytest.fail(f"DynamoDB table ({dynamodb_table}) does not exist.", False)
