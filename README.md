# email-api
#mail http protocol

协议结构体
mail_server_setting{
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

--------------协议----------------
1.---------------------mail server setting -------------------------------
http://127.0.0.1:port/setting/get_setting_list
method: get
response:
{result:0, "server_settings":[mail_server_setting], "errmsg":""}

http://127.0.0.1:port/setting/add_setting
method: post
data:{"setting":mail_server_setting}
response:
{"result":"", "id":"", "errmsg":""}

http://127.0.0.1:port/setting/edit_server_setting
method: post
data:
{"setting":mail_server_setting}
response:
{"result":"", "id":"", "errmsg":""}

http://127.0.0.1:port/setting/del_setting
method: post
data:
{"id":"setting_id"}
response:
{"result":0, "id":"", "errmsg":""}

2-------------------------------mail auth--------------------------------------
http://127.0.0.1:port/auth/login
method:post
data:{"mail_account_name":"", "mail_account_psd":""}
response:
{"result":0, "uid":"", "errmsg":""}

3.------------------------------mail content-------------------------------------
协议结构体：
mail_title{"id":xx,"title":"", "sender":"xxx@mail.com", "time":"yyyy-mm-hh HH:MM:SS", "readed":"true/false", "sended":"true/false"}
attachment{"name":"", "remeto_url":url, "local_path":""}
mail_content{"id":xx,"title":"", "sender":"", "cc":"", "content":"", "attach_list":[attachment]}
request:http://127.0.0.1:port/mail/get_recevice_mail_list?index=id&count=xxx;
method:get
response:
{result:0, "count":xxxx; "mail_list":[mail_title], "total_count":xxxx}
request:http://127.0.0.1:port/mail/get_send_mail_list?index=id&count=xxx;
method:get
response:
{result:0, "count":xxxx; "mail_list":[mail_title], "total_count":xxxx}
request:http://127.0.0.1:port/mail/get_mail_content?id=id;
method:get
response:
{"result":0, "id":"", "content":mail_content, "errmsg":""}
4-------------------------------mail mark----------------------------------------
request:http://127.0.0.1:port/mail/mark_as_readed?id=xxx?operator="read, unread, del"
method:get
response:
{"result":0, "id":"", "errmsg":""}
5-------------------------------mail send ---------------------------------------
request:http://127.0.0.1:port/mail/send_mail
method: post
data:{"mail":mail_content}
response:
{"result":0, "id":"id of mail", "errmsg":""}

# install

# license
