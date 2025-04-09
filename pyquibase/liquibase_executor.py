# Copyright 2017 Eun Woo Song

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import subprocess

from pkg_resources import resource_filename

LIQUIBASE_COMMAND = """java -cp %s liquibase.integration.commandline.Main \
    --driver=%s \
    --classpath=%s \
    --changeLogFile=%s \
    --url="%s" \
    --username=%s \
    --password=%s \
    --liquibaseSchemaName=db_logs \
    --logLevel=%s \
"""

SUPPORTED_DATABASES = {
    "postgresql": {
        "url": "jdbc:postgresql://%s:%s/%s",
        "driver": "org.postgresql.Driver",
        "db_connector": resource_filename(
            __package__, "db-connectors/postgresql-42.3.2.jar"
        ),
        "command": LIQUIBASE_COMMAND,
    }
}


class LiquibaseExecutor(object):
    def __init__(self, config):
        if config["database"] not in SUPPORTED_DATABASES:
            raise Exception("%s is not a supported database" % config["database"])

        self.config = config
        self.db = SUPPORTED_DATABASES[config["database"]]
        self.liquibaseJar = resource_filename(
            __package__, "liquibase/liquibase-core-4.25.0.jar"
        )
        self.logger = logging.getLogger(__name__)

    def execute(self, changeLogFilePath, *args):
        """
        Execute a liquibase command
        """
        config = self.config
        db = self.db

        if config["database"] == "postgresql":
            url = db["url"] % (config["host"], config["port"], config["db_name"])
            liquibase_command = db["command"] % (
                self.liquibaseJar,
                db["driver"],
                db["db_connector"],
                config["change_log_file"],
                url,
                config["username"],
                config["password"],
                config["log_level"],
            )

        args = " ".join(args)
        liquibase_command = liquibase_command + args

        # Find the index of "--password=" in the command string
        start_index = liquibase_command.find("--password=")

        # If "--password=" exists in the command string
        if start_index != -1:
            # Find the end index of the password value
            end_index = liquibase_command.find(" ", start_index)
            if end_index == -1:
                end_index = len(liquibase_command)

            # Replace the password value with asterisks
            output_liquibase_command = (
                liquibase_command[: start_index + len("--password=")]
                + "*********"
                + liquibase_command[end_index:]
            )

            print(output_liquibase_command)

        output = subprocess.check_output(
            liquibase_command, stderr=subprocess.STDOUT, shell=True
        )

        return output.decode("UTF-8")
