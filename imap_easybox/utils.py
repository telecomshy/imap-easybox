from email.message import Message
from email.header import decode_header
from pathlib import Path
from typing import Union
import base64


def decode_mail_header(header):
    """解析邮件元数据"""

    results = decode_header(header)
    values = []

    for val, encoding in results:
        if encoding is None:
            encoding = 'utf8'

        if isinstance(val, bytes):
            val = val.decode(encoding)

        values.append(val)

    return values


def parse_raw_mail(raw_mail: Message) -> dict:
    """递归解析原始邮件，返回邮件内容组成的字典:

    .. code-block:: python

        content = {
            "text_body": ...,
            "html_body": ...,
            "html_encoding": ...,
            "attachments": [...],
            "images": [...]
        }
    """

    content = {
        "text_body": None,
        "html_body": None,
        "html_encoding": None,
        "attachments": [],
        "images": []
    }

    def _parse(parts):
        content_type = parts.get_content_type()

        if content_type.startswith('multipart'):
            for part in parts.get_payload():
                _parse(part)
        elif content_type == 'text/plain':
            content['text_body'] = parts.get_payload(decode=True).decode(parts.get_content_charset())
        elif content_type == 'text/html':
            html_coding = parts.get_content_charset()
            content['html_body'] = parts.get_payload(decode=True).decode(html_coding)
            content['html_encoding'] = html_coding
        elif content_type.startswith('image'):
            filename = decode_mail_header(parts.get_filename())[0]
            content["images"].append({
                "filename": filename,
                "content_id": parts.get("Content-id")[1:-1],
                "content_type": parts.get_content_type(),
                "content": parts.get_payload(decode=True)
            })
        else:
            filename = decode_mail_header(parts.get_filename())[0]
            # 其它情况下，只可能为附件或者嵌入html页面内的元素，或者通过content_type是否为"application"开头来判断是否为附件
            if "attachment" in parts.get("Content-Disposition", []):
                content["attachments"].append({
                    "filename": filename,
                    "content": parts.get_payload(decode=True)
                })
            else:
                raise NotImplemented(f"Don't know how to deal with type: {content_type}")

    _parse(raw_mail)

    return content


def image_to_base64(image: Union[str, bytes], encoding) -> str:
    """
    将图片转换成base64编码

    Parameters
    ----------
    image: str or bytes
        字节码或者字符串，如果是字符串，表示图片的路径
    encoding: str
        字符串编码

    Returns
    -------
        base64编码的字符串
    """

    if isinstance(image, str):
        image = Path(image).read_bytes()
    image_base64 = base64.b64encode(image)
    image_base64 = image_base64.decode(encoding)
    return image_base64


def imap_utf7_encode(text: str) -> bytes:
    """将字符串转换成imap支持的utf7编码，并将+号替换成&号"""
    return text.encode('utf7').replace(b'+', b'&')


def imap_utf7_decode(bytes_: bytes) -> str:
    """将imap的字节编码转换成字符串，imap是utf7格式，并将+号替换成&号"""
    return bytes_.replace(b'&', b'+').decode('utf7')
