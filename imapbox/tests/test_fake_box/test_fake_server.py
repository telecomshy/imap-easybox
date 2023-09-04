def test_list_box_folders(fake_box):
    assert str(fake_box.folders) == "[Folder<inbox>, Folder<drafts>, Folder<已发送>]"

