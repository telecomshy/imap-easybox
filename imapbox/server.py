import imaplib
from .folder import Folder, FoldList


class MailBox:
    def __init__(self, host, port=993, user=None, password=None, ssl=True, **kwargs):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.imap_cls = getattr(imaplib, 'IMAP4_SSL') if ssl else getattr(imaplib, 'IMAP4')
        self.server = None
        self.kwargs = kwargs
        self._folders = {}

    def login(self, user=None, password=None):
        """登陆并获取所有文件夹名称"""

        if user is None:
            user = self.user
        if password is None:
            password = self.password

        self.server = self.imap_cls(self.host, self.port, **self.kwargs)
        # 登录成果返回('OK', [b'LOGIN completed'])
        # 用户名密码错误抛出异常imaplib.IMAP4.error: b'LOGIN failure, invalid username/password'
        # 邮箱地址错误抛出异常imaplib.IMAP4.error: LOGIN command error: BAD [b'LOGIN failure, domain is disable.']
        self.server.login(user, password)
        self._get_folders_name()

    def quit(self):
        self.server.close()
        self.server.logout()

    def __getattr__(self, item):
        return getattr(self.server, item)

    def __enter__(self):
        self.login(self.user, self.password)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            # 需要先选择select邮箱，然后再close，否则会抛出错误
            self.quit()
        except Exception:
            pass

    def select(self, folder_name: str):
        folder_raw_name = self._folders[folder_name.lower()]
        self.server.select(folder_raw_name)
        return Folder(self.server, folder_name)

    @property
    def folders(self):
        return FoldList(Folder(self.server, folder_name) for folder_name in self._folders.keys())

    def _get_folders_name(self):
        # list返回的结果是('OK', [b'(\\Marked) "/" "INBOX"', b'(\\Marked) "/" "&XfJT0ZAB-"'])
        resp, data = self.server.list()

        # 结果中类似&XfJT0ZAB-的字符串是utf7编码，并且把+号替换回&符号
        for folder_byte in data:
            folder_name_byte = folder_byte.split(b' ')[-1].replace(b'"', b'')
            folder_key = folder_name_byte.replace(b"&", b"+").decode('utf7').lower()
            folder_val = folder_name_byte.decode('ascii')
            self._folders[folder_key] = folder_val


