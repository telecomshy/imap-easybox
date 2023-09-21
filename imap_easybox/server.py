import imaplib
from typing import Union
from .folder import Folder, FolderList
from .utils import imap_utf7_encode, imap_utf7_decode


class ImapEasyBox:
    """登录imap服务器，对邮箱内的文件夹进行操作

    Parameters
    ----------
    host : str
        服务器域名
    port : int, default 993
        服务器端口，默认为993
    user: str, default None
        用户名，也可以稍后在调用 ``login`` 方法时指定
    password: str, default None
        密码，也可以稍后在调用 ``login`` 方法时指定
    ssl: bool, default True
        为 ``True``, 则内部使用 :class:`imaplib.IMAP4`，否则使用 :class:`imaplib.IMAP4_SSL` 创建实例
    kwargs:
        任意关键字参数，会透传给 :class:`imaplib.IMAP4` 或 :class:`imaplib.IMAP4_SSL` 构造函数

    Examples
    ----------
    可以传入用户名，密码，登录时候无须再次输入

    >>> box = ImapEasyBox(host='mail.imap.com', port=993, user='username', password='password')
    >>> box.login()

    也可以延迟输入用户名密码:

    >>> box = ImapEasyBox(host='mail.imap.com', port=993)
    >>> box.login(user='username', password='password')

    调用 ``quit`` 方法退出:

    >>> box.quit()

    可以使用上下文管理器:

    >>> with ImapEasyBox(host='mail.imap.com', port=993, user='username', password='password') as box:
    ...     pass

    """
    server: Union[imaplib.IMAP4, imaplib.IMAP4_SSL, None]

    def __init__(self, host: str, port=993, user: str | None = None, password: str | None = None, ssl: bool = True,
                 **kwargs):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.imap_cls = getattr(imaplib, 'IMAP4_SSL') if ssl else getattr(imaplib, 'IMAP4')
        self.server = None
        self.kwargs = kwargs
        # self._folders是邮箱中文名和原始名称构成的字典
        self._folders = None

    def login(self, user: str | None = None, password: str | None = None):
        """登陆邮箱

        Parameters
        ----------
        user: str, default None
            用户名，如果已指定，则可忽略
        password: str, default None
            密码，如果已指定，则可忽略

        """
        if user is None:
            user = self.user
        if password is None:
            password = self.password

        self.server = self.imap_cls(self.host, self.port, **self.kwargs)
        # 登录成果返回('OK', [b'LOGIN completed'])
        # 用户名密码错误抛出异常imaplib.IMAP4.error: b'LOGIN failure, invalid username/password'
        # 邮箱地址错误抛出异常imaplib.IMAP4.error: LOGIN command error: BAD [b'LOGIN failure, domain is disable.']
        self.server.login(user, password)
        self._update_folders()

    def quit(self):
        """退出登录"""
        # 需要先选择select邮箱，然后再close，否则会抛出错误
        try:
            self.server.close()
        except imaplib.IMAP4.error:
            pass

        self.server.logout()

    def __getattr__(self, item: str):
        return getattr(self.server, item)

    def __enter__(self):
        self.login(self.user, self.password)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.quit()

    def select(self, folder_name: str) -> Folder:
        """选择文件夹

        登录以后，必须先选择一个文件夹

        Parameters
        ----------
        folder_name: str
            文件夹名称

        Returns
        -------
        Folder
            返回一个 :class:`Folder` 实例
        """
        folder_raw_name = self._folders[folder_name.lower()]
        self.server.select(folder_raw_name)
        return Folder(folder_name, self)

    @property
    def folders(self) -> FolderList:
        """FolderList: 返回邮箱当前所有文件夹

        Examples
        ---------

        >>> folders = box.folders
        >>> folders
        [Folder<inbox>, Folder<垃圾箱>, ...]

        返回 :class:`.FolderList` 实例，:class:`.FolderList` 可通过整数或者文件夹名称选择文件夹
        """
        return FolderList(Folder(folder_name, self) for folder_name in self._folders.keys())

    def _update_folders(self):
        """更新文件夹列表

        获取当前所有文件夹，构成一个字典，键是解析后的文件夹名称，值是文件夹的原始名称，保存到 ``_folders`` 属性中

        """
        self._folders = {}

        # list返回的结果是('OK', [b'(\\Marked) "/" "INBOX"', b'(\\Marked) "/" "&XfJT0ZAB-"'])
        typ, data = self.server.list()

        # 结果中类似&XfJT0ZAB-的字符串是utf7编码，并且把+号替换回&符号
        for folder_byte in data:
            folder_name_byte = folder_byte.split(b' ')[-1].replace(b'"', b'')
            folder_name_key = imap_utf7_decode(folder_name_byte).lower()
            folder_name_val = folder_name_byte.decode('ascii')
            self._folders[folder_name_key] = folder_name_val

    def create_folder(self, folder_name: str):
        """创建文件夹，创建成功更新邮箱所有文件夹"""
        # 创建已存在的文件夹返回('NO', [b'CREATE Folder exist']
        folder_name = imap_utf7_encode(folder_name)
        self.server.create(folder_name)
        self._update_folders()

    def rename_folder(self, old_folder_name: str, new_folder_name: str):
        """修改指定文件夹名称，修改成功更新邮箱所有文件夹"""
        try:
            old_folder_name = self._folders[old_folder_name.lower()]
        except KeyError:
            raise NameError(f"Folder<{old_folder_name}>不存在")

        new_folder_name = imap_utf7_encode(new_folder_name).decode('ascii')
        self.server.rename(old_folder_name, new_folder_name)
        self._update_folders()

    def delete_folder(self, folder_name: str):
        """删除指定文件夹，删除成功更新邮箱所有文件夹"""
        # 删除不存在的文件夹会返回('NO', [b'DELETE Folder not exist'])
        try:
            folder_name = self._folders[folder_name.lower()]
        except KeyError:
            raise NameError(f"Folder<{folder_name}>不存在")

        self.server.delete(folder_name)
        self._update_folders()
