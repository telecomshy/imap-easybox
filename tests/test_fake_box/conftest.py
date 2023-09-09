import pytest
from imaplib import IMAP4_SSL
from imap_easybox import ImapEasyBox


class FakeImap(IMAP4_SSL):

    def list(self, *args, **kwargs):
        return 'OK', [b'(\\Marked) "/" "INBOX"', b'(\\Marked) "/" "Drafts"', b'(\\Marked) "/" "&XfJT0ZAB-"']

    def _connect(self, *args, **kwargs):
        ...

    def shutdown(self, *args, **kwargs):
        ...

    def open(self, *args, **kwargs):
        ...

    def login(self, *args, **kwargs):
        return 'OK', [b'LOGIN completed']

    def logout(self, *args, **kwargs):
        ...


@pytest.fixture(scope='session')
def fake_box():
    box = ImapEasyBox('imap.fakeserver.com')
    box.imap_cls = FakeImap
    box.login()
    yield box
    box.quit()
