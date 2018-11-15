from account_manager import Account

def getTestSetting(setting_id):
    settings = {
        1: {
            'id': 1,
            'host': '163.com',
            'smtp_server_host': 'smtp.163.com',
            'imap_server_host': 'imap.163.com'
        },
        2: {
            'id': 2,
            'host': 'qq.com',
            'smtp_server_host': 'smtp.qq.com',
            'imap_server_host': 'imap.qq.com',
        }
    }
    return settings.get(setting_id, None)


def getTestAccount():
    return Account('boss_coal@163.com', 'daweige1234', 'smtp.163.com', 'imap.163.com')


def getTestLoginedAccounts():
    qq_account = Account('215731713@qq.com', 'vkcjffgagicnbhhd', 'smtp.qq.com', 'imap.qq.com')
    return [
        getTestAccount(),
        qq_account
    ]