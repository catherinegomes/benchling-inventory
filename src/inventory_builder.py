import csv
from typing import Any, List, Literal, Dict

from benchling_sdk import models as benchling_models
from benchling_sdk.auth.client_credentials_oauth2 import ClientCredentialsOAuth2
from benchling_sdk.benchling import Benchling

from src import log
from src import models
from src import secrets_manager
from src import settings


logger = log.logger()


def create_session(tenant: str, auth: Dict):
    benchling_client = Benchling(
        url=f"https://{tenant}.benchling.com",
        auth_method=ClientCredentialsOAuth2(
            client_id=auth['client_id'], client_secret=auth['client_secret'],
        ),
    )
    return benchling_client


def write_to_csv(
    mode: Literal['w+', 'a'],
    location_barcodes: List[str],
    names: List[str],
    **barcodes: List[str],
) -> None:

    with open('inventory_locations.csv', mode, newline='') as f:
        writer = csv.writer(f)

        if barcodes:
            writer.writerows(zip(location_barcodes, barcodes, names))
        else:
            writer.writerows(zip(location_barcodes, names))


def write_shelves(shelves: int, parent_barcode: str) -> models.Location:
    'Write custom Shelf names and barcodes to csv'
    logger.info('initiated')

    location_barcodes = ['Location Barcode'] + [parent_barcode] * shelves
    shelf_barcodes = ['Barcode'] + [
        f"{parent_barcode}-S{count}" for count in range(1, shelves + 1)
    ]
    shelf_names = ['Name'] + \
        [f"Shelf {count}" for count in range(1, shelves + 1)]

    write_to_csv(
        mode='w+',
        location_barcodes=location_barcodes,
        barcodes=shelf_barcodes,
        names=shelf_names,
    )

    return models.Location(barcodes=shelf_barcodes, names=shelf_names)


def write_racks(
    shelves: int,
    rack_prefix: str,
    rack_in_full: str,
    racks: int,
    parent_barcode: str,
    shelf_barcodes: List[str],
) -> models.Location:
    'Write custom [ Rack | Cane ] names and barcodes to csv'
    logger.info('initiated')

    location_barcodes = ['Location Barcode']
    rack_barcodes = ['Barcode']
    rack_names = ['Name']

    if shelves != 0 and shelf_barcodes:
        for s_count in range(1, shelves + 1):
            for r_count in range(1, racks + 1):
                location_barcodes.append(shelf_barcodes[s_count])
                rack_barcodes.append(
                    f"{parent_barcode}-S{s_count}-{rack_prefix}{r_count}",
                )
                rack_names.append(f"{rack_in_full} {r_count}")
    else:
        for r_count in range(1, racks + 1):
            location_barcodes.append(parent_barcode)
            rack_barcodes.append(f"{parent_barcode}-{rack_prefix}{r_count}")
            rack_names.append(f"{rack_in_full} {r_count}")

    write_to_csv(
        mode='a',
        location_barcodes=location_barcodes,
        barcodes=rack_barcodes,
        names=rack_names,
    )

    return models.Location(barcodes=rack_barcodes, names=rack_names)


def write_drawers_or_rows(
    rack_barcodes: List[str], prefix: str, name_in_full: str, drawers: int,
) -> models.Location:
    'Write custom [ Drawer | Row ] names and barcodes to csv'
    logger.info('initiated')

    location_barcodes = ['Location Barcode']
    barcodes = ['Barcode']
    names = ['Name']

    for e in rack_barcodes[1:]:
        for i in range(1, drawers + 1):
            location_barcodes.append(e)
            barcodes.append(f"{e}-{prefix}{i}")
            names.append(f"{name_in_full} {i}")

    write_to_csv(
        mode='a',
        location_barcodes=location_barcodes,
        barcodes=barcodes,
        names=names,
    )

    return models.Location(barcodes=barcodes, names=names)


def write_boxes(boxes: int, barcodes: List[str]) -> List[str]:
    'Write Box names [Box 1, Box 2, Box 3...] to csv.'
    logger.info('initiated')

    location_barcodes = ['Location Barcode']
    box_names = ['Name']

    for e in range(1, len(barcodes)):
        location_barcodes.extend([barcodes[e]] * boxes)
        box_names.extend([f"Box {b_count}" for b_count in range(1, boxes + 1)])

    write_to_csv('a', location_barcodes=location_barcodes, names=box_names)

    return box_names


def post_parent_location(
    parent_barcode: str, parent_name: str, location_schema: str, benchling_client: Any
) -> str:
    'POST request to create storage location with custom barcode'
    logger.info('initiated')

    r = benchling_client.locations.create(
        location=benchling_models.LocationCreate(
            name=parent_name, schema_id=location_schema, barcode=parent_barcode,
        ),
    )
    return [r.id]


def extend_list(barcodes: List[str], parent_storage_id: List[str]) -> List[str]:
    logger.info('initiated')

    fold = (len(barcodes) - 1) // len(parent_storage_id)
    return [e for e in parent_storage_id for _ in range(fold)]


def post_child_location(
    barcodes: List[str],
    names: List[str],
    parent_storage_id: List[str],
    location_schema: str,
    benchling_client: Any
) -> List[str]:
    'POST request to create interior locations with custom barcodes'
    logger.info('initiated')

    storage_ids = []

    if len(parent_storage_id) == 1:
        for e in range(len(barcodes) - 1):
            r = benchling_client.locations.create(
                location=benchling_models.LocationCreate(
                    name=names[e + 1],
                    schema_id=location_schema,
                    barcode=barcodes[e + 1],
                    parent_storage_id=parent_storage_id[0],
                ),
            )
            storage_ids.append(r.id)

    else:
        if len(parent_storage_id) < len(barcodes):
            parent_storage_ids = extend_list(barcodes, parent_storage_id)
            barcodes = barcodes[1:]  # Ensures the lists are of all same length
            names = names[1:]

            for e in range(len(barcodes)):

                r = benchling_client.locations.create(
                    location=benchling_models.LocationCreate(
                        name=names[e],
                        schema_id=location_schema,
                        barcode=barcodes[e],
                        parent_storage_id=parent_storage_ids[e],
                    ),
                )

                storage_ids.append(r.id)
    return storage_ids


def post_box(
    box_names: List[str], parent_storage_id: List[str], schema: str,
    benchling_client: Any
) -> None:
    'POST request to create boxes with autogenerated barcodes'
    logger.info('initiated')

    if len(parent_storage_id) < len(box_names):
        parent_storage_ids = extend_list(box_names, parent_storage_id)
    else:
        parent_storage_ids = parent_storage_id

    count = 0

    for e in range(1, len(box_names)):
        benchling_client.boxes.create(
            box=benchling_models.BoxCreate(
                name=box_names[e],
                schema_id=schema,
                parent_storage_id=parent_storage_ids[e - 1],
            ),
        )

        count += 1

    print(f"{count} of {len(box_names) - 1} boxes successfully created")


def main():

    # Create parent_location
    top_parent_storage_id = post_parent_location(
        parent_barcode=storage.parent_barcode,
        parent_name=storage.parent_name,
        location_schema=parameters.freezer_schema,
        benchling_client=benchling_client
    )

    # Create shelves & racks within parent location
    if storage.shelves != 0:
        shelf = write_shelves(storage.shelves, storage.parent_barcode)
        rack = write_racks(
            storage.shelves, storage.rack_prefix, storage.rack_in_full, storage.racks, storage.parent_barcode, shelf.barcodes,
        )

        # create (shelf) child locations
        shelf_storage_ids = post_child_location(
            shelf.barcodes,
            shelf.names,
            parent_storage_id=top_parent_storage_id,
            location_schema=parameters.shelf_schema,
            benchling_client=benchling_client
        )

        # Create (rack/cane) child locations within shelves
        rack_storage_ids = post_child_location(
            rack.barcodes,
            rack.names,
            parent_storage_id=shelf_storage_ids,
            location_schema=parameters.rack_schema,
            benchling_client=benchling_client
        )

    # Create racks within parent for LN2 configuration
    else:
        rack = write_racks(
            storage.shelves, storage.rack_prefix, storage.rack_in_full, storage.racks, storage.parent_barcode, shelf_barcodes=0,
        )
        rack_storage_ids = post_child_location(
            rack.barcodes,
            rack.names,
            parent_storage_id=top_parent_storage_id,
            location_schema=parameters.rack_schema,
            benchling_client=benchling_client
        )

    # Create drawers within racks/canes
    if storage.drawers != 0:
        drawer = write_drawers_or_rows(
            rack.barcodes, parameters.drawer_prefix, parameters.drawer_in_full, storage.drawers)
        drawer_storage_ids = post_child_location(
            drawer.barcodes,
            drawer.names,
            parent_storage_id=rack_storage_ids,
            location_schema=parameters.drawer_schema,
            benchling_client=benchling_client
        )

        # Create boxes within drawers
        boxes_names = write_boxes(storage.boxes, drawer.barcodes)
        post_box(
            box_names=boxes_names,
            parent_storage_id=drawer_storage_ids,
            schema=box_schema,
            benchling_client=benchling_client
        )

    # Create boxes within racks/canes for LN2 configuration
    else:
        boxes_names = write_boxes(storage.boxes, rack.barcodes)
        post_box(
            box_names=boxes_names,
            parent_storage_id=rack_storage_ids,
            schema=box_schema,
            benchling_client=benchling_client
        )


if __name__ == '__main__':

    parameters = settings.env_variables()

    secret = secrets_manager.get_secret(secret_name=parameters.secret)

    benchling_client = create_session(tenant=parameters.tenant, auth=secret)

    storage = settings.collect_input.main(standalone_mode=False)
    box_schema = settings.box_schema_id(
        storage.box_dimension, parameters.tenant)

    main()
