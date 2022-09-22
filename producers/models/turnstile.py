"""Creates a turnstile data producer"""
import logging
from pathlib import Path

from confluent_kafka import avro

from models.producer import Producer
from models.turnstile_hardware import TurnstileHardware

logger = logging.getLogger(__name__)


class Turnstile(Producer):
    key_schema = avro.load(f"{Path(__file__).parents[0]}/schemas/turnstile_key.json")

    #
    # TODO: Define this value schema in `schemas/turnstile_value.json, then uncomment the below
    #
    # value_schema = avro.load(
    #    f"{Path(__file__).parents[0]}/schemas/turnstile_value.json"
    # )
    value_schema = avro.load(f"{Path(__file__).parents[0]}/schemas/turnstile_value.json")

    def __init__(self, station):
        """Create the Turnstile"""
        # station_name = (
        #     station.name.lower()
        #     .replace("/", "_and_")
        #     .replace(" ", "_")
        #     .replace("-", "_")
        #     .replace("'", "")
        # )
        station_name = 'org.chicago.cta.station.turnstile.v1'

        #
        #
        # TODO: Complete the below by deciding on a topic name, number of partitions, and number of
        # replicas
        #
        #
        super().__init__(
            f"{station_name}",  # TODO: Come up with a better topic name
            key_schema=Turnstile.key_schema,
            # TODO: value_schema=Turnstile.value_schema, TODO: Uncomment once schema is defined
            # TODO: num_partitions=???,
            # TODO: num_replicas=???,
            value_schema=Turnstile.value_schema,
            num_partitions=1,
            num_replicas=1,
        )
        self.station = station
        self.turnstile_hardware = TurnstileHardware(station)

    def run(self, timestamp, time_step):
        """Simulates riders entering through the turnstile."""
        num_entries = self.turnstile_hardware.get_entries(timestamp, time_step)
        #
        #
        # TODO: Complete this function by emitting a message to the turnstile topic for the number
        # of entries that were calculated
        #
        #
        try:
            for i in range(num_entries):
                self.producer.produce(
                    topic=self.topic_name,
                    key_schema=Turnstile.key_schema,
                    value_schema=Turnstile.value_schema,
                    key={"timestamp": self.time_millis()},
                    value={
                        "station_id": int(self.station.station_id),
                        "station_name": str(self.station.name),
                        "line": str(self.station.color)
                    }
                )
        except Exception as e:
            logger.error(f"Turnstile running error: {e}")
            logger.info("turnstile kafka integration incomplete - skipping")
