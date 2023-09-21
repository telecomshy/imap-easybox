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

    def test_select_folder_by_item(self, mail_box):
        folders = mail_box.folders
        draft_folder = folders[1]
        assert draft_folder.folder_name == '草稿箱'
        assert mail_box.state == 'SELECTED'
        send_folder = folders["已发送"]
        assert send_folder.folder_name == '已发送'
        assert mail_box.state == 'SELECTED'


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
        assert test_folder.folder_name is None

    def test_search_mail_by_keyword(self, mail_box):
        inbox = mail_box.select('inbox')
        mails = inbox.search(subject="new")
        assert "new" in mails[0].subject

    def test_search_mail_by_raw_str(self, mail_box):
        inbox = mail_box.select('inbox')
        mails = inbox.search('(SUBJECT "new")')
        assert "new" in mails[0].subject


class TestMail:

    def test_add_flag(self, inbox):
        mail = inbox.mails[0]
        mail.add_flags(['Flagged', 'Answered'])
        assert 'Flagged' in mail.flags and 'Answered' in mail.flags
