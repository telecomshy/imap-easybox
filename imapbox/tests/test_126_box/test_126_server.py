from pprint import pprint


def test_list_folders(mail_box):
    folders = str(mail_box.folders)
    assert 'Folder<inbox>' in folders
    assert 'Folder<草稿箱>' in folders
    assert 'Folder<垃圾邮件>' in folders


def test_create_folder(mail_box):
    test_folder = mail_box.create_folder('test_folder')
    assert test_folder.folder_name == 'test_folder'
    assert "Folder<test_folder>" in str(mail_box.folders)


def test_fetch_mail(mail_box):
    inbox = mail_box.select('inbox')
    print(inbox.mails)
    mail1 = inbox.mails[0]
    mail1.set_flags('seen draft')
    print(mail1.flags)

