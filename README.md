# email-api
## mail http protocol

协议结构体
### mail_server_setting
    {
        "id":"",
        "host":"",
        "type":"POP3,IMap,Exchage",
        "send_server_host":"",
        "send_server_port":"",
        "enable_send_server_ssl":"true/false",
        "smtp_server_host":"",
        "smtp_server_port":"",
        "enable_smtp_server_ssl":"",
        "enable_starttls":"true/false",
        "exchange_server":""
    }

## 1.mail server setting
### get mail server setting request
    request:http://127.0.0.1:port/setting/get_setting_list
    method:get
#### response:
    {result:0, "server_settings":[mail_server_setting], "errmsg":""}

### add mail server setting request
    http://127.0.0.1:port/setting/add_setting
    method: post
#### data:
    {"setting":mail_server_setting}
#### response:
    {"result":"", "id":"", "errmsg":""}

### edit mail server setting request
    http://127.0.0.1:port/setting/edit_setting
    method: post
#### data:
    {"setting":mail_server_setting}
#### response:
    {"result":"", "id":"", "errmsg":""}

### delete mail setting request
    http://127.0.0.1:port/setting/del_setting
    method: post
#### data:
    {"id":"setting_id"}
#### response:
    {"result":0, "id":"", "errmsg":""}

## 2.mail auth
    logined_account_info:{"uid":0, "mail_account_name":""}
### get logined account request
    http://127.0.0.1:port/auth/logined_account
    method:get
#### response
    {"result":0, "account_info":[logined_account_info], "errmsg"}

### login request
    http://127.0.0.1:port/auth/login
    method:post
#### data:
    {"mail_account_name":"", "mail_account_psd":""}
#### response:
    {"result":0, "uid":"", "mail_address":"" , "errmsg":""}

### logout request
    http://127.0.0.1:port/auth/logout
    method:post
#### data:
    {"mail_account_name":"", "mail_account_psd":""}
#### response:
    {"result":0, "uid":"", "mail_address":"" , "errmsg":""}

## 3.mail content
协议结构体：
### mail_title
    {"id":xx,"title":"", "sender":"xxx@mail.com", "time":"yyyy-mm-dd HH:MM:SS", "readed":"true/false",       "sended":"true/false"}
### attachment
    {"name":"", "remeto_url":url, "local_path":""}
### mail_content
    {"id":xx,"title":"", "sender":"", "cc":"", "content":"", "attach_list":[attachment]}

### get mail list request
    request:http://127.0.0.1:port/mail/get_mail_list?uid=x&index=id&count=xxx;
    method:get
#### response:
    {result:0, "count":xxxx; "mail_list":[mail_title], "total_count":xxxx}
    
### get send box mail request
    request:http://127.0.0.1:port/mail/get_send_box_mail_list?index=id&count=xxx;
    method:get
#### response:
    {result:0, "count":xxxx; "mail_list":[mail_title], "total_count":xxxx}

### get mail content request:
    http://127.0.0.1:port/mail/get_mail_content?id=id;
    method:get
#### response:
    {"result":0, "id":"", "content":mail_content, "errmsg":""}

## 4.mail operator
#### tag mail request
    http://127.0.0.1:port/mail/tag"
    method:post
#### data
    {"op_list":[{"id", "op":"read/unread/del"}]}
#### response:
    {"result":0, "id":"", "errmsg":""}

#### edit mail content
    http://127.0.0.1:port/mail/edit_mail"
    method:post
#### data
    {"id":xx,"title":"", "sender":"", "cc":"", "content":"", "attach_list":[attachment]}
#### response:
    {"result":0, "id":"", "errmsg":""}
    
## 5.send mail
### send mail request
    request:http://127.0.0.1:port/mail/send_mail
    method: post
#### data:
    {"mail":mail_content}
#### response:
    {"result":0, "id":"id of mail", "errmsg":""}

# install

# config

# license
