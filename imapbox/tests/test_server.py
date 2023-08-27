from imapbox.folder import FoldList
import imaplib

# def fake_list():
#     return 'OK', [b'(\\Marked) "/" "INBOX"', b'(\\Marked) "/" "Drafts"', b'(\\Marked) "/" "&XfJT0ZAB-"']

def test_list_box_folders(mail_box):
    # monkeypatch.setattr(mail_box.server, 'list', fake_list)
    # mail_box._get_folders_name()
    print(mail_box.folders)
