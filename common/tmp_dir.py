import os
import pathlib
from datetime import datetime

from config import conf


class TmpDir(object):
    """A temporary directory that is deleted when the object is destroyed."""

    tmpFilePath = pathlib.Path("./tmp/")

    def __init__(self, group_name=None):
        if group_name:
            current_date_str = datetime.today().strftime("%Y-%m-%d")
            self.tmpFilePath = pathlib.Path(f"./tmp/{group_name}/{current_date_str}/")
        pathExists = os.path.exists(self.tmpFilePath)
        if not pathExists:
            os.makedirs(self.tmpFilePath)

    def path(self):

        return str(self.tmpFilePath) + "/"
