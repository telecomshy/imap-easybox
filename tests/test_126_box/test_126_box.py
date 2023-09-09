import pytest


class TestServer:
    def test_list_folders(self, mail_box):
        folders = str(mail_box.folders)
        assert 'Folder<inbox>' in folders
        assert 'Folder<草稿箱>' in folders
        assert 'Folder<垃圾邮件>' in folders

    def test_create_folder(self, mail_box):
        mail_box.create_folder('测试文件夹')
        assert "Folder<测试文件夹>" in str(mail_box.folders)

    def test_rename_folder(self, mail_box):
        mail_box.rename_folder('测试文件夹', '新测试文件夹')
        assert "Folder<新测试文件夹>" in str(mail_box.folders)

    def test_delete_folder(self, mail_box):
        mail_box.delete_folder('新测试文件夹')
        assert "Folder<新测试文件夹>" not in str(mail_box.folders)

    def test_select_folder(self, mail_box):
        assert mail_box.state == 'AUTH'
        inbox = mail_box.select('inbox')
        assert mail_box.state == 'SELECTED'
        assert inbox.folder_name == 'inbox'


class TestFolder:
    def test_rename_folder(self, mail_box):
        mail_box.create_folder('测试文件夹')
        test_folder = mail_box.select('测试文件夹')
        test_folder.rename('新测试文件夹')
        assert test_folder.folder_name == '新测试文件夹'
        assert "Folder<新测试文件夹>" in str(mail_box.folders)

    def test_delete_folder(self, mail_box):
        test_folder = mail_box.select('新测试文件夹')
        test_folder.delete()
        assert "Folder<新测试文件夹>" not in str(mail_box.folders)
        with pytest.raises(RuntimeError):
            mails = test_folder.mails

    def test_search_mail(self, mail_box):
        inbox = mail_box.select('inbox')
        print(inbox.mails)
        # mails = inbox.search(subject="new")
        # assert len(mails) == 1
        mails = inbox.search('(NOT (SUBJECT "new"))')
        print(mails)


class TestMail:

    def test_add_flag(self, inbox):
        mail = inbox.mails[0]
        print(mail.flags)
        mail.add_flags(['Flagged', 'Answered'])
        print(mail.flags)
