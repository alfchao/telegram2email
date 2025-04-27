FROM python:alpine
ENV TZ=Asia/Shanghai
WORKDIR /app
COPY app/app.py requirements.txt /app/

RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apk/repositories && apk update

RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple && \
    python -m pip install --upgrade pip && \
    pip install -r requirements.txt

CMD [ "python ", "app.py" ]