import email
import re
from email import generator
from pathlib import Path
from datetime import datetime
from typing import TYPE_CHECKING
from .utils import decode_mail_header, parse_raw_mail, image_to_base64

VALID_FLAGS = ['Seen', 'Flagged', 'Answered', 'Draft', 'Deleted', 'Recent']

if TYPE_CHECKING:
    from .folder import Folder


class Mail:
    def __init__(self, mail_id: int | str, folder: 'Folder'):
        self.folder = folder
        self.box = folder.box
        self.server = folder.server
        self.mail_id = str(mail_id)
        self._raw_mail = None
        self._content = None
        self._headers = None

    def __getattr__(self, item):
        return getattr(self.raw_mail, item)

    def _fetch(self, command):
        """根据指令获取邮件内容"""
        # imap fetch的第二个参数是用括号括起来的1个或者多个指令，比如(RFC822), (RFC822 FLAGS)
        # 返回的data是一个列表，如果列表元素是一个元组，则元组的第二个元素是邮件实体
        # 当指定的mail_id不正确的时候，返回的值为('OK', [None])
        typ, data = self.server.fetch(self.mail_id, command)

        outputs = []

        for resp in data:
            if isinstance(resp, tuple):
                outputs.append(resp[1].decode("utf-8"))
            if isinstance(resp, bytes):
                outputs.append(resp.decode("utf-8"))

        return outputs

    @property
    def content(self) -> dict:
        """返回邮件所有内容构成的字典，结构如下：

        .. code-block::

                content = {
                    "text_body": ...,
                    "html_body": ...,
                    "html_encoding": ...,
                    "attachments": [...],
                    "images": [...]
                }
        """
        if self._content is None:
            self._content = parse_raw_mail(self.raw_mail)
        return self._content

    @property
    def raw_mail(self) -> email.message.Message:
        """返回邮件原始的 :class:`~email.message.Message` 对象"""
        if self._raw_mail is None:
            data = self._fetch("(RFC822)")
            self._raw_mail = email.message_from_string(data[0])
        return self._raw_mail

    @property
    def headers(self) -> dict:
        """返回邮件元信息"""
        if self._headers is None:
            self._headers = {k.lower(): v for k, v in self.raw_mail.items()}
        return self._headers

    def _get_mail_info(self, key):
        """获取邮件头中指定的值"""
        value = self.headers.get(key)
        if value:
            value = ''.join(decode_mail_header(value))
        return value

    @property
    def subject(self) -> str:
        """返回邮件的主题"""
        return self._get_mail_info("subject")

    @property
    def sender(self) -> str:
        """返回邮件的发件人"""
        return self._get_mail_info("sender")

    @property
    def from_(self) -> str:
        """返回邮件发件人相关信息"""
        return self._get_mail_info("from")

    @property
    def to(self) -> str:
        """返回邮件收件人"""
        return self._get_mail_info("to")

    @property
    def date(self) -> str:
        """返回邮件发送日期，日期格式为 ``%Y-%m-%d %H:%M:%S``"""
        D = self.headers["date"]
        D = D if not "," in D else D.split(",")[1]  # weekday off
        d, b, y, t, z = D.split()[:5]
        if not z or not z[0] in {"-", "+"}:  # no tz offset in date
            z = "+0000"
        dt = datetime.strptime(f"{d} {b} {y} {t} {z}", "%d %b %Y %H:%M:%S %z")
        return dt.astimezone().strftime("%Y-%m-%d %H:%M:%S")

    @property
    def text_body(self) -> str:
        """返回邮件的文本内容"""
        return self.content.get("text_body")

    @property
    def html_body(self) -> str:
        """返回邮件html的内容"""
        return self.content.get("html_body")

    def save_html(self, save_path: str = '.'):
        """将邮件保存为html文件，图片编码成base64格式嵌入

        Parameters
        ----------
        save_path: str
            邮件保存目录
        """
        html_body = self.html_body

        if not html_body:
            raise ValueError("mail has no html body")

        save_path = Path(save_path)
        Path.mkdir(save_path, exist_ok=True)
        html_path = save_path / f'{self.mail_id}.html'

        for image in self.content["images"]:
            content_id = image['content_id']
            content_type = image['content_type']
            content = image_to_base64(image['content'], self.content['html_coding'])
            base64_image = f"data:{content_type};base64,{content}"
            html_body = html_body.replace(f"cid:{content_id}", base64_image)

        html_path.write_text(html_body, self.content["html_encoding"])

    @property
    def attachments(self) -> list:
        """返回一个列表，元素是字典，字典的键是附件名称，值是附件二进制内容"""
        return self.content["attachments"]

    def save_attachments(self, save_path: str = '.'):
        """保存所有附件，返回附件路径组成的列表

        Parameters
        ----------
        save_path: str, default '.'
            附件保存目录，默认为当前目录
        """
        save_path = Path(save_path)
        Path.mkdir(save_path, exist_ok=True)

        pathes = []

        for attachment in self.attachments:
            filepath = save_path / Path(attachment["filename"])
            filepath.write_bytes(attachment["content"])
            pathes.append(str(filepath))

        return pathes

    def save(self, filename: str = None):
        """将邮件保存为eml文件

        Parameters
        ----------
        filename: str, default None
            邮件名称
        """
        if filename is None:
            filename = f"{self.mail_id}.eml"

        filename = Path(filename)

        if filename.suffix != '.eml':
            raise ValueError("file suffix must be .eml")

        with open(filename, 'wt') as eml:
            gen = generator.Generator(eml)
            gen.flatten(self.raw_mail)

    @property
    def flags(self) -> list[str]:
        """返回邮件当前所有flag标志构成的列表"""
        # self._fetch('FLAGS')的结果为['1 (FLAGS (\\Seen \\Flagged))']或者['1 (FLAGS ())']
        # 转换成'1 FLAGS \\Seen \\Flagged'或者'1 FLAG  '
        flags = self._fetch('FLAGS')[0].replace('(', '').replace(')', '').replace('\\', '')
        # split不加参数会去掉结果中包含的''
        flags = flags.split()[2:]
        return flags

    # 把flag设置为mail的特性容易和text_body等属性造成混淆，所以统一通过add_flags,set_flags,remove_flags来设置标志
    def _store_flags(self, command: str, flags: str):
        """设置邮件标志通用方法"""
        try:
            flags = re.split(r',|\s+', flags)
        except TypeError:
            pass

        flags = [flag.capitalize() for flag in flags]

        for flag in flags:
            if flag not in VALID_FLAGS:
                raise ValueError(f'{flag} is not a valid flag.')

        flags = ' '.join([rf'\{flag}' for flag in flags])
        self.server.store(self.mail_id, command, flags)

    def set_flags(self, flags: list | str):
        """设置邮件标识，可用标识有seen, flagged, answered, draft, deleted

        Parameters
        ----------
        flags: list or str
            设置邮件flag标志，可以是标记构成的列表，或者多个标记组成的字符串，标志之间用逗号或空格分隔
        """
        self._store_flags('FLAGS', flags)

    def add_flags(self, flags: list | str):
        """添加邮件标识，可用标识有seen, flagged, answered, draft, deleted

        Parameters
        ----------
        flags: list or str
            设置邮件flag标志，可以是标记构成的列表，或者多个标记组成的字符串，标志之间用逗号或空格分隔
        """
        self._store_flags('+FLAGS', flags)

    def remove_flags(self, flags: list | str):
        """删除邮件标识，可用标识有seen, flagged, answered, draft, deleted

        Parameters
        ----------
        flags: list or str
            设置邮件flag标志，可以是标记构成的列表，或者多个标记组成的字符串，标志之间用逗号或空格分隔
        """
        self._store_flags('-FLAGS', flags)

    def move_to(self, folder_name):
        """将邮件移动到指定文件夹

        Parameters
        ----------
        folder_name: str
            目的文件夹名称
        """
        self.server.copy(self.mail_id, self.box._folders[folder_name])
        self.add_flags('deleted')

    def __repr__(self):
        return f"Mail<{self.mail_id}>"
