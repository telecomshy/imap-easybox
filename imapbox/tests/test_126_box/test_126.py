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
        assert mail_box.server.state == 'AUTH'
        mail_box.select('inbox')
        assert mail_box.server.state == 'SELECTED'
