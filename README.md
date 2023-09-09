# Imap Box

## 简单介绍
imapbox是基于python内置imaplib，方便收取邮件，
读取邮件内容。 类似的三方包有[redbox](https://github.com/Miksus/red-box)，
[imap_tools](https://github.com/ikvk/imap_tools)，redbox对中文支持不太好，
imap_tools感觉稍微有点复杂。因为工作需要，顺便完整学习编写一个python包，因此写了
这样一个小工具。

## 安装

```shell
pip install imap-box
```

## 如何使用

### 基本例子

```python
from imapbox import ImapBox

box = ImapBox('imap.mail.com', port=993)  # 端口默认993

# 登录邮箱
box.login('username', 'password')

# 列出邮箱当前所有文件夹,返回[folder<'inbox'>, folder<'发件箱'>, ...]
folders = box.folders

# 选择inbox文件夹，返回Folder实例
# 也可以通过索引来选取文件夹，inbox = folders[0]，通过索引选取文件夹，会自动select到该文件夹
inbox_folder = box.select('inbox')

# 查看文件夹所有邮件,返回[mail<1>, mail<2>...]
mails = inbox_folder.mails

# 获取第一封邮件, 返回Mail对象实例
mail = mails[0]

# 获取邮件的相关属性
mail.subject              # 邮件主题
mail.from_                # 邮件来源
mail.sender               # 发件人
mail.to                   # 收件人
mail.text_body            # 邮件文本内容
mail.html_body            # 邮件html内容
mail.save_attachments()   # 保存邮件附件到本地
mail.move_to('垃圾箱')     # 将邮件移动到垃圾箱

box.quit()  # 退出邮箱
```
也可以在创建实例的时候传入用户名密码，登录的时候就不用再输入了：
```python
box = ImapBox('imap.mail.com', port=993, username='username', password='password')
box.login()
```
也支持上下文管理器:
```python
with ImapBox('imap.mail.com', username='username', password='password') as box:
    ...
```

### 文件夹操作

可以对文件夹进行新建，改名，删除的操作：
```python
box.create_folder('folder_name')                         # 创建文件夹
box.rename_folder('old_folder_name', 'new_folder_name')  # 重命名文件夹
box.delete_folder('folder_name')                         # 删除文件夹
```
除了可以在box实例上调用方法对文件夹进行操作，文件夹实例也提供了`rename`,`delete`方法，
不过没有`create`方法，因为个人感觉这有点违和，😂：
```python
inbox_folder.rename('new_folder_name')  # 重命名文件夹
inbox_folder.delete()                   # 删除该文件夹
```

### 操作邮件标签

可以对邮件标签进行操作，根据[RFC2060](https://datatracker.ietf.org/doc/html/rfc2060.html#section-6.4.4)，
目前支持6个标签的设置，分别是`Seen`, `Flagged`, `Answered`, `Draft`, `Deleted`, `Recent`，
所有标签操作不区分大小写：
```python
# 操作邮件标签
flags = mail.flags                          # 查看邮件当前标签,返回['Seen', 'Flagged', 'Answered', 'Draft', 'Deleted']
mail.add_flags('Seen')                      # 设置邮件为已读，可以是用逗号或者空格分隔的多个标签组成的字符串，也可以是列表
mail.set_flags('Flagged, Answered')         # 添加Flagged, Answered标签
mail.remove_flags(['Flagged', 'Answered'])  # 删除邮件标签
```

### 搜索邮件

---
`folder.mails`会返回文件夹内的所有邮件，但有时候我们想要搜索满足条件的某些邮件，
可以调用`folder.search`方法，`folder.search`支持通过关键字参数传递搜索条件，
也可以直接传入原生的(即内置库`imaplib`)搜索语句:
```python
# 使用关键字参数进行搜索
inbox_folder.search(subject='test')                         # 按主题搜索
inbox_folder.search(from_='imap.mail.com', seen=True)       # 按发件人和邮件标志搜索，from条件比较特殊，因为和python关键字冲突，所以后面要加一个下划线
inbox_folder.search(on='13-Aug-2023')                       # 按日期搜索，注意日期需要按照%d-%b-%Y的格式
```
可使用的所有条件可参考[RFC3501](https://www.rfc-editor.org/rfc/rfc3501#section-6.4.4),
不过是否生效还要看服务器是否支持。

所有flag标志和接收单个参数的条件都可以做为关键字参数，flag标志设置为`bool`值。所
有的关键字参数都是与(AND)的关系。如果需要是或(OR)，或者否(NOT)的关系，则只能使用
原生的搜索语句。[redbox](https://github.com/Miksus/red-box)和
[imap_tools](https://github.com/ikvk/imap_tools)都提供了特别
的搜索语句，但是实际上原生的搜索语句也不是很复杂，所以就偷个懒，没有再
费脑子了。原生搜索语句规则基本上就是，参数用双引号包含起来，整个搜索条件
用圆括号包含起来，如果没有参数，则直接上圆括号，下面是几个例子：
```python
inbox_folder.search('(SUBJECT "test")')
inbox_folder.search('((FROM "imap.mail.com") (SEEN))')    # 条件之间是与的关系
inbox_folder.search('(FROM "imap.mail.com") (SEEN)')      # 最外层的圆括号可要可不要
inbox_folder.search('OR (FROM "imap.mail.com") (SEEN)')   # 按或的关系进行搜索
inbox_folder.search('NOT (FROM "imap.mail.com") (SEEN)')  # 按否的关系进行搜索
```

## 作者

* **telecomshy** - [telcomshy](https://github.com/telecomshy) - telecomshy@126.com