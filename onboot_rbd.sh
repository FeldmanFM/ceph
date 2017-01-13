#!/bin/bash
### GLOBAL VARIABLES

#####################################
#####	global variables	#####
#####################################
status=1



#####################################
#####		functions	#####
#####################################

function ceph_wait {
echo "`date +%Y/%m/%d-%H:%M:%S`: start waiting for ceph"
logger "$0 : start waiting for ceph"
while [ "$status" -ne 0 ]
do
        echo "`date +%Y/%m/%d-%H:%M:%S`: keep waiting"
	logger "$0 : keep waiting"
        timeout 30 ceph health
        status=$?
        echo $status
        sleep 3
done
}

function ceph_status {
echo "`date +%Y/%m/%d-%H:%M:%S`: start status check for ceph"
logger "$0 : start status check for ceph"
sleep 30
while [ `ceph health | awk '{print $1}'` = "HEALTH_ERR" ]
do
        echo "`date +%Y/%m/%d-%H:%M:%S`: keep waiting"
	loger "$0 : keep waiting"
	sleep 30
done
}

function ceph_map {

echo "`date +%Y/%m/%d-%H:%M:%S`: start mapping devices"
logger "$0 : start mapping devices"
rbdmap map

echo "`date +%Y/%m/%d-%H:%M:%S`: map complete"
logger "$0 : map complete"

}

function ceph_iscsi_restore {
echo "`date +%Y/%m/%d-%H:%M:%S`: iscsi restoring"
logger "$0 : iscsi restoring"
systemctl stop tgtd && targetcli clearconfig  confirm=True && targetcli restoreconfig /etc/target/startup-config.json  && systemctl start tgtd && echo "service tgtd started"
sleep 30
echo "`date +%Y/%m/%d-%H:%M:%S`: iscsid restarting"
logger "$0 : iscsi restarting"
systemctl restart iscsid
/usr/sbin/iscsiadm -m node --targetname iqn.2016-08.ru.gtest:ovirt -p 127.0.0.1:3260 -l
/usr/sbin/iscsiadm -m node --targetname iqn.2016-08.ru.gtest:storage -p 127.0.0.1:3260 -l
echo "`date +%Y/%m/%d-%H:%M:%S`: complete"
logger "$0 : complete"
}

function ovirt_ha_start {
sleep 30
echo "`date +%Y/%m/%d-%H:%M:%S`: ovirt ha restoring"
systemctl start ovirt-ha-agent ovirt-ha-broker vdsmd
echo "`date +%Y/%m/%d-%H:%M:%S`: ovirt ha ending"
}



ceph_wait
ceph_status
ceph_map
ceph_iscsi_restore
ovirt_ha_start
python2 /root/onboot.py 2>&1 > /root/py.txt
