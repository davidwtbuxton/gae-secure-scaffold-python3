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

import logging
import secrets

try:
    from google.cloud import ndb
except ImportError:
    logging.info("Add google-cloud-ndb to your project's requirements.txt")
    raise


class AppConfig(ndb.Model):
    """Datastore model for storing app-wide configuration.

    This is used by `create_app` to save a random value for SECRET_KEY that
    persists across application startup, rather than defining SECRET_KEY in
    your source code.
    """

    SINGLETON_ID = "config"

    secret_key = ndb.StringProperty()

    @classmethod
    def singleton(cls) -> "AppConfig":
        """Create a datastore entity to store app-wide configuration."""
        config = cls.initial_config()
        obj = cls.get_or_insert(cls.SINGLETON_ID, **config)

        return obj

    @classmethod
    def initial_config(cls) -> dict:
        """Initial values for app configuration."""
        config = {
            "secret_key": secrets.token_urlsafe(16),
        }

        return config


def get_config_from_datastore() -> AppConfig:
    # This happens at application startup, so we use a new NDB context.
    client = ndb.Client()

    with client.context():
        obj = AppConfig.singleton()

    return obj


def configure_secret_key(app) -> AppConfig:
    """Set the Flask SECRET_KEY from the datastore."""
    config = get_config_from_datastore()
    app.config["SECRET_KEY"] = config.secret_key

    return config
