# example

## install
    npm install
    
## run
    mail.js 用同步的方法写了若干接口的用法，实际运行时，登陆后大部分接口都是可以异步非阻塞地运行的
    在mail.js 设置好account, password和contact（从数据库查询与该contact的邮件记录）
### run directly
    cd src
    node index.js
### run html demo
    dist/example.html 是一个初始化时拉取邮件的实例（拉取数据，同时刷新ui)
    npx webpack # 用webpack打包程序
    本地浏览器运行dist/example.html
    点击"获取邮件"按钮，拉取邮件
    