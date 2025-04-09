from pyquibase.pyquibase import Pyquibase

import pg8000 as pg

import config

def get_liquibase_connector(db_type: str, change_log_file: str = ""):
    """
    return the liquibase connector object based on db_type
    :param db_type: the type of database where migration will be applied
    :type db_type: str
    :param change_log_file: path of the changeLog file
    :type change_log_file: str
    """
    if db_type == "postgres":
        return Pyquibase.postgresql(
            host=config.POSTGRES_HOST,
            port=config.PORT,
            db_name=config.POSTGRES_DB,
            username=config.POSTGRES_USER,
            password=config.POSTGRES_PASSWORD,
            change_log_file=change_log_file,
            log_level=config.LOG_LEVEL,
        )
    return None


def get_db_connector(db_type: str):
    """
    return the db connector based on db_type
    :param db_type: the type of database where migration will be applied
    :type db_type: str
    """
    if db_type == "postgres":
        return pg.connect(
            host=config.POSTGRES_HOST,
            port=config.PORT,
            user=config.POSTGRES_USER,
            password=config.POSTGRES_PASSWORD,
            database=config.POSTGRES_DB,
        )
    return None

