.. imap easybox documentation master file, created by
   sphinx-quickstart on Mon Sep 11 21:50:45 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Imap EasyBox的文档
========================================

使用手册
-----------------

安装
+++++++++++++++++

.. code-block:: console

   pip install imap_easybox

基本操作
+++++++++++++++++

.. code-block:: python

   from imap_easybox import ImapEasyBox

   box = ImapEasyBox('imap.mail.com', port=993)  # 端口默认993

   # 登录邮箱
   box.login('username', 'password')

   # 列出邮箱当前所有文件夹,返回[folder<'inbox'>, folder<'发件箱'>, ...]
   folders = box.folders

   # 首先要通过box的select方法选择一个文件夹，返回Folder实例
   inbox_folder = box.select('inbox')
   # 也可以通过整数或者字符串索引返回文件夹，会自动select该文件夹
   inbox_folder = folders[0]
   inbox_folder = folders['inbox']

   # 查看文件夹所有邮件,返回[mail<1>, mail<2>...]
   mails = inbox_folder.mails

   # 获取第一封邮件, 返回Mail对象实例
   mail = mails[0]

   # 获取邮件的相关属性
   mail.subject             # 查看邮件主题
   mail.from_               # 查看邮件来源
   mail.sender              # 发件人
   mail.to                  # 收件人
   mail.text_body           # 邮件文本内容
   mail.html_body           # 邮件html内容
   mail.save_attachments()  # 保存邮件附件到本地
   mail.move_to('垃圾箱')    # 将邮件移动到垃圾箱

   box.quit()  # 退出邮箱

文件夹操作
+++++++++++++++++

可以对文件夹进行新建，改名，删除：

.. code-block:: python

   box.create_folder('folder_name')                         # 创建文件夹
   box.rename_folder('old_folder_name', 'new_folder_name')  # 重命名文件夹
   box.delete_folder('folder_name')                         # 删除文件夹

``Folder`` 实例也提供了 ``rename`` 和 ``delete`` 方法：

.. code-block:: python

   inbox_folder.rename('new_folder_name')  # 重命名文件夹
   inbox_folder.delete()                   # 删除该文件夹

API参考
-----------------

.. toctree::
   :maxdepth: 2

   api



