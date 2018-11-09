from account_manager import Account

def getTestSetting(setting_id):
    settings = {
        1: {
            'id': 1,
            'host': '163.com',
            'smtp_server_host': 'smtp.163.com',
            'imap_server_host': 'imap.163.com'
        }
    }
    return settings.get(setting_id, None)


def getTestAccount():
    return Account('boss_coal@163.com', 'daweige123', 'smtp.163.com', 'imap.163.com')


def getTestLoginedAccounts():
    return [getTestAccount()]