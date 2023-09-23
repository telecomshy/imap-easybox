from collections import UserList
from typing import TYPE_CHECKING
from .email import Mail

if TYPE_CHECKING:
    from .server import ImapEasyBox


class FolderList(UserList):
    """
    覆盖了 :class:`collections.UserList` 的 ``__getitem__`` 方法，可通过整数或者文件夹名称选择文件夹，在内部会调用
    :meth:`.ImapEasyBox.select` 方法选定该文件夹

    Examples
    ----------

    >>> folders
    [Folder<inbox>, Folder<垃圾箱>, ...]
    >>> inbox = folders[0]
    >>> inbox
    Folder<inbox>
    >>> inbox = folders['inbox']
    >>> inbox
    Folder<inbox>

    """

    def __getitem__(self, item):
        if isinstance(item, str):
            for folder in self:
                if item == folder.folder_name:
                    val = folder
                    break
            else:
                raise KeyError(item)
        else:
            val = super().__getitem__(item)

        if isinstance(val, Folder):
            val.box.select(val.folder_name)
        return val


class Folder:
    """对应邮箱中的文件夹"""

    def __init__(self, folder_name: str, box: 'ImapEasyBox'):
        self.box = box
        self.server = box.server
        self.folder_name = folder_name

    @property
    def mails(self) -> list[Mail]:
        """返回当前文件夹中所有邮件"""

        return self.search('ALL')

    def search(self, query: str = None, *, encoding: str = None, **kwargs) -> list[Mail]:
        """
        根据条件搜索邮件，具体例子参考 :ref:`tutorial:搜索邮件`

        Parameters
        ----------
        query: str, default None
            原生搜索字符串，具体查看 :ref:`按原生字符串搜索 <raw search string>`
        encoding: str, default None
            注意，如果搜索条件包含中文，需要指定编码。是否支持该编码依赖于服务器支持
        **kwargs:
            按关键字搜索，支持的关键字参考 `RFC3501 <https://www.rfc-editor.org/rfc/rfc3501#section-6.4.4>`_, 不区分大小写。
            条件之间是与的关系，如果是或，否的关系，请使用原生搜索字符串。

        Returns
        -------
            返回 :class:`.Mail` 对象组成的列表

        """
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

    def rename(self, folder_name: str):
        """更改当前文件夹名称

        Parameters
        ----------
        folder_name: str
            新的文件夹名称
        """
        self.box.rename_folder(self.folder_name, folder_name)
        self.folder_name = folder_name
        self.box.update_folders()

    def delete(self):
        """删除当前文件夹

        删除以后，实例的 ``folder_name``, ``box``, ``server`` 属性都被设置为 ``None``。
        """
        self.box.delete_folder(self.folder_name)
        self.folder_name = None
        self.box = None
        self.server = None

    def __repr__(self):
        return f"Folder<{self.folder_name}>"
