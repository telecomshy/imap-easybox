from pprint import pprint


def test_list_folders(mail_box):
    folders = str(mail_box.folders)
    assert 'Folder<inbox>' in folders
    assert 'Folder<草稿箱>' in folders
    assert 'Folder<垃圾邮件>' in folders


def test_create_folder(mail_box):
    mail_box.create_folder('测试文件夹')
    assert "Folder<测试文件夹>" in str(mail_box.folders)


def test_delete_folder(mail_box):
    mail_box.delete_folder('测试文件夹')
    assert "Folder<测试文件夹>" not in str(mail_box.folders)
