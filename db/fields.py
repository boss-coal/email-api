table_list = ['mail_setting', 'mail_account', 'mail_title', 'mail_content']

fields = {
    'mail_setting': (
        ('id', 'integer not null primary key autoincrement'),
        ('host', 'varchar(256) not null'),
        ('type', 'varchar(16) not null default "imap4"'),
        ('imap_server_host', 'varchar(256) not null'),
        ('imap_server_port', 'integer not null default 143'),
        ('smtp_server_host', 'varchar(256) not null'),
        ('smtp_server_port', 'integer not null default 25'),
        ('enable_smtp_server_ssl', 'integer default 0'),
        ('enable_starttls', 'integer default 0'),
        ('exchange_server', 'integer default 0'),
    ),
    'mail_account': (
        ('id', 'integer not null primary key autoincrement'),
        ('mail_account_name', 'varchar(256) not null'),
        ('mail_account_psd', 'varchar(256) not null'),
        ('status', 'integer default 0'),
        ('mail_setting_id', 'integer not null references "mail_setting" ("id")'),
    ),
    'mail_title': (
        ('id', 'integer not null primary key autoincrement'),
        ('msg_id', 'varchar(1024) not null'),
        ('uuid', 'integer not null'),
        ('mail_box', 'varchar(128) not null'),
        ('subject', 'varchar(1024) not null'),
        ('to', 'varchar(4096) not null'),
        ('cc', 'varchar(4096)'),
        ('bcc', 'varchar(4096)'),
        ('from', 'varchar(4096) not null'),
        ('date', 'varchar(1024) not null'),
        ('gm_time', 'int'),
        ('tag', 'varchar(1024)'),
        ('mail_uid_id', 'integer not null references "mail_account" ("id")'),
    ),
    'mail_content': (
        ('id', 'integer not null primary key autoincrement'),
        ('uuid', 'integer not null'),
        ('content', 'text not null'),
        ('mail_box', 'varchar(128) not null'),
        ('mail_uid_id', 'integer not null references "mail_account" ("id")'),
    ),
}

def parseQueryList(data, table):
    field = fields.get(table, None)
    if field:
        result = []
        for item in data:
            node = {}
            for i, v in enumerate(item):
                node[field[i][0]] = v
            result.append(node)
        return result
    return data