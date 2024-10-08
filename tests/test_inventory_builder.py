import pytest

from unittest import mock
from unittest.mock import MagicMock
from benchling_sdk import models as benchling_models

from src import inventory_builder
from src import models


@pytest.mark.unittest
def test_write_shelves():
    actual = inventory_builder.write_shelves(shelves=4, parent_barcode="EQS-1234")
    expected = models.Location(
        barcodes=["Barcode","EQS-1234-S1", "EQS-1234-S2", "EQS-1234-S3", "EQS-1234-S4"],
        names=["Name", "Shelf 1", "Shelf 2", "Shelf 3", "Shelf 4"]
    )
    assert actual == expected


@pytest.mark.unittest
def test_write_racks_or_canes():
    actual = inventory_builder.write_racks_or_canes(shelves=4, rack_prefix="R", rack_in_full="Rack", racks=5, parent_barcode="EQS-1234", shelf_barcodes=["Name", "Shelf 1", "Shelf 2", "Shelf 3", "Shelf 4"],mode="a")
    expected = models.Location(
        barcodes=[
            "Barcode",
            "EQS-1234-S1-R1",
            "EQS-1234-S1-R2",
            "EQS-1234-S1-R3",
            "EQS-1234-S1-R4",
            "EQS-1234-S1-R5",
            "EQS-1234-S2-R1",
            "EQS-1234-S2-R2",
            "EQS-1234-S2-R3",
            "EQS-1234-S2-R4",
            "EQS-1234-S2-R5",
            "EQS-1234-S3-R1",
            "EQS-1234-S3-R2",
            "EQS-1234-S3-R3",
            "EQS-1234-S3-R4",
            "EQS-1234-S3-R5",
            "EQS-1234-S4-R1",
            "EQS-1234-S4-R2",
            "EQS-1234-S4-R3",
            "EQS-1234-S4-R4",
            "EQS-1234-S4-R5",
        ],
        names=[
            "Name",
            "Rack 1",
            "Rack 2",
            "Rack 3",
            "Rack 4",
            "Rack 5",
            "Rack 1",
            "Rack 2",
            "Rack 3",
            "Rack 4",
            "Rack 5",
            "Rack 1",
            "Rack 2",
            "Rack 3",
            "Rack 4",
            "Rack 5",
            "Rack 1",
            "Rack 2",
            "Rack 3",
            "Rack 4",
            "Rack 5",
        ]
    )
    assert actual == expected


@pytest.mark.unittest
def test_write_drawers_or_rows():
    """Drawers"""
    actual = inventory_builder.write_drawers_or_rows(
        rack_barcodes=[
            "Barcode",
            "EQS-1234-S1-R1",
            "EQS-1234-S1-R2",
            "EQS-1234-S1-R3",
            "EQS-1234-S1-R4",
            "EQS-1234-S1-R5",
        ],
        prefix="D", name_in_full="Drawer", drawers=2)
    expected = models.Location(
        barcodes=[
            "Barcode"
            "EQS-1234-S1-R1-D1",
            "EQS-1234-S1-R1-D2",
            "EQS-1234-S1-R2-D1",
            "EQS-1234-S1-R2-D2",
            "EQS-1234-S1-R3-D1",
            "EQS-1234-S1-R3-D2",
            "EQS-1234-S1-R4-D1",
            "EQS-1234-S1-R4-D2",
            "EQS-1234-S1-R5-D1",
            "EQS-1234-S1-R5-D2",
        ],
        names=[
            "Name",
            "Drawer 1",
            "Drawer 2",
            "Drawer 1",
            "Drawer 2",
            "Drawer 1",
            "Drawer 2",
            "Drawer 1",
            "Drawer 2",
            "Drawer 1",
            "Drawer 2",
        ]
    )
    assert actual == expected


@pytest.mark.unittest
def test_write_drawers_or_rows():
    """Rows"""
    actual = inventory_builder.write_drawers_or_rows(
        rack_barcodes=[
            "Barcode",
            "EQS-1234-S1-R1",
            "EQS-1234-S1-R2",
            "EQS-1234-S1-R3",
            "EQS-1234-S1-R4",
            "EQS-1234-S1-R5",
        ], prefix="R", name_in_full="Row", drawers=2)
    expected = models.Location(
        barcodes=[
            "Barcode",
            "EQS-1234-S1-R1-R1",
            "EQS-1234-S1-R1-R2",
            "EQS-1234-S1-R2-R1",
            "EQS-1234-S1-R2-R2",
            "EQS-1234-S1-R3-R1",
            "EQS-1234-S1-R3-R2",
            "EQS-1234-S1-R4-R1",
            "EQS-1234-S1-R4-R2",
            "EQS-1234-S1-R5-R1",
            "EQS-1234-S1-R5-R2",
        ],
        names=[
            "Name",
            "Row 1",
            "Row 2",
            "Row 1",
            "Row 2",
            "Row 1",
            "Row 2",
            "Row 1",
            "Row 2",
            "Row 1",
            "Row 2",
        ]
    )
    assert actual == expected

@pytest.mark.unittest
def test_write_boxes():
    actual = inventory_builder.write_boxes(boxes=3, barcodes=["Barcode", "EQS-1234-S1-R1-D1"])
    expected = ["Name", "Box 1", "Box 2", "Box 3"]
    assert actual == expected


@pytest.mark.unittest
def test_post_parent_location():
    mock_benchling_client = MagicMock()
    mock_location_create = MagicMock()
    mock_benchling_client.locations.create.return_value = mock_location_create
    
    with mock.patch("inventory_builder.create_session", mock_benchling_client):
    
        inventory_builder.post_parent_location(
            parent_barcode="EQS-1234",
            parent_name="FREEZER_NAME",
            location_schema="dev_freezer_schema",
            benchling_client=mock_benchling_client
        )

        assert mock_benchling_client.locations.create.call_count == 1


@pytest.mark.unittest
def test_extend_list():
    actual = inventory_builder.extend_list(
        barcodes=[
            "Barcode",
            "EQS-1234-S1-R1",
            "EQS-1234-S1-R2",
            "EQS-1234-S1-R3",
            "EQS-1234-S1-R4",
            "EQS-1234-S1-R5",
        ],
        parent_storage_id=["EQS-1234-S1"]
    )
    expected = [
        "EQS-1234-S1",
        "EQS-1234-S1",
        "EQS-1234-S1",
        "EQS-1234-S1",
        "EQS-1234-S1"
    ]
    assert actual == expected


@pytest.mark.unittest
def test_post_child_location():

    mock_benchling_client = MagicMock()
    mock_location_create = MagicMock()
    mock_benchling_client.locations.create.return_value = mock_location_create
    
    with mock.patch("inventory_builder.create_session", mock_benchling_client):
    
        inventory_builder.post_child_location(
            barcodes=[
                "Barcode",
                "EQS-1234-S1-R1-D1",
                "EQS-1234-S1-R1-D2",
                "EQS-1234-S1-R1-D3"
            ],
            names=[
                "Name",
                "Drawer 1",
                "Drawer 2",
                "Drawer 3",
            ],
            parent_storage_id=["dev_rack_id"],
            location_schema="dev_rack_schema",
            benchling_client=mock_benchling_client
        )
        assert mock_benchling_client.locations.create.call_count == 3


@pytest.mark.unittest
def test_post_box(capsys):

    mock_benchling_client = MagicMock()
    
    with mock.patch("inventory_builder.create_session", mock_benchling_client):

        inventory_builder.post_box(
            box_names=["Name", "Box 1", "Box 2", "Box 3"],
            parent_storage_id=["dev_rack_id"],
            schema="boxsch_xyz789",
            benchling_client=mock_benchling_client
        )

        assert mock_benchling_client.boxes.create.call_count == 3
    
        for i in range(2, 4):
            mock_benchling_client.boxes.create.assert_any_call(
                box=benchling_models.BoxCreate(
                    name=f"Box {i}",
                    schema_id="boxsch_xyz789",
                    parent_storage_id="dev_rack_id",
                )
            )

    expected_output = "3 of 3 boxes successfully created"
    captured_output = capsys.readouterr()
    assert expected_output in captured_output.out
