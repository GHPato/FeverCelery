from io import BytesIO
import xml.etree.ElementTree as ET
from dateutil import parser
from app.models.event import Events
from app.services.connectors.postgres import Postgres
import logging

logger = logging.getLogger(__name__)


def process_and_store_events_stream(xml_data):
    """
    Processes XML data using streaming parsing, checking for existing events
    and updating or inserting as necessary.
    Handles large XML files efficiently using iterparse and
    batches database operations.
    """
    session = Postgres.get_scoped_session()
    logger.info("Started processing events...")

    try:
        # Ensure the XML data is in bytes, just to be safe
        if isinstance(xml_data, str):
            xml_data = xml_data.encode("utf-8")

        # Wrap the XML byte string in a file-like object for streaming parsing
        xml_file = BytesIO(xml_data)  # Correct use of BytesIO for byte string

        # Stream the XML file using iterparse
        context = ET.iterparse(xml_file, events=("start", "end"))
        context = iter(context)
        event_type, root = next(context)

        batch_size = 100
        events_to_insert = []
        events_to_update = []

        for event_type, elem in context:
            if event_type == "end" and elem.tag == "base_event":
                event_id = elem.get("base_event_id")
                title = elem.get("title")
                sell_mode = elem.get("sell_mode")
                logger.info(
                    f"Processing event: {title} (ID: {event_id}) with \
                        sell mode: {sell_mode}"
                )

                for event in elem.findall("event"):
                    try:
                        start_date = parser.isoparse(event.get("event_start_date"))
                        end_date = parser.isoparse(event.get("event_end_date"))
                    except (ValueError, TypeError) as e:
                        logger.error(
                            f"Invalid date for event: {title}. Error: {str(e)}"
                        )
                        continue  # Skip this event if dates are invalid

                    min_price = float(
                        min(
                            [float(zone.get("price")) for zone in event.findall("zone")]
                        )
                    )
                    max_price = float(
                        max(
                            [float(zone.get("price")) for zone in event.findall("zone")]
                        )
                    )

                    # Check if the event already exists in the database
                    existing_event = (
                        session.query(Events).filter_by(id=event_id).first()
                    )

                    if existing_event:
                        # Update if details have changed
                        if (
                            existing_event.start_date != start_date
                            or existing_event.end_date != end_date
                            or existing_event.min_price != min_price
                            or existing_event.max_price != max_price
                            or existing_event.is_online != sell_mode
                        ):
                            existing_event.start_date = start_date
                            existing_event.end_date = end_date
                            existing_event.min_price = min_price
                            existing_event.max_price = max_price
                            existing_event.is_online = sell_mode
                            events_to_update.append(existing_event)
                    else:
                        # Insert new event
                        new_event = Events(
                            id=event_id,
                            title=title,
                            start_date=start_date,
                            end_date=end_date,
                            min_price=min_price,
                            max_price=max_price,
                            is_online=sell_mode,
                        )
                        events_to_insert.append(new_event)

                # Commit batches for inserts and updates
                if len(events_to_insert) >= batch_size:
                    session.bulk_save_objects(events_to_insert)
                    session.commit()
                    logger.info(
                        f"Inserted {len(events_to_insert)} events \
                            into the database."
                    )
                    events_to_insert = []

                if len(events_to_update) >= batch_size:
                    session.bulk_save_objects(events_to_update)
                    session.commit()
                    logger.info(
                        f"Updated {len(events_to_update)} events \
                            in the database."
                    )
                    events_to_update = []

                # Clear the processed element to free memory
                elem.clear()

        # Commit any remaining events after processing
        if events_to_insert:
            session.bulk_save_objects(events_to_insert)
            session.commit()
            logger.info(f"Inserted {len(events_to_insert)} events \
                        into the database.")

        if events_to_update:
            session.bulk_save_objects(events_to_update)
            session.commit()
            logger.info(f"Updated {len(events_to_update)} \
                        events in the database.")

    except Exception as e:
        session.rollback()
        logger.error(f"Error processing events: {str(e)}")
    finally:
        if session:
            Postgres.close_scoped_session()  # Ensure the session is closed
