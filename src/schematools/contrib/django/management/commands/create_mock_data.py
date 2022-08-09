from typing import Any, Dict, List

from django.conf import settings
from django.core.management import BaseCommand, CommandParser

from schematools.contrib.django.datasets import get_datasets_from_files, get_datasets_from_url
from schematools.contrib.django.faker.create import create_data_for


class Command(BaseCommand):  # noqa: D101
    help = """Create mock data for Amsterdam schema files.

    Datasets (in DSO db) + dataset tables should already have been created,
    usually with the `import_schemas --create-tables` mgm. command.
    """  # noqa: A003
    requires_system_checks = []

    def add_arguments(self, parser: CommandParser) -> None:  # noqa: D102
        parser.add_argument("schema", nargs="*", help="Paths to local schema files to import")
        parser.add_argument(
            "--schema-url",
            default=settings.SCHEMA_URL,
            help=f"Schema URL (default: {settings.SCHEMA_URL})",
        )
        parser.add_argument("-s", "--size", type=int, default=50, help="Number of rows")
        parser.add_argument("--sql", action="store_true", help="Generate the sql statements.")
        parser.add_argument(
            "--start-at", type=int, default=1, help="Starting number for sequences."
        )
        parser.add_argument("--skip", nargs="*", default=[], help="Dataset ids to be skipped.")
        parser.add_argument(
            "--limit-to", nargs="*", default=[], help="Dataset ids to be included exclusively."
        )

    def handle(self, *args: List[Any], **options: Dict[str, Any]) -> None:  # noqa: D102
        if options["schema"]:
            datasets = get_datasets_from_files(list(options["schema"]))
        else:
            datasets = get_datasets_from_url(
                options["schema_url"], limit_to=options["limit_to"], skip=options["skip"]
            )

        sql_lines = create_data_for(
            *datasets, start_at=options["start_at"], size=options["size"], sql=options["sql"]
        )
        if sql_lines:
            self.stdout.write("\n".join(sql_lines))
