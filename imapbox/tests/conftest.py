import pytest
import imaplib
from imaplib import IMAP4_SSL
from imapbox import MailBox


class FakeImap(IMAP4_SSL):
    # def __init__(self, *args, **kwargs):
    #     ...

    def list(self, *args, **kwargs):
        return 'OK', [b'(\\Marked) "/" "INBOX"', b'(\\Marked) "/" "Drafts"', b'(\\Marked) "/" "&XfJT0ZAB-"']

    def _connect(self, *args, **kwargs):
        ...

    def shutdown(self, *args, **kwargs):
        ...

    def open(self, *args, **kwargs):
        ...


@pytest.fixture(scope='session')
def mail_box():
    box = MailBox('imap.fakeserver.com')
    box.server = FakeImap(box.host)
    box._get_folders_name()
    return box
