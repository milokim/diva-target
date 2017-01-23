#!/bin/bash
USERLOCAL=/usr/local/bin/
RUNSCRIPT=diva-device
SYSTEMD_ETC=/etc/systemd/system/
SERVICE=diva-device.service

cp $RUNSCRIPT $USERLOCAL
chmod a+x $USERLOCAL$RUNSCRIPT
cp $SERVICE $SYSTEMD_ETC
chmod 0664 $SYSTEMD_ETC$SERVICE 

systemctl daemon-reload
systemctl start $SERVICE
systemctl enable $SERVICE
