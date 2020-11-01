"""Fetch latest parking garage information from Amsterdam."""
from aiohttp import ClientSession, ClientResponseError
from dataclasses import dataclass
import logging

@dataclass
class AmsterdamCase:
    """Class for garages Amsterdam"""

    URL = "http://opd.it-t.nl/data/amsterdam/ParkingLocation.json"
    NAME = "Garages Amsterdam"

    id: str
    garageName: str
    state: str
    freeSpaceShort: int
    freeSpaceLong: int
    shortCapacity: int
    longCapacity: int

    @staticmethod
    def from_json(item):
        attrs = item["properties"]
        id = item
        return AmsterdamCase(
            id=id["Id"],
            garageName=correctName(attrs["Name"]),
            state=attrs["State"],
            freeSpaceShort=attrs["FreeSpaceShort"],
            freeSpaceLong=attrs["FreeSpaceLong"],
            shortCapacity=attrs["ShortCapacity"],
            longCapacity=attrs["LongCapacity"],
        )

DEFAULT_SOURCE = AmsterdamCase

def correctName(name):
    """Change parking garage name for consistency if needed."""
    filter = ["CE-","ZD-","ZO-","ZU-"]
    corrections = ["P1 ", "P3 "]

    if any(x in name for x in filter):
        name = name[3:]
        if any(y in name for y in corrections):
            return name[:1] + '0' + name[1:]
        else:
            return name
    else:
        return name

async def get_cases(session: ClientSession, *, source=DEFAULT_SOURCE):
    """Fetch parking garage data."""
    resp = await session.get(source.URL)
    data = await resp.json(content_type=None)

    if 'error' in data:
        raise ClientResponseError(
            resp.request_info,
            resp.history,
            status=data['error']['code'],
            message=data['error']['message'],
            headers=resp.headers
        )

    results = []
    wrongKeys = ['FP','Fiets']

    # results = [
    #     source.from_json(item)
    #     for item in data["features"]
    #     if not any(x in item["properties"]["Name"] for x in wrongKeys)
    # ]

    for item in data["features"]:
        try:
            if not any(x in item["properties"]["Name"] for x in wrongKeys):
                results.append(source.from_json(item))
        except KeyError:
            logging.getLogger(__name__).warning("Got wrong data: %s", item)

    # print(results)
    return results