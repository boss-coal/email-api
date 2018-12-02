const http = require('http')
const querystring = require('querystring')

const account = 'abc@qq.com';
const password = '1234567';
const contact = 'cccc@163.com'

var post_task_queue = [];

function process_task() {
    if (post_task_queue.length > 0) {
        let task = post_task_queue.shift();
        task();
    }
}

function post(path, args, callback) {
    console.log(`post: ${path}`);
    let postData = args? querystring.stringify(args) : '';
    let options = {
        hostname: '127.0.0.1',
        port: 8080,
        path: path,
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Content-Length': Buffer.byteLength(postData)
        }
    };
    let req = http.request(options, (res) => {
        let data = null;
        res.on('data', (chunk) => {
            if (!data) {
                data = chunk;
            } else {
                data += chunk;
            }
        });

        res.on('end', (e) => {
            console.log(`response from ${path}: ${data}`);
            if (callback) {
                callback(JSON.parse(data));
            }
            process_task();
        });
    });

    req.on('error', (e) => {
        console.error(`请求遇到问题: ${e.message}`);
    });

    if (postData) {
        req.write(postData);
    }
    req.end();
}

function mailPost(path, args, callback) {
    args['mail_account_name'] = account;
    post(path, args, callback);
}

function login() {
    post('/auth/login', {
        mail_account_name: account,
        mail_account_psd: password
    });
}

const target_mailbox_name = "INBOX";
var target_mailbox = null;
function getMailbox(callback) {
    mailPost('/mail/get_mail_box_list', {}, function (result) {
        target_mailbox = result.data[target_mailbox_name];
        target_mailbox['name'] = target_mailbox_name;
        if (callback) {
            callback(result);
        }
    });
}


const fetch_remote_mail_per_time = 20;
function fetchMailList(mailbox, end, callback) {
    let start = end - fetch_remote_mail_per_time + 1;
    if (start <= 0) {
        start = 1;
    }
    mailPost('/mail/get_remote_mail_list', {
        end: end,
        start: start,
        use_uid: 0,
        mailbox: mailbox
    }, function (result) {
        if (callback) {
            callback(result);
        }
        // continue to fetch older mails
        if (start > 1) {
            fetchMailList(mailbox, start-1, callback);
        }
    });
}

function fetchMailListTask() {
    fetchMailList(target_mailbox_name, target_mailbox.EXISTS);
}


function searchContactMail() {
    mailPost('/mail/search_local_contact_mail_list', {
        contact: contact,
        after: '2018-08-08'
    });
}

function main() {
    post_task_queue.push(login);
    post_task_queue.push(getMailbox);
    post_task_queue.push(fetchMailListTask);
    post_task_queue.push(searchContactMail);

    process_task();
}

module.exports = {
    main: main,
    login: login,
    mailBox: (callback) => {getMailbox(callback)},
    fetchMails: function (callback) {
        fetchMailList(target_mailbox_name, target_mailbox.EXISTS, callback);
    }
};
