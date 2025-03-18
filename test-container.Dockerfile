FROM python:3.13

ENV APP_HOME=/app \
    TZ=Europe/Berlin \
    PIP_ROOT_USER_ACTION=ignore

ADD requirements.txt /
    
RUN rm /usr/bin/python3 &&\
    ln -s /usr/local/bin/python3 /usr/bin/python3 &&\
    apt-get update &&\
    python -m pip install --upgrade pip 
    #&&\
    #pip install --no-cache-dir -r /requirements.txt 
    #&&\
    #git ngsildclient

RUN mkdir -p    $APP_HOME &&\
    mkdir -p    $APP_HOME/src &&\
    mkdir -p    $APP_HOME/data &&\
    cd $APP_HOME/src &&\
    export PATH=${PATH}:/home/myuser/.local/bin:$APP_HOME/src

# Klonen und Installieren des ngsildclient-Pakets
RUN cd $APP_HOME/src &&\
    #mkdir ngsild-client &&\
    #cd ngsild-client &&\
    git clone https://github.com/Orange-OpenSource/python-ngsild-client.git &&\
    cd python-ngsild-client &&\
    pip install . &&\
    cd $APP_HOME/src

VOLUME  [ "$APP_HOME/data" ]
WORKDIR $APP_HOME/src
ENTRYPOINT [ "./orionld_test.py" ]

COPY orionld_test.py            $APP_HOME/src/orionld_test.py
RUN chmod ugo+rwx $APP_HOME/src/*.py &&\
    ls -la $APP_HOME/src



