

const mail = require('./mail');



var Main = {
    data() {
        return {
            tableData: [],
            ok: true
        }
    },
    methods: {
        toFetch: function () {
            mail.fetchMails( (result) => {
                result.data.forEach((item) => {
                    this.tableData.push(item);
                });

            });
        }
    },
    created: function () {
        console.log('created');
        mail.login();
        setTimeout( () => {
            mail.mailBox((result) => {this.ok = false;});
        }, 1000);

    }
};


var Ctor = Vue.extend(Main)
new Ctor().$mount('#app')