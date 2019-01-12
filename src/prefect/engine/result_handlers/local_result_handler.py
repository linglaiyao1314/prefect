# Licensed under LICENSE.md; also available at https://www.prefect.io/licenses/alpha-eula

"""
Result Handlers provide the hooks that Prefect uses to store task results in production; a `ResultHandler` can be provided to a `Flow` at creation.

Anytime a task needs its output or inputs stored, a result handler is used to determine where this data should be stored (and how it can be retrieved).
"""
import base64
import tempfile
from typing import Any

import cloudpickle

from prefect.engine.result_handlers import ResultHandler


class LocalResultHandler(ResultHandler):
    """
    Hook for storing and retrieving task results from local file storage. Only intended to be used
    for local testing and development. Task results are serialized using `cloudpickle` and stored in the
    provided location for use in future runs.

    **NOTE**: Stored results will _not_ be automatically cleaned up after execution.

    Args:
        - dir (str, optional): the _absolute_ path to a directory for storing
            all results; defaults to `$TMPDIR`
    """

    def __init__(self, dir: str = None):
        self.dir = dir

    def deserialize(self, fpath: str) -> Any:
        """
        Deserialize a result from the given file location.

        Args:
            - fpath (str): the _absolute_ path to the location of a serialized result

        Returns:
            - the deserialized result from the provided file
        """
        with open(fpath, "rb") as f:
            return cloudpickle.loads(f.read())

    def serialize(self, result: Any) -> str:
        """
        Serialize the provided result to local disk.

        Args:
            - result (Any): the result to serialize and store

        Returns:
            - str: the _absolute_ path to the serialized result on disk
        """
        fd, loc = tempfile.mkstemp(prefix="prefect-", dir=self.dir)
        with open(fd, "wb") as f:
            f.write(cloudpickle.dumps(result))
        return loc
