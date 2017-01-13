#! /usr/bin/python

#
#CONNECTION

import requests
import time
import random
from datetime import datetime
from ovirtsdk.api import API
from ovirtsdk.xml import params

VERSION = params.Version(major='3', minor='0')
ADDRESS = "http://10.10.2.5"
URL = 'https://10.10.2.5/ovirt-engine/api'
USERNAME = 'admin@internal'
PASSWORD = '12345678'
DC_NAME = 'Default'
CLUSTER_NAME = 'Default'
#HOST_NAME = 'my_host'
#STORAGE_NAME = 'ceph_storage'
STORAGE_NAME = 'ceph_storage'
#EXPORT_NAME = 'export_domain'
#VM_NAME = ["cl_bsz3","cl_bsz2","cl_bsz1","ansible"]

#### FUNCTIONS

def start_all_virt():
    "stop all virtualization"
    vm_list=api.vms.list()
    for i in vm_list:
        vm_name=i.name
        print vm_name
        try:
            if api.vms.get(vm_name).status.state != 'up':
                print vm_name+" status "+api.vms.get(vm_name).status.state
                print "send start to VM "+vm_name
                api.vms.get(vm_name).start()
                #print 'Waiting for VM '+vm_name+" to stop"
                #while api.vms.get(vm_name).status.state != 'up':
                #  time.sleep(1)
            else:
                print 'VM already up'

        except Exception as e:
            print 'Start VM:\n%s' % str(e)

def check_storage_status():
    "check_ss"
    dc = api.datacenters.get(DC_NAME)
    storageInDc = dc.storagedomains.get(STORAGE_NAME)
    storageStatus = storageInDc.status.state
    print storageInDc.id
    print "check storage status is %s" % storageStatus
    if storageInDc is None:
        print "storage name %s is not exist" % STORAGE_NAME
        return False
    if storageStatus == 'active':
        print "Storage %s already active" % storageInDc.name
        return True
    elif storageStatus == 'locked':
        print "Storage %s is locked" % storageInDc.name
        time.sleep(10)
        return False
    elif storageStatus == 'unknown':
        print "Storage %s is unknown" % storageInDc.name
        print "Will try to activate"
        try:
            storageInDc.activate()
        except Exception, err:
            print err
            return False
        return False
    elif storageStatus == 'preparing_for_maintenance':
        print "Storage %s is preparing for maintenance" % storageInDc.name
        time.sleep(10)
        return False
    elif storageStatus == 'maintenance':
        print "Storage %s is in maintenenace mode" % storageInDc.name
        print "Will try to activate"
        try:
            storageInDc.activate()
            return False
        except Exception, err:
            print err
            return 0
    elif storageStatus == 'inactive':
        print "Storage %s is inactive" % storageInDc.name
        print "Will try to activate"
        try:
            storageInDc.activate()
            return False
        except Exception, err:
            print err
            return 0

def check_manager_livelines():
    "check manager liveliness"
    print "%s : Checking manager existing" % datetime.now()
    try:
        request = requests.get(ADDRESS, timeout=10.0)
        if request.status_code == 200:
            print "Manager with address %s is available\ncontinuing" % ADDRESS
            return True
        else:
            print "Manager with address %s is not available" % ADDRESS
            return False
    except requests.Timeout as err:
        print "Manager with address %s is not available, connection timed out" % ADDRESS
        return False
    except requests.RequestException as err:
        print "Manager with address %s is not available" % ADDRESS
        return False

def check_api_available():
    global api
    try:
        api = API(url=URL, username=USERNAME, password=PASSWORD, insecure=True)
        print "connection succeded"
        return True
    except ConnectionError, err:
        print "Connection failed: %s" % err
        return False


def check_vm_status(vm_name):
    "VM status"
    counter=0
    print "status %s is %s" % (vm_name, api.vms.get(vm_name).status.state)
    while (api.vms.get(vm_name).status.state == 'down') and (counter < 6):
        print "Trying to start %s, count number %s" % (vm_name, (counter + 1))
        api.vms.get(vm_name).start()
        counter = counter + 1
        time.sleep(5)

def check_hosts_status():
    time.sleep(15)
    hosts = api.hosts.list()
    for i in hosts:
        print i.name+" "+i.status.state
        if i.status.state != 'up':
            try:
                print "try to activate hosted_engine"
                i.activate()
            except Exception, err:
                print err



def startup_function():
    "runs at startup"
    start = datetime.now()
    print "PYTHON REST_API SCRIPT RUNNING"
    while check_manager_livelines() is False:
        time.sleep(10)
    while check_api_available() is False:
        time.sleep(10)
    check_hosts_status()
    while check_storage_status() is False:
        time.sleep(10)
        print "returned False"
        print "%s : still waiting" % datetime.now()
    check_hosts_status()
    time.sleep(10)
    start_all_virt()
    check_hosts_status()
    for i in api.vms.list():
        try:
            vm_name=i.name
            check_vm_status(vm_name)
        except Exception, err:
            print err
    check_hosts_status()
    end = datetime.now()
    print "\n%s : finished\n" % datetime.now()
    print "Started at %s; ended at %s" % (start, end)

###### RUNNING SCRIPT


startup_function()
