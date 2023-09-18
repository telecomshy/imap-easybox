📕 使用手册
=================

安装
-----------------

.. code-block:: console

   pip install imap_easybox

基本操作
-----------------

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
-----------------

可以对文件夹进行新建，改名，删除：

.. code-block:: python

   box.create_folder('folder_name')                         # 创建文件夹
   box.rename_folder('old_folder_name', 'new_folder_name')  # 重命名文件夹
   box.delete_folder('folder_name')                         # 删除文件夹

``Folder`` 实例也提供了 :py:meth:`~imap_easybox.folder.Folder.rename` 和 :py:meth:`~imap_easybox.folder.Folder.delete`
方法，不要问为什么没有 ``create`` 方法，因为觉得不合适，😊：

.. code-block:: python

   inbox_folder.rename('new_folder_name')  # 重命名文件夹
   inbox_folder.delete()                   # 删除该文件夹

邮件标志操作
-------------------------

所谓标志，就是比如什么已读，已删除之类的标记，根据 `RFC2060 <https://datatracker.ietf.org/doc/html/rfc2060.html#section-6.4.4>`_，
目前支持6个标签的设置，分别是 ``Seen``, ``Flagged``, ``Answered``, ``Draft``, ``Deleted``, ``Recent``，

所有方法中的参数不区分大小写：

.. code-block:: python

    # 参数可以是逗号或空格分隔的多个标签组成的字符串，也可以是列表
    flags = mail.flags                          # 查看邮件当前标签,返回['Seen', 'Flagged', ...]
    mail.add_flags('Seen')                      # 添加已读标签
    mail.set_flags('Flagged, Answered')         # 设置邮件标签为已标记和已回复，已有标记会被清除
    mail.remove_flags(['Flagged', 'Answered'])  # 删除邮件的已标记和已回复标记

搜索邮件
---------------

``Folder`` 实例的 :py:attr:`~imap_easybox.folder.Folder.mails` 特性会返回文件夹内的所有邮件，但有时候我们想要根据条件搜索邮件，可以调
用 ``Folder`` 实例的 :py:meth:`~imap_easybox.folder.Folder.search` 方法，返回 :py:class:`~imap_easybox.email.Mail` 实例构成的
列表。 :py:meth:`~imap_easybox.folder.Folder.search` 方法可以通过关键字参数传递搜索条件，也可以直接传入原生的（即传
入 :py:class:`imaplib.IMAP4` 的 :py:meth:`~imaplib.IMAP4.search` 方法）搜索字符串，所有条件可参考
`RFC3501 <https://www.rfc-editor.org/rfc/rfc3501#section-6.4.4>`_, 不过是否生效还要看服务器是否支持。

**关键字参数**

.. code-block:: python

    # 按主题搜索
    mails = inbox_folder.search(subject='test')
    # 按发件人和邮件标志搜索，from条件比较特殊，因为和python关键字冲突，所以后面要加一个下划线
    mails = inbox_folder.search(from_='imap.mail.com', seen=True)
    # 按日期搜索，注意日期需要按照%d-%b-%Y的格式
    mails = inbox_folder.search(on='13-Aug-2023')

所有 `Flag` 标志和接收单个参数的条件都可以做为关键字参数，`Flag` 标志设置为 `bool` 值。多个关键字参数是 `AND` 的关系。
如果需要 `OR`，或者 `NOT` 的关系，则只能使用原生的搜索字符串。

**原生字符串**
