import json
from schematools.importer.ndjson import NDJSONImporter
from pg_grant import query
from schematools.permissions import create_acl_from_profiles, apply_schema_and_profile_permissions
from sqlalchemy.exc import ProgrammingError
import pytest
from schematools.types import DatasetSchema


def test_openbaar_permissions(here, engine, afval_schema, dbsession):
    importer = NDJSONImporter(afval_schema, engine)
    importer.generate_tables("containers", truncate=True)
    importer.generate_tables("clusters", truncate=True)

    # Setup schema and profile
    ams_schema = {afval_schema.id: afval_schema}
    profile_path = here / "files" / "profiles" / "gebieden_test.json"
    with open(profile_path) as f:
        profile = json.load(f)
    profiles = {profile["name"]: profile}

    # Create postgres roles
    _create_role(engine, "openbaar")
    _create_role(engine, "bag_r")
    # Check if the roles exist, the tables exist, and the roles have no read privilige on the tables.
    _check_permission_denied(engine, "openbaar", "afvalwegingen_containers")
    _check_permission_denied(engine, "bag_r", "afvalwegingen_clusters")

    apply_schema_and_profile_permissions(engine, ams_schema, profiles, "openbaar", "OPENBAAR")
    apply_schema_and_profile_permissions(engine, ams_schema, profiles, "bag_r", "BAG/R")

    _check_permission_granted(engine, "openbaar", "afvalwegingen_containers")
    _check_permission_denied(engine, "openbaar", "afvalwegingen_clusters")
    _check_permission_denied(engine, "bag_r", "afvalwegingen_containers")
    _check_permission_granted(engine, "bag_r", "afvalwegingen_clusters")






def test_interacting_permissions(here, engine, gebieden_schema, dbsession):
    """Prove that dataset, table, and field permissions are set according to the "OF-OF" Exclusief principle"""

    ndjson_path = here / "files" / "data" / "gebieden.ndjson"
    importer = NDJSONImporter(gebieden_schema, engine)
    importer.generate_tables("bouwblokken", truncate=True)
    importer.load_file(ndjson_path)
    importer.generate_tables("buurten", truncate=True)

    # Setup schema and profile
    ams_schema = {gebieden_schema.id: gebieden_schema}
    profile_path = here / "files" / "profiles" / "gebieden_test.json"
    with open(profile_path) as f:
        profile = json.load(f)
    profiles = {profile["name"]: profile}

    # Create postgres roles
    _create_role(engine, "level_a")
    _create_role(engine, "level_b")
    _create_role(engine, "level_c")

    # Check if the roles exist, the tables exist, and the roles have no read privilige on the tables.
    _check_permission_denied(engine, "level_a", "gebieden_bouwblokken")
    _check_permission_denied(engine, "level_b", "gebieden_bouwblokken")
    _check_permission_denied(engine, "level_c", "gebieden_bouwblokken")
    _check_permission_denied(engine, "level_a", "gebieden_buurten")
    _check_permission_denied(engine, "level_b", "gebieden_buurten")
    _check_permission_denied(engine, "level_c", "gebieden_buurten")

    # Apply the permissions from Schema and Profiles.
    apply_schema_and_profile_permissions(engine, ams_schema, profiles, "level_a", "LEVEL/A")
    apply_schema_and_profile_permissions(engine, ams_schema, profiles, "level_b", "LEVEL/B")
    apply_schema_and_profile_permissions(engine, ams_schema, profiles, "level_c", "LEVEL/C")

    # Check if the read priviliges are correct
    _check_permission_denied(engine, "level_a", "gebieden_bouwblokken")
    _check_permission_granted(engine, "level_b", "gebieden_bouwblokken", "id, eind_geldigheid")
    _check_permission_denied(engine, "level_b", "gebieden_bouwblokken", "begin_geldigheid")
    _check_permission_denied(engine, "level_c", "gebieden_bouwblokken", "id, eind_geldigheid")
    _check_permission_granted(engine, "level_c", "gebieden_bouwblokken", "begin_geldigheid")
    _check_permission_granted(engine, "level_a", "gebieden_buurten")
    _check_permission_denied(engine, "level_b", "gebieden_buurten")
    _check_permission_denied(engine, "level_c", "gebieden_buurten")


def _create_role(engine, role):
    #  If role already exists just fail and ignore. This may happen if a previous pytest did not terminate correctly.
    try:
        engine.execute('CREATE ROLE "{}"'.format(role))
    except ProgrammingError:
        #  psycopg2.errors.DuplicateObject
        pass


def _check_permission_denied(engine, role, table, column='*'):
    """Check if role has no SELECT permission on table. Fail if role, table or column does not exist."""
    with pytest.raises(Exception) as e_info:
        with engine.begin() as connection:
            connection.execute("SET ROLE {}".format(role))
            connection.execute("SELECT {} FROM {}".format(column, table))
            connection.execute("RESET ROLE")
    assert "permission denied for table {}".format(table) in str(e_info)


def _check_permission_granted(engine, role, table, column='*'):
    "Check if role has SELECT permission on table. Fail if role, table or column does not exist."
    with engine.begin() as connection:
        connection.execute("SET ROLE {}".format(role))
        result = connection.execute("SELECT {} FROM {}".format(column, table))
        connection.execute("RESET ROLE")
    assert result

