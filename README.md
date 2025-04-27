# Telegram 文件转发至邮箱 (telegram2email)

本项目旨在将用户发送给指定 Telegram Bot 的文件自动转发至预设的邮箱地址。一个常见的应用场景是，将电子书等文件自动转发到 Kindle 设备的邮箱中。  
可搭配 Z-library bot 使用，将电子书转给此bot。

---
此脚本使用 **轮询** 的方式获取 Telegram 消息，不影响原有的 Telegram bot 的功能。

### 环境变量

| 变量名        | 默认值             | 说明                                                         | 必填 |
| ------------- | ------------------ | ------------------------------------------------------------ | ---- |
| bot_token     | 无                 | Telegram Bot Token                                           | 是   |
| admin_chat_id | 无                 | 你的 Telegram 用户 ID，Bot 只会处理来自此用户的消息          | 是   |
| telegram_api  | api.telegram.org   | Telegram Bot API 地址，国内用户可使用 Cloudflare 等建反向代理 | 否   |
| poll_interval | 5                  | Bot 轮询更新的间隔时间（秒）                                 | 否   |
| save_path     | .                 | 文件保存路径，***可搭配calibre使用，实现电子书自动入库***                                 | 否   |
| send_to_email | False              | 是否启用邮件发送功能                                         | 否   |
| debug         | False              | 是否开启 Debug 模式，开启后日志输出更详细                    | 否   |
| mail_sender   | 无                 | 发件人邮箱地址                                               | 否   |
| send_server   | 无                 | 发件人邮箱的 SMTP 服务器地址                                 | 否   |
| send_port     | 465                | 发件人邮箱的 SMTP 服务器端口 (通常 SSL 为 465, TLS 为 587)   | 否   |
| password      | 无                 | 发件人邮箱密码或授权码                                       | 否   |
| receiver      | 无                 | 收件人邮箱地址 (例如你的 Kindle 邮箱)                        | 否   |

### 使用方法

#### 方法一：使用 Docker 运行

1.  拉取 Docker 镜像：
    ```bash
    docker pull alfchao/telegram2email
    ```
2.  修改 `docker-compose.yml` 文件（如果使用），填入所需的环境变量。
3.  启动容器：
    ```bash
    docker-compose up -d
    ```
    或者直接使用 `docker run` 并通过 `-e` 参数传入环境变量。

#### 方法二：下载源码执行

1.  克隆项目仓库：
    ```bash
    git clone https://github.com/alfchao/telegram2email.git
    ```
2.  进入项目目录：
    ```bash
    cd telegram2email
    ```
3.  安装依赖：
    ```bash
    python -m pip install -r requirements.txt
    ```
4.  修改 `app` 目录下的 `.env` 文件（如果存在）或直接设置环境变量。
5.  运行程序：
    ```bash
    python app\app.py
    ```