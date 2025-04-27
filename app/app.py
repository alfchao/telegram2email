import functools
import os
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import aiosmtplib
from urllib.parse import urlparse
from pathlib import Path
from loguru import logger
from pydantic_settings import BaseSettings
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, filters, MessageHandler
import json
base_url = "https://api.telegram.org/bot"
base_file_url = "https://api.telegram.org/file/bot"

def json_f(data):
    return json.dumps(data, ensure_ascii=False, indent=4)

class Settings(BaseSettings):
    class Config:
        env_file = ".env"

    bot_token: str
    admin_chat_id: str
    telegram_api: str = 'api.telegram.org'
    poll_interval: int = 5
    save_path: str = '.'
    send_to_email: bool = False
    debug: bool = False
    mail_sender: str = None
    send_server: str = None
    send_port: int = 465
    password: str = None
    receiver: str = None



settings = Settings()


if settings.debug:
    level = "DEBUG"
else:
    level = "INFO"

LOGGER_FORMAT = "[{time}]({level}) pid:{thread}, tid:{process}, {file}, {module}, {function}, {line}: {message}"
logger.add(sys.stdout, level=level, format=LOGGER_FORMAT)
logger.add("main.log", level=level, rotation="1 days", encoding="utf-8", enqueue=True, retention="7 days",
           format=LOGGER_FORMAT)


logger.info(json_f(settings.dict()))


def convert_size(text):
    """
    文件大小单位换算
    :text: 文件字节
    :return: 返回字节大小对应单位的数值
    """
    units = ["B", "KB", "MB", "GB", "TB", "PB"]
    size = 1024
    for i in units:
        if (text / size) < 1:
            return "%.2f%s" % (text, i)  # 返回值保留小数点后两位
        text /= size


async def async_send_email(attach_file):
    msg = MIMEMultipart()
    msg['From'] = settings.mail_sender
    msg['To'] = settings.receiver
    msg['Subject'] = os.path.basename(attach_file)
    mail_content = '邮件由telegram2kindle发送，' + os.path.basename(attach_file)
    content = MIMEText(mail_content, 'plain', 'utf-8')
    msg.attach(content)
    with open(attach_file, 'rb') as f:
        attach = MIMEText(f.read(), 'base64', 'utf-8')
    attach['Content-Type'] = 'application/octet-stream'
    attach.add_header('Content-Disposition', 'attachment', filename=os.path.basename(attach_file))
    msg.attach(attach)
    async with aiosmtplib.SMTP(
            hostname=settings.send_server,
            port=settings.send_port,
            use_tls=True  # 默认SSL
    ) as smtp:
        await smtp.login(settings.mail_sender, settings.password)
        await smtp.send_message(msg)
        logger.info('邮件异步发送成功')


if settings.telegram_api:
    base_url = urlparse(base_url)._replace(netloc=settings.telegram_api).geturl()
    base_file_url = urlparse(base_file_url)._replace(netloc=settings.telegram_api).geturl()


def auth_admin(func):
    @functools.wraps(func)
    async def warpper(*args, **kwargs):
        update = args[0]
        logger.info(f"{args}, {kwargs}")
        logger.debug(update.message)
        if update.message.from_user.id != int(settings.admin_chat_id):
            logger.info(f"{update.message.from_user.id} 无权限")
        else:
            await func(*args, **kwargs)

    return warpper


@auth_admin
async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Hello {update.effective_user.first_name}',
                                    reply_to_message_id=update.message.message_id)


# 下载收到的文件
@auth_admin
async def download(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    file_id = update.message.document.file_id
    file_name = update.message.document.file_name
    logger.info(f"文件名是：{file_name}， 大小：{convert_size(float(update.message.document.file_size))}")
    # 回复消息，正在下载中
    reply = await update.message.reply_text("正在下载中，请稍后...", reply_to_message_id=update.message.message_id)
    new_file = await context.bot.get_file(file_id)

    custom_path = os.path.join(settings.save_path, file_name)
    await new_file.download_to_drive(custom_path=custom_path)
    if settings.send_to_email:
        logger.info("发送邮件")
        await async_send_email(custom_path)
        logger.info("发送完成")
    # 下载完成，
    await reply.edit_text("下载完成")
    # 发送邮件


app = ApplicationBuilder().token(settings.bot_token).base_url(
    base_url).base_file_url(base_file_url).build()

app.add_handler(CommandHandler("hello", hello))
app.add_handler(MessageHandler(filters.Document.ALL, download))

app.run_polling(poll_interval=settings.poll_interval)
