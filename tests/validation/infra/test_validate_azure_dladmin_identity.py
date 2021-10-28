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
# Source File Name:  test_validate_azure_dladmin_identity.py
###
"""Azure Validate Datalake Admin Identity Actions Tests."""
import dataclasses
from typing import Dict, List
from unittest.mock import Mock

from azure.mgmt.authorization import AuthorizationManagementClient
from azure.mgmt.resource import ResourceManagementClient

from cdpctl.validation.infra.validate_azure_dladmin_identity import (
    _azure_dladmin_data_storage_actions_check,
    _azure_dladmin_data_storage_data_actions_check,
    _azure_dladmin_logs_storage_actions_check,
    _azure_dladmin_logs_storage_data_actions_check,
)
from tests.validation import expect_validation_failure, expect_validation_success


def get_config(role_name):
    return {
        "infra": {
            "azure": {"subscription_id": "test_id", "metagroup": {"name": "rg_name"}}
        },
        "env": {
            "azure": {
                "role": {"name": {"datalake_admin": f"{role_name}"}},
                "storage": {
                    "name": "storage_name",
                    "path": {
                        "logs": "abfs://logs@storage_name.dfs.core.windows.net",
                        "data": "abfs://data@storage_name.dfs.core.windows.net",
                    },
                },
            }
        },
    }


def setup_mocks(
    resource_client: ResourceManagementClient,
    auth_client: AuthorizationManagementClient,
    identity_name: str,
    scope: str,
    actions,
    not_actions,
    data_actions,
    not_data_actions,
):
    ResourceGetbyidResponse = dataclasses.make_dataclass(
        "ResourceGetbyidResponse", [("properties", Dict)]
    )
    resource_client.resources.get_by_id.return_value = ResourceGetbyidResponse(
        {"principalId": identity_name}
    )

    RoleAssignment = dataclasses.make_dataclass(
        "RoleAssignment", [("role_definition_id", str), ("scope", str)]
    )
    auth_client.role_assignments.list.return_value = [
        RoleAssignment(identity_name, scope)
    ]

    Permission = dataclasses.make_dataclass(
        "Permission",
        [
            "actions",
            "not_actions",
            "data_actions",
            "not_data_actions",
        ],
    )

    RoleDefinition = dataclasses.make_dataclass(
        "RoleDefinition", ["role_name", "permissions"]
    )

    auth_client.role_definitions.get_by_id.return_value = RoleDefinition(
        "test",
        [
            Permission(
                actions=actions,
                not_actions=not_actions,
                data_actions=data_actions,
                not_data_actions=not_data_actions,
            )
        ],
    )


def test_azure_dladmin_logs_actions_check_success(
    azure_data_required_actions: List[str],
) -> None:
    identity_name = "dladmin"
    scope = "/subscriptions/test_id/resourceGroups/rg_name/providers/Microsoft.Storage/storageAccounts/storage_name/blobServices/default/containers/logs"

    resource_client = Mock(spec=ResourceManagementClient)
    auth_client = Mock(spec=AuthorizationManagementClient)

    setup_mocks(
        resource_client=resource_client,
        auth_client=auth_client,
        identity_name=identity_name,
        scope=scope,
        actions=azure_data_required_actions,
        not_actions=[],
        data_actions=[],
        not_data_actions=[],
    )

    func = expect_validation_success(_azure_dladmin_logs_storage_actions_check)
    func(
        get_config("success"),
        auth_client,
        resource_client,
        azure_data_required_actions,
    )


def test_azure_dladmin_logs_actions_check_fail(
    azure_data_required_actions: List[str],
) -> None:
    identity_name = "dladmin"
    scope = "/subscriptions/test_id/resourceGroups/rg_name/providers/Microsoft.Storage/storageAccounts/storage_name/blobServices/default/containers/logs"

    resource_client = Mock(spec=ResourceManagementClient)
    auth_client = Mock(spec=AuthorizationManagementClient)

    setup_mocks(
        resource_client=resource_client,
        auth_client=auth_client,
        identity_name=identity_name,
        scope=scope,
        actions=[],
        not_actions=[],
        data_actions=[],
        not_data_actions=[],
    )

    func = expect_validation_failure(_azure_dladmin_logs_storage_actions_check)
    func(
        get_config("fail"),
        auth_client,
        resource_client,
        azure_data_required_actions,
    )


def test_azure_dladmin_logs_data_actions_check_success(
    azure_data_required_data_actions: List[str],
) -> None:
    identity_name = "dladmin"
    scope = "/subscriptions/test_id/resourceGroups/rg_name/providers/Microsoft.Storage/storageAccounts/storage_name/blobServices/default/containers/logs"

    resource_client = Mock(spec=ResourceManagementClient)
    auth_client = Mock(spec=AuthorizationManagementClient)

    setup_mocks(
        resource_client=resource_client,
        auth_client=auth_client,
        identity_name=identity_name,
        scope=scope,
        actions=[],
        not_actions=[],
        data_actions=azure_data_required_data_actions,
        not_data_actions=[],
    )

    func = expect_validation_success(_azure_dladmin_logs_storage_data_actions_check)
    func(
        get_config("success"),
        auth_client,
        resource_client,
        azure_data_required_data_actions,
    )


def test_azure_dladmin_logs_data_actions_check_fail(
    azure_data_required_data_actions: List[str],
) -> None:
    identity_name = "dladmin"
    scope = "/subscriptions/test_id/resourceGroups/rg_name/providers/Microsoft.Storage/storageAccounts/storage_name/blobServices/default/containers/logs"

    resource_client = Mock(spec=ResourceManagementClient)
    auth_client = Mock(spec=AuthorizationManagementClient)

    setup_mocks(
        resource_client=resource_client,
        auth_client=auth_client,
        identity_name=identity_name,
        scope=scope,
        actions=[],
        not_actions=[],
        data_actions=[],
        not_data_actions=[],
    )

    func = expect_validation_failure(_azure_dladmin_logs_storage_data_actions_check)
    func(
        get_config("fail"),
        auth_client,
        resource_client,
        azure_data_required_data_actions,
    )


def test_azure_dladmin_data_storage_actions_check_success(
    azure_data_required_actions: List[str],
) -> None:
    identity_name = "dladmin"
    scope = "/subscriptions/test_id/resourceGroups/rg_name/providers/Microsoft.Storage/storageAccounts/storage_name/blobServices/default/containers/data"

    resource_client = Mock(spec=ResourceManagementClient)
    auth_client = Mock(spec=AuthorizationManagementClient)
    setup_mocks(
        resource_client=resource_client,
        auth_client=auth_client,
        identity_name=identity_name,
        scope=scope,
        actions=azure_data_required_actions,
        not_actions=[],
        data_actions=[],
        not_data_actions=[],
    )

    func = expect_validation_success(_azure_dladmin_data_storage_actions_check)
    func(
        get_config("success"),
        auth_client,
        resource_client,
        azure_data_required_actions,
    )


def test_azure_dladmin_data_storage_actions_check_fail(
    azure_data_required_actions: List[str],
) -> None:
    identity_name = "dladmin"
    scope = "/subscriptions/test_id/resourceGroups/rg_name/providers/Microsoft.Storage/storageAccounts/storage_name/blobServices/default/containers/data"

    resource_client = Mock(spec=ResourceManagementClient)
    auth_client = Mock(spec=AuthorizationManagementClient)

    setup_mocks(
        resource_client=resource_client,
        auth_client=auth_client,
        identity_name=identity_name,
        scope=scope,
        actions=[],
        not_actions=[],
        data_actions=[],
        not_data_actions=[],
    )

    func = expect_validation_failure(_azure_dladmin_data_storage_actions_check)
    func(
        get_config("fail"),
        auth_client,
        resource_client,
        azure_data_required_actions,
    )


def test_azure_dladmin_data_storage_data_actions_check_success(
    azure_data_required_data_actions: List[str],
) -> None:
    identity_name = "dladmin"
    scope = "/subscriptions/test_id/resourceGroups/rg_name/providers/Microsoft.Storage/storageAccounts/storage_name/blobServices/default/containers/data"

    resource_client = Mock(spec=ResourceManagementClient)
    auth_client = Mock(spec=AuthorizationManagementClient)
    setup_mocks(
        resource_client=resource_client,
        auth_client=auth_client,
        identity_name=identity_name,
        scope=scope,
        actions=[],
        not_actions=[],
        data_actions=azure_data_required_data_actions,
        not_data_actions=[],
    )

    func = expect_validation_success(_azure_dladmin_data_storage_data_actions_check)
    func(
        get_config("success"),
        auth_client,
        resource_client,
        azure_data_required_data_actions,
    )


def test_azure_dladmin_data_storage_data_actions_check_fail(
    azure_data_required_data_actions: List[str],
) -> None:
    identity_name = "dladmin"
    scope = "/subscriptions/test_id/resourceGroups/rg_name/providers/Microsoft.Storage/storageAccounts/storage_name/blobServices/default/containers/data"

    resource_client = Mock(spec=ResourceManagementClient)
    auth_client = Mock(spec=AuthorizationManagementClient)

    setup_mocks(
        resource_client=resource_client,
        auth_client=auth_client,
        identity_name=identity_name,
        scope=scope,
        actions=[],
        not_actions=[],
        data_actions=[],
        not_data_actions=[],
    )

    func = expect_validation_failure(_azure_dladmin_data_storage_data_actions_check)
    func(
        get_config("fail"),
        auth_client,
        resource_client,
        azure_data_required_data_actions,
    )
