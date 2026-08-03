from django.db import migrations


def repair_original_main_contents_schema(apps, schema_editor):
    """Repair databases where the 0049 rename was recorded but not applied."""
    table_name = "diamm_data_source"
    legacy_column = "source_main_contents"
    canonical_column = "original_main_contents"
    with schema_editor.connection.cursor() as cursor:
        columns = {
            column.name
            for column in schema_editor.connection.introspection.get_table_description(
                cursor, table_name
            )
        }

    if legacy_column in columns and canonical_column not in columns:
        quote = schema_editor.quote_name
        schema_editor.execute(
            f"ALTER TABLE {quote(table_name)} "
            f"RENAME COLUMN {quote(legacy_column)} TO {quote(canonical_column)}"
        )


class Migration(migrations.Migration):
    dependencies = [
        ("diamm_data", "0049_remove_source_host_main_contents_and_more"),
    ]

    operations = [
        migrations.RunPython(
            repair_original_main_contents_schema,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
