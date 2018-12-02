# email-api
## mail http protocol
### note
    (1) 参数的值是结构体时，先转为字符串 JSON.strinfify
    (2) 以下描述0代表整型，""代表字符串
    (3) 一般地，返回值status=0表示成功，其他表示失败
    (4) 部分操作，会由于服务器延迟，不会同步到最新内容，例如发送邮件后，拉取到的最近已发送邮件
        可能不包含该邮件，需要重新拉取
    (5) 本地服务器是非阻塞的，可使用轮询的方法，同步新邮件状态

协议结构体
### mail_server_setting
    {
        "id":"",
        "host":"",
        "type":"POP3,IMap,Exchage", # 暂时只支持imap4
        "imap_server_host":"",  # 必填
        "imap_server_port":0,   # default 143
        "smtp_server_host":"",  # 必填
        "smtp_server_port":0,   # default 25
        "enable_smtp_server_ssl":0,
        "enable_starttls": 0,
        "exchange_server":""
    }

## 1.mail server setting
### get mail server setting request
    http://127.0.0.1:port/setting/get_setting_list
#### response:
    {"status":0, "data":[mail_server_setting], "count": 0, "errmsg":""}

### add mail server setting request
    http://127.0.0.1:port/setting/add_setting
#### data:
    {"setting":mail_server_setting}
    (1) 不能包含'id'字段，必须包含imap_server_host与smtp_server_host字段
    (2) transform mail_server_setting to string
#### response:
    {"status":0, "id":"", "errmsg":""}

### edit mail server setting request
    http://127.0.0.1:port/setting/edit_setting
#### data:
    {"setting":mail_server_setting}
    (1) 必须包含'id'字段
#### response:
    {"status":"", "id":"", "errmsg":""}

### delete mail setting request
    http://127.0.0.1:port/setting/del_setting
#### data:
    {"id": 0}
#### response:
    {"result":0, "msg":"", "errmsg":""}

## 2.mail auth
### login request
    http://127.0.0.1:port/auth/login
#### data:
    (1) 初次登录：{"mail_account_name":"abc@123.com", "mail_account_psd":"", "mail_setting_id": 0}
        登录成功后，账号信息保存到数据库
    (2) 断线后，使用原密码重新登录：{"mail_account_name": "", "relogin": 1}
    (3) 断线后，手输密码重新登录，参数与初始登录一致，登录成功后，新密码会更新到数据库
#### response:
    {"status":0, "id":0, "errmsg":""}

### get logined account request
    http://127.0.0.1:port/auth/logined_account
#### data:
    不用传参
#### response
    {"status":0, "errmsg", "result": [{"status": 0， "id": 0, "account_name": ""}...]}
#### note
    一般地，启动程序后，首先调用该接口，尝试将数据库记录的账户登录到远程server, response-result表示各个账号的登录结果

### logout request
    由于实现了断线自动重连功能，登出功能不实现

## 3.mail content
    以下接口都必须传参{"mail_account_name": ""}

### get mail box list
    http://127.0.0.1:port/mail/get_mail_box_list
#### data:
#### response:
    {"status": 0, "data":{box_info}, "errmsg": ""}
#### note:
    "data"是邮箱名与对应的信息的键值对，例如：
    "data": {"INBOX": {"EXISTS": 123, "UNSEEN": 12, "RECENT": 0, ...}, "Sent Messages": {...}}
    邮箱名非常重要，大部分接口将胜；邮箱信息字段对应的意义请参考imap相关文档

### get remote mail list request
    从远程服务器拉取邮件，并同步到本地数据库
    http://127.0.0.1:port/mail/get_remote_mail_list
#### data:
    {"mailbox": "INBOX", "start": 0, "end": 0, "use_uid": 1}
#### response:
    {"status":0, "count":0; "data":[header_info], "errmsg": ""}
#### note:
    (1) start, end, use_uid都是可选参数
    (2) use_uid为0时，使用序号拉取邮件信息，否则使用uid，默认为1
    (3) start与end都为空时，拉取最近的1封邮件（不同邮箱表现不一，有的可以拉到最近1封，有的返回空）
    (4) start为空，end非空，则从开始拉到end为止（包含end指向的邮件）
    (5) start不为空, end为空，则从start开始拉取到最新的邮件
    (6) start与end都不为空，则由start拉取到end
    (7) 拉取到邮件头后，立即返回结果，然后后台将邮件头写入数据库，并且静默拉取邮件内容写入数据库，后台操作不会阻塞服务器响应客户端新的请求
    (8) 当拉取范围过大时，建议分批拉取，否则会耗时较多才返回结果（等待返回结果时，不会阻塞服务器）；
        例如初始拉取时，若数量（邮箱信息的EXISTS字段）过大，可以设置end=EXISTS,start=EXISTS-n,use_uid=0，来拉取n条信息，由此类推，逐批拉取
    (9) header_info包括[message-id, uid, subject, to, cc, bcc, from, data]等字段
    (10)结果逆序排序，最新的在前面

### get local mail list
    从本地数据库拉取邮件
    http://127.0.0.1:port/mail/get_local_mail_list
#### data:
    {"mailbox": "", "count": 0, "offset": 0}
    or
    {"mailbox": "", "start": 0, "end": 0}
#### response:
    同 remote mail list
#### note:
    两种参数方式以第一种优先（当参数包含count并且不为0），第一种方式offset可空，默认0；第二种方式start与end都可空，同为空则拉取全部

### get mail content request:
    http://127.0.0.1:port/mail/get_mail_content
#### data:
    {"message_uid": "", "mailbox": ""}
#### response:
    {"result":0, "id":"", "content":[mail_content], "errmsg":""}
#### note:
    (1) mail_content {'UID': "", "RFC822": ""}, "RFC822"是MIME格式的字符串，可解析出邮件的各项信息
    (2) 优先从本地数据库获取邮件内容，若无则从远程服务器拉取，并同步到本地数据库

## 4.mail operator
#### tag mail request
    http://127.0.0.1:port/mail/tag"
#### data
    {"message_uid": "", "mailbox": "", "op":"read/unread/trash/del"}
#### response:
    {"result":0, "errmsg":""}
#### note:
    (1) 各操作会同步远程服务器（若设置为同步许可）与本地数据库
    (2) 若操作为trash，会将邮件移到回收站（Deleted Messages)，并从远程服务器拉取新的Deleted Messages写入response
    (3) del为永久删除操作，注意与trash区分

    
## 5.send mail
### send mail request
    http://127.0.0.1:port/mail/send_mail
#### data:
    {"mime":{mail_content}}
#### response:
    {"result":0, "data":[new_msg_in_sent_box], "errmsg":""}
#### note:
    {
        'headers': {
            'Subject': 'hello world',
            'To': '1<a@a.com>, 2<b@b.com>,...',
            'From': 'hei <h@h.com>',
            'Cc': ...,
            'Bcc': ...
        },
        'receivers': [a@a.com, b@b.com,...],
        'parts': [
            {
                'type': 'plain',
                'content': '老板明天带我们去happy咯\r\n\r\n'
            },
            {
                 'type': 'html',
                 'content': '<div><a href="https://www.qq.com">腾讯</a></div><br>'
            },
            {
                 'type': 'attachment',
                 'file_path': '/Users/name/Documents/1.txt',
                 'filename': '1.txt'
            },
            {
                 'type': 'attachment',
                 'file_path': '/Users/name/Documents/2.txt',
                 'filename': '2.txt'
            },
            {
                 'type': 'html-img',
                 'content': '<br><img src="cid:image1"><br><br>'
            },
            {
                 'type': 'img',
                 'img_path': '/Users/name/Downloads/a.png',
                 'img_cid': 'image1'
            }
        ],
        'mode': 'single'
    }
    (1) mime的形式大约如上所示, remember JSON.stringify
    (2) parts中的type，html与html-img冲突，当包含内嵌图片时选择html-img，否则可选择html
    (3) 当使用html-img时，html-img part中content的<img>cid与img part的img_cid对应，如有多个<img>标签，
        则要有相应的img part
    (4) attachment part可以有多个
    (5) attachment part与img part的路径都使用文件的全路径，不需要传文件内容（减小跨进取传输的内容），
        本地服务器会根据路径读取内容并传送
    (6) 若传入参数mode，且设置为single，且收件人多于1个，则会启用"群发单显"功能
    (7) 发送成功后，则会从远程服务器拉取最近已发送文件，并写入response与同步到本地数据库

# install
    运行 python install.py会检查需要的库文件，并创建新的数据库
    运行 python main.py，则启动本地服务器进程

# config
    (1) conf/provider.json配置初始的邮件服务提供商(mail_setting)

# license
