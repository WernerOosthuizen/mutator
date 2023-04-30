import hashlib
import logging

log = logging.getLogger()


def hash_object(obj):
    logging.debug(f"Creating hash for: {obj}")
    return hashlib.sha1(obj.__str__().encode("UTF-8")).hexdigest()  # nosec
