# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from unittest import mock

import pytest
from google.cloud import ndb

from securescaffold import factory
from securescaffold import emulator
from securescaffold import datastoreconfig


@pytest.fixture(scope="session")
def datastore():
    """Start and stop the datastore emulator."""
    with emulator.DatastoreEmulatorForTests():
        yield


@pytest.fixture(scope="function")
def ndb_client(datastore):
    client = ndb.Client()

    yield client

    # Now delete all entities.
    with client.context():
        for key in ndb.Query().iter(keys_only=True):
            key.delete_async()


def test_create_app_creates_secret_key(ndb_client):
    with mock.patch("secrets.token_urlsafe", return_value="topsecret"):
        app = factory.create_app("test")
        datastoreconfig.configure_secret_key(app)

    with ndb_client.context():
        obj = datastoreconfig.AppConfig.get_by_id(datastoreconfig.AppConfig.SINGLETON_ID)
        assert obj.secret_key == app.config["SECRET_KEY"]
        assert app.config["SECRET_KEY"] == "topsecret"


def test_create_app_uses_existing_secret_key(ndb_client):
    with ndb_client.context():
        id_ = datastoreconfig.AppConfig.SINGLETON_ID
        datastoreconfig.AppConfig(id=id_, secret_key="hunter2").put()

    app = factory.create_app("test")
    datastoreconfig.configure_secret_key(app)

    assert app.config["SECRET_KEY"] == "hunter2"
