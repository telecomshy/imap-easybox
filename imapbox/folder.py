from collections import UserList
from typing import TYPE_CHECKING
from .email import Mail

if TYPE_CHECKING:
    from .server import ImapBox


class FoldList(UserList):
    def __getitem__(self, item):
        val = super().__getitem__(item)
        if isinstance(val, Folder):
            val.server.select(val.folder_name)
        return val


class Folder:
    def __init__(self, folder_name: str, box: 'ImapBox'):
        self.box = box
        self.server = box.server
        self.folder_name = folder_name

    @property
    def mails(self):
        return self.search(None, 'ALL')

    def search(self, *args, encoding=None):
        typ, data = self.server.search(encoding, *args)

        if typ != 'OK':
            raise RuntimeError(data[0].decode("ascii"))

        mail_ids = data[0].decode('ascii').split()
        return [Mail(i, self) for i in mail_ids]

    def rename(self, folder_name):
        """更改文件夹名称"""
        self.box.rename_folder(self.folder_name, folder_name)
        self.folder_name = folder_name

    def delete(self):
        """删除文件夹"""
        self.box.delete_folder(self.folder_name)
        self.folder_name = None
        self.box = None
        self.server = None

    def __repr__(self):
        return f"Folder<{self.folder_name}>"
