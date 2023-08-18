import email
from collections import UserList
from .email import Mail


class FoldList(UserList):
    def __getitem__(self, item):
        val = super().__getitem__(item)
        if isinstance(val, Folder):
            val.server.select(val.folder_name)
        return val


class Folder:
    def __init__(self, server, folder_name):
        self.server = server
        self.folder_name = folder_name

    @property
    def mail_counts(self):
        mails = self.search(None, 'ALL')
        return len(mails) if mails else 0

    @property
    def mails(self):
        return self.search(None, 'ALL')

    def search(self, *args):
        typ, data = self.server.search(None, *args)
        mail_ids = data[0].decode('utf8').split(' ')
        if mail_ids == ['']:
            return []
        return [Mail(self.server, i, self) for i in mail_ids]

    def __repr__(self):
        return f"Folder<{self.folder_name}>"