from typing import Literal

import click


def env_variables() -> tuple[str, str, str, str, str]:
    """Based on user input, return env variables to create a hierarchal configuration."""

    instance = None

    while instance is None:
        instance = click.prompt("\nSpecify the instance: ", type=click.Choice(["dev", "test", "prod"], case_sensitive=False))

    if instance == "dev":
        instance = "orgdev"
        freezer_schema = ""
        shelf_schema = ""
        rack_schema = ""
        drawer_schema = ""
    
    elif instance == "test":
        instance = "orgtest"
        freezer_schema = ""
        shelf_schema = ""
        rack_schema = ""
        drawer_schema = ""

    else:
        instance = "org"
        freezer_schema = ""
        shelf_schema = ""
        rack_schema = ""
        drawer_schema = ""

    return instance, freezer_schema, shelf_schema, rack_schema, drawer_schema


@click.command()
@click.option('--racks_prompt', prompt="Using Racks or Canes? ", type=click.Choice(['Racks', 'Canes'], case_sensitive=False))
@click.option('--drawers_prompt', prompt="Using Drawers or Rows? ", type=click.Choice(['Drawers', 'Rows', 'Neither'], case_sensitive=False))
def collect_input(racks_prompt, drawers_prompt) -> tuple[str, str, int, str, str, int, str, str, int, int, str]:
    confirm_1 = False
    confirm_2 = False

    while confirm_1 is False:
        parent_barcode = click.prompt("\nEnter the asset tag ", type=str)
        parent_name = click.prompt(
            "\nEnter the Location name. This is the refrigerator, freezer or LN2 ",
            type=str,
        )
        confirm_1 = click.confirm(
            f"\nAsset tag: {parent_barcode}\nLocation name: {parent_name}\n\nDoes this look correct?",
            abort=False,
        )

    while confirm_2 is False:
        shelves = click.prompt("\nHow many shelves? ", type=int)
        canes_or_racks = racks_prompt

        if canes_or_racks != "Canes":
            rack_prefix = "R"
            rack_in_full = "Rack"
        else:
            rack_prefix = "C"
            rack_in_full = "Cane"

        racks = click.prompt(f"\nHow many {rack_in_full}s per shelf? ", type=int)

        # Because drawers/rows are optional, prompt for # of drawers is within if/else block
        drawer_or_row = drawers_prompt

        if drawer_or_row == "Rows":
            drawer_prefix = "R"
            drawer_in_full = "Row"
            drawers = click.prompt(f"\nHow many {drawer_in_full}s per {rack_in_full}? ", type=int)

        elif drawer_or_row == "Drawers":
            drawer_prefix = "D"
            drawer_in_full = "Drawer"
            drawers = click.prompt(f"\nHow many {drawer_in_full}s per {rack_in_full}? ", type=int)
        else:
            drawer_prefix = None
            drawer_in_full = None
            drawers = 0

        boxes = click.prompt(f"\nHow many boxes per {drawer_in_full}? ", type=int)
        n_dimension = click.prompt("\nSelect box dimensions:\n1. 9x9\n2. 10x10 ", type=click.IntRange(1,2))
        confirm_2 = click.confirm(
            f"\n# of Shelves: {shelves}\n# of {rack_in_full}s per shelf: {racks}\n# of {drawer_in_full}s per {rack_in_full}: {drawers}\n# of Boxes per {drawer_in_full}: {boxes}\n\nDoes this look correct? ",
            abort=False,
        )

    return parent_barcode, parent_name, shelves, rack_prefix, rack_in_full, racks, drawer_prefix, drawer_in_full, drawers, boxes, n_dimension


def box_schema_id(n_dimension: int, instance: Literal["orgdev", "orgtest", "org"]) -> str:
    """Based on collect_input, return the schema_id for the box dimension and instance."""

    if n_dimension == 1 and instance == "dev":
        dimension_id = "boxsch_xyz789"  # 9x9 boxes

    elif n_dimension == 2 and instance == "dev":
        dimension_id = "boxsch_xyz987"  # 10x10 boxes
    
    elif n_dimension == 1 and instance == "test":
        dimension_id = "boxsch_xyz123"  # 9x9 boxes

    elif n_dimension == 2 and instance == "test":
        dimension_id = "boxsch_xyz456"  # 10x10 boxes

    elif n_dimension == 1 and instance == "prod":
        dimension_id = "boxsch_abc123"  # 9x9 boxes

    elif n_dimension == 2 and instance == "prod":
        dimension_id = "boxsch_abc456"  # 10x10 boxes

    return dimension_id
