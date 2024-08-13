from typing import Any
from typing import Literal

import click
from pydantic import BaseModel, field_validator


class DevelopmentSettings(BaseModel):
    tenant: Literal["orgdev"]
    freezer_schema: str = "dev_freezer_schema"
    shelf_schema: str = "dev_shelf_schema"
    rack_schema: str = "dev_rack_schema"
    drawer_schema: str = "dev_drawer_schema"


class TestSettings(BaseModel):
    tenant: Literal["orgtest"]
    freezer_schema: str = "test_freezer_schema"
    shelf_schema: str = "test_shelf_schema"
    rack_schema: str = "test_rack_schema"
    drawer_schema: str = "test_drawer_schema"


class ProductionSettings(BaseModel):
    tenant: Literal["org"]
    freezer_schema: str = "prod_freezer_schema"
    shelf_schema: str = "prod_shelf_schema"
    rack_schema: str = "prod_rack_schema"
    drawer_schema: str = "prod_drawer_schema"


class StorageConfig(BaseModel):
    parent_barcode: str
    parent_name: str
    shelves: int
    rack_prefix: Literal["R", "C"]
    rack_in_full: Literal["Racks", "Canes"]
    racks: int
    drawer_prefix: Literal["D", "R"]
    drawer_in_full: Literal["Drawers", "Rows"]
    drawers: int
    boxes: int
    box_dimension: int

    @field_validator("shelves", "racks", "drawers", "boxes")
    def validate_numeric_input(cls, value):
        if value < 0:
            raise ValueError(
                f"Only zero or positive values permitted, revise provided input: {value}"
            )
        return value


def env_variables() -> Any:
    """Based on user input, return env variables to prepare storage configuration.

    returns:
        DevelopmentSettings, TestSettings or Production Settings(
            tenant = 'orgdev'
            freezer_schema = ''
            shelf_schema = ''
            rack_schema = ''
            drawer_schema = ''
            secret_name = ''
        )
    """

    instance = None

    while instance is None:
        instance = click.prompt(
            "\nSpecify the instance: ",
            type=click.Choice(["dev", "test", "prod"], case_sensitive=False),
        )

    if instance == "dev":
        return DevelopmentSettings

    elif instance == "test":
        return TestSettings

    return ProductionSettings


@click.command()
@click.option(
    "--racks_prompt",
    prompt="Using Racks or Canes? ",
    type=click.Choice(["Racks", "Canes"], case_sensitive=False),
)
@click.option(
    "--drawers_prompt",
    prompt="Using Drawers or Rows? ",
    type=click.Choice(["Drawers", "Rows", "Neither"], case_sensitive=False),
)
def collect_input(racks_prompt, drawers_prompt) -> StorageConfig:
    """Based on user and implementation needs, sets up the required storage configuration

    returns:
        StorageConfig(
            parent_barcode: str,
            parent_name: str,
            shelves: int,
            rack_prefix: str,
            rack_in_full: str,
            racks: int,
            drawer_prefix: str,
            drawer_in_full: str,
            drawers: int,
            boxes: int,
            box_dimension: int,
        )
    """
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

        racks = click.prompt(
            f"\nHow many {rack_in_full}s per shelf? ",
            type=int,
        )

        # Because drawers/rows are optional, prompt for # of drawers is within if/else block
        drawer_or_row = drawers_prompt

        if drawer_or_row == "Rows":
            drawer_prefix = "R"
            drawer_in_full = "Row"
            drawers = click.prompt(
                f"\nHow many {drawer_in_full}s per {rack_in_full}? ",
                type=int,
            )

        elif drawer_or_row == "Drawers":
            drawer_prefix = "D"
            drawer_in_full = "Drawer"
            drawers = click.prompt(
                f"\nHow many {drawer_in_full}s per {rack_in_full}? ",
                type=int,
            )
        else:
            drawer_prefix = None
            drawer_in_full = None
            drawers = 0

        boxes = click.prompt(
            f"\nHow many boxes per {drawer_in_full}? ",
            type=int,
        )
        box_dimension = click.prompt(
            "\nSelect box dimensions:\n1. 9x9\n2. 10x10 ",
            type=click.IntRange(1, 2),
        )
        confirm_2 = click.confirm(
            f"\n# of Shelves: {shelves}\n# of {rack_in_full}s per shelf: {racks}\n# of {drawer_in_full}s per {rack_in_full}: {drawers}\n# of Boxes per {drawer_in_full}: {boxes}\n\nDoes this look correct? ",
            abort=False,
        )

    return StorageConfig(
        parent_barcode,
        parent_name,
        shelves,
        rack_prefix,
        rack_in_full,
        racks,
        drawer_prefix,
        drawer_in_full,
        drawers,
        boxes,
        box_dimension,
    )


def box_schema_id(
    n_dimension: int,
    tenant: Literal["orgdev", "orgtest", "org"],
) -> str:
    """Based on collect_input, return the schema_id for the box dimension and instance."""

    if n_dimension == 1 and tenant == "orgdev":
        schema = "boxsch_xyz789"  # 9x9 boxes

    elif n_dimension == 2 and tenant == "orgdev":
        schema = "boxsch_xyz987"  # 10x10 boxes

    elif n_dimension == 1 and tenant == "orgtest":
        schema = "boxsch_xyz123"  # 9x9 boxes

    elif n_dimension == 2 and tenant == "orgtest":
        schema = "boxsch_xyz456"  # 10x10 boxes

    elif n_dimension == 1 and tenant == "org":
        schema = "boxsch_abc123"  # 9x9 boxes

    elif n_dimension == 2 and tenant == "org":
        schema = "boxsch_abc456"  # 10x10 boxes

    return schema
