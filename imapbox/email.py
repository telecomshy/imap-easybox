import email
from pathlib import Path
from datetime import datetime
from .utils import decode_mail_header, parse_raw_mail, image_to_base64


class Mail:
    def __init__(self, server, mail_id, folder):
        self.server = server
        self.mail_id = int(mail_id)
        self.folder = folder
        self._raw_mail = None
        self._content = None
        self._headers = None

    def __getattr__(self, item):
        return getattr(self.raw_mail, item)

    def _fetch(self, command):
        """根据指令获取邮件内容"""
        # imap fetch的第二个参数是用括号括起来的1个或者多个指令，比如(RFC822), (RFC822 FLAGS)
        # 返回的data是一个列表，元素个数和指令个数对应，比如(RFC822)返回的data包含一个元素，(RFC822 FLAGS)返回的data包含二个元素
        # 如果元素是一个元组，则元组的第二个元素是邮件实体
        typ, data = self.server.fetch(str(self.mail_id), command)

        if typ != 'OK':
            raise ConnectionError(f"Error with IMAP: {typ}")

        outputs = []

        for resp in data:
            if isinstance(resp, tuple):
                outputs.append(resp[1].decode("utf-8"))
            elif isinstance(resp, bytes):
                outputs.append(resp.decode("utf-8"))
            else:
                raise ValueError(f"Unknown how to handle response, type is {resp}")

        return outputs

    @property
    def content(self):
        """返回一个字典"""
        if self._content is None:
            self._content = parse_raw_mail(self.raw_mail)
        return self._content

    @property
    def raw_mail(self):
        """返回邮件原始内容，是email包的Message对象"""
        if self._raw_mail is None:
            data = self._fetch("(RFC822)")
            self._raw_mail = email.message_from_string(data[0])
        return self._raw_mail

    @property
    def headers(self):
        """获取邮件元信息"""
        if self._headers is None:
            self._headers = {k.lower(): v for k, v in self.raw_mail.items()}
        return self._headers

    def get_mail_meta(self, key):
        value = self.headers.get(key)
        if value:
            value = ''.join(decode_mail_header(value))
        return value

    @property
    def subject(self):
        return self.get_mail_meta("subject")

    @property
    def sender(self):
        return self.get_mail_meta("sender")

    @property
    def from_(self):
        return self.get_mail_meta("from")

    @property
    def to(self):
        return self.get_mail_meta("to")

    @property
    def date(self):
        d, b, y, t, z = self.headers["date"].split(',')[1].split()[:5]
        dt = datetime.strptime(f"{d} {b} {y} {t} {z}", "%d %b %Y %H:%M:%S %z")
        return dt.astimezone().strftime("%Y-%m-%d %H:%M:%S")

    @property
    def text_body(self):
        """获取邮件的文本内容"""
        return self.content.get("text_body")

    @property
    def html_body(self):
        """获取邮件html的内容"""
        return self.content.get("html_body")

    def save_html(self, save_path='.'):
        """保存邮件为html文件，图片编码成base64格式嵌入"""
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
    def attachments(self):
        """返回一个列表，元素是字典，字典的键是附件名称，值是附件二进制内容"""
        return self.content["attachments"]

    def save_attachments(self, save_path='.'):
        """保存所有附件，返回附件路径组成的列表"""
        save_path = Path(save_path)
        Path.mkdir(save_path, exist_ok=True)

        pathes = []

        for attachment in self.attachments:
            filepath = save_path / Path(attachment["filename"])
            filepath.write_bytes(attachment["content"])
            pathes.append(str(filepath))

        return pathes

    def __repr__(self):
        return f"Mail<{self.mail_id}>"
