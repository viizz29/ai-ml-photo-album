from collections.abc import Mapping, Sequence

from hashids import Hashids
from fastapi.responses import JSONResponse

from .config import settings

hashids = Hashids(salt=settings.HASHIDS_SALT, min_length=8)


def _should_encode_key(key: str) -> bool:
    return key == "id" or key.endswith("_id")


def _to_camel_case(key: str) -> str:
    if "_" not in key:
        return key

    first, *rest = key.split("_")
    return first + "".join(part.capitalize() for part in rest)


def encode_ids_in_payload(value):
    if isinstance(value, Mapping):
        transformed = {}
        for key, item in value.items():
            key_str = str(key)
            response_key = _to_camel_case(key_str)

            if _should_encode_key(key_str) and isinstance(item, int) and not isinstance(item, bool):
                transformed[response_key] = hashids.encode(item)
            else:
                transformed[response_key] = encode_ids_in_payload(item)
        return transformed

    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [encode_ids_in_payload(item) for item in value]

    return value


class HashIdJSONResponse(JSONResponse):
    def render(self, content) -> bytes:
        return super().render(encode_ids_in_payload(content))
