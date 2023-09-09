from collections import UserList
from typing import TYPE_CHECKING
from .email import Mail

if TYPE_CHECKING:
    from .server import ImapEasyBox


class FoldList(UserList):
    def __getitem__(self, item):
        val = super().__getitem__(item)
        if isinstance(val, Folder):
            val.server.select(val.folder_name)
        return val


class Folder:
    def __init__(self, folder_name: str, box: 'ImapEasyBox'):
        self.box = box
        self.server = box.server
        self.folder_name = folder_name

    @property
    def mails(self):
        return self.search('ALL')

    def search(self, query=None, *, encoding=None, **kwargs):
        """根据条件搜索邮件"""
        if query is None:
            query = self._format_search_query(kwargs)

        if encoding:
            query = query.encode(encoding)

        typ, data = self.server.search(encoding, query)

        if typ != 'OK':
            raise RuntimeError(data[0].decode("ascii"))

        mail_ids = data[0].decode('ascii').split()
        return [Mail(i, self) for i in mail_ids]

    @staticmethod
    def _format_search_query(kwargs):
        """根据传入search方法的关键字参数构造原生的搜索条件字符串"""
        criteria = []

        for field, value in kwargs.items():
            field = field.rstrip('_').upper()

            if isinstance(value, str):
                criteria.append(f"({field} {value})")

            if isinstance(value, bool):
                if value:
                    criteria.append(f"({field})")
                else:
                    criteria.append(f"(NOT {field})")

        query = f"({' '.join(criteria)})"
        return query

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
