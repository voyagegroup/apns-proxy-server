#!/bin/bash

app=`basename $0`
pid=`dirname $0`/run/apns_proxy_server.pid
APNS_PROXY_CRONOLOG_PATH=${APNS_PROXY_CRONOLOG_PATH:-/usr/sbin/cronolog}
APNS_PROXY_LOG_PATH=${APNS_PROXY_LOG_PATH:-/var/log/app_tmp/apns-proxy-server/%Y/%m/%d/apns_proxy.log}


start() {
    if [ -f $pid ] && kill -0 `cat $pid` 2>/dev/null; then
        echo "running already. pid: `cat $pid`";
        return 1;
    fi

    cd `dirname $0`
    exec 8> >($APNS_PROXY_CRONOLOG_PATH -w $APNS_PROXY_LOG_PATH)
    ./bin/python -m apns_proxy_server.invoker 2>&8 1>&8 &

    mkdir -p `dirname $pid`
    echo $! > $pid
}

stop() {
    kill `cat $pid`
    rm -f $pid
    exec 8>&-
}

restart() {
    stop
    start
}

status() {
    if [ -f $pid ]; then
        ps u --pid=`cat $pid`
        echo
        ps xfo "%U %p %C %z %t (%x) %c : " o args=ARGS
    else
        echo "not running.";
        exit 3;
    fi
}

case "$1" in
  start)
    start
    ;;
  stop)
    stop
    ;;
  restart)
    restart
    ;;
  status)
    status
    ;;
  *)
    echo $"Usage: $0 {start|stop|restart|status}"
    exit 1
esac

exit $?
