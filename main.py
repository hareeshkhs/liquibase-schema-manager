"""
Entry module
"""

import logging
import os
import subprocess
import sys
from subprocess import CalledProcessError
import re
import traceback

import config
from connector import get_liquibase_connector, get_db_connector
from version import __version__
from email_notifications import send_email_notification


def tag_the_database(db_type: str):
    """
    Execute a liquibase tag command
    """
    pyquibase = get_liquibase_connector(db_type)
    output = pyquibase.tag(__version__)
    print(f"----------> {db_type.capitalize()} Database tagged {__version__}")
    print(output)


def prefix_executions_using_connectors(db_type: str):
    """
    Executes these queries using connectors
    1. Create the schema if not exists for liquibase to store the chagesets data.
    2. Remove the lock on the table databasechangeloglock table from previous failed deployment.
    """
    if db_type == "postgres":
        print(
            f'----------> --url="jdbc:postgresql://{config.POSTGRES_HOST}:5432/?db={config.POSTGRES_DB}&username={config.POSTGRES_USER}&password=********"'
        )

        connection = get_db_connector(db_type)
        # Create a cursor object
        cur = connection.cursor()

        # Create schema db_logs if not exists
        cur.execute("create schema if not exists db_logs")

        # Commit the transaction
        connection.commit()

        # Check if the table exists
        cur.execute(
            "select exists(select * from information_schema.tables where table_name='databasechangeloglock' and table_schema = 'db_logs')"
        )
        table_exists = cur.fetchone()[0]

        # If the table exists, release the lock
        if table_exists:
            cur.execute(
                "UPDATE db_logs.databasechangeloglock SET LOCKED=FALSE, LOCKGRANTED = NULL, LOCKEDBY = NULL where ID=1"
            )
            connection.commit()

        # Close the cursor and connection
        cur.close()
        connection.close()


def deploy_file(change_log_file: str, db_type: str):
    """
    Deploys a changeLog files
    :param change_log_file: path of the changeLog file
    :type change_log_file: str
    :param db_type: the type of database where migration will be applied
    :type db_type: str
    """

    if change_log_file.endswith(".sql"):
        print(f"----------> Deploying changeLog file {change_log_file}")

        pyquibase = get_liquibase_connector(db_type, change_log_file)
        output = pyquibase.update()
        print(f"----------> Successfully deployed changeLog file {change_log_file}")
        return output

    return "----------> File extension is not .sql. Skipping it"


def get_required_values(output: str):
    lines = output.splitlines()

    start_index = None
    result_logs = None
    for i in range(len(lines) - 1, -1, -1):
        if "Caused by:" in lines[i]:
            start_index = i
            break

    if start_index is not None:
        result_logs = "\n".join(lines[start_index:])

    match = re.search(r"Migration failed for changeset\s(.+?::.+?::.+?):", output)
    dynamic_text = None

    if match:
        dynamic_text = match.group(1)

    return result_logs, dynamic_text


def replace_password(content: str):
    # Find the index of "--password=" in the command string
    start_index = content.find("--password=")

    # If "--password=" exists in the command string
    if start_index != -1:
        # Find the end index of the password value
        end_index = content.find(" ", start_index)
        if end_index == -1:
            end_index = len(content)

        # Replace the password value with asterisks
        content_output = content[: start_index + len("--password=")] + "*********" + content[end_index:]
    return content_output


def main():
    """
    Entry function for schema deployment
    This function is triggered with `python3 main.py`
    """
    directories = config.AVAILABLE_SCHEMAS

    print(f"----------> Available schemas Before Modification: {directories}")

    print(f"----------> Schema manager tag {__version__}")

    print(f"----------> Available Schemas Final List: {directories}")
    postgres_lock = False
    for directory in directories:
        try:
            os.listdir(directory)
        except FileNotFoundError as err:
            print(f"----------> No such schema available:  {directory}")
            print(str(err))
        else:
            db_type = "postgres"
            if not postgres_lock:
                prefix_executions_using_connectors(db_type)
                postgres_lock = True

            print(f"----------> Deploying schema {directory} on {db_type.capitalize()}")
            sorted_files = sorted(os.listdir(directory))
            for file in sorted_files:
                try:
                    filename = os.fsdecode(file)
                    change_log_file = directory + "/" + filename
                    response = deploy_file(change_log_file, db_type)
                    print(response)
                except CalledProcessError as err:
                    print("----------> ERROR!!")
                    print("----------> Execution halted due to the following error")
                    print("----------> Please fix it and release a new tag.")
                    print(err.stdout.decode("UTF-8"))
                    error_logs = err.stdout.decode("UTF-8")
                    caused_by, migration_failed_changeset = get_required_values(error_logs)
                    traceback_str = traceback.format_exc()
                    traceback_str_output = replace_password(traceback_str)
                    send_email_notification(
                        "FAILED",
                        config.POSTGRES_HOST,
                        directories,
                        __version__,
                        change_log_file,
                        migration_failed_changeset,
                        caused_by,
                        traceback_str_output,
                    )
                    sys.exit(1)
                tag_the_database(db_type)
    send_email_notification("SUCCESS", config.POSTGRES_HOST, directories, __version__, "None", "None", "None", "None")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        main()
