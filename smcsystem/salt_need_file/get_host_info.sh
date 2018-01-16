#!/bin/bash

salt_id=`cat /etc/salt/minion|grep -Po '(?<=^id: ).*'|head -1`
ip=`ip a|awk '/inet /{split($2,a,"/");if(a[2]!="32"&&a[1]!="127.0.0.1")print a[1]}'|head -1`
all_ip=`ip a|sed '/^1:/,/^2:/d'|awk '/inet /{split($2,a,"/");if(a[1]!="127.0.0.1"&&a[2]!="32")print $NF,a[1]" ";if(a[2]=="32")print "vip",a[1]" "}'|sed ':a;N;s/\n//;ta'`
ifconfig_info=`ifconfig|sed ':a;N;s/\n/ttwrap/;ta'`
hostname=`hostname`
#cpu
cpu_num=`cat /proc/cpuinfo |grep "processor"|wc -l`
cpu=`cat /proc/cpuinfo | grep name|awk -F': ' 'NR==1{print $2}'`

#磁盘
disk_num=`fdisk -l 2>/dev/null|grep Disk|grep sd|wc -l`

if [[ ${disk_num} > 20 ]];then
    disk_num=`mount|grep -o '/dev/sd.'|awk '!a[$0]++'|wc -l`
fi


disk_g=`df -hP|awk '!/^[0-9]+/{print $2}'|grep 'G'|awk '{a+=+$0}END{print a}'`
disk_t=`df -hP|awk '!/^[0-9]+/{print $2}'|grep 'T'|awk '{a+=+$0}END{print a}'`
disk_t_g=`echo "${disk_t:-0}*1024"|bc`
disk_all=`echo "${disk_t_g}+${disk_g}"|bc`
disk_use_g=`df -hP|awk '!/^[0-9]+/{print $3}'|grep 'G'|awk '{a+=+$0}END{print a}'`
disk_use_t=`df -hP|awk '!/^[0-9]+/{print $3}'|grep 'T'|awk '{a+=+$0}END{print a}'`
disk_use_t_g=`echo "${disk_use_t:-0}*1024"|bc`
disk_use=`echo "${disk_use_t_g}+${disk_use_g:-0}"|bc`

#内存
free_all=`free -m|awk '/Mem/{printf "%0.1f\n",$2/1024}'`
free_num=`free -m|awk '/-/'|awk '{printf "%0.1f\n",$NF/1024}'`
free_use=`echo $free_all-$free_num|bc`

#品牌
brand_len=`dmidecode |grep Vendor|wc -l`
if [[ ${brand_len} == 1 ]];then
    brand=`dmidecode |grep Vendor|grep -v "VMware"|grep -Po '(?<=: )[\w]+.*'`
else
    brand="None"
fi


#主机性质 1是物理机 2是虚拟机

if lspci | grep -i vga|grep VMware >/dev/null
then
    type='2'
else
    type='1'
fi

#sn号
sn=`dmidecode -t 1|grep "Serial Number"|grep -v "VMware"|grep -Po '(?<=: )[\w]+'`


#系统版本
system=`cat /etc/issue|head -1|sed 's/release//g'|sed 's/(.*)//g'|awk '{$1=$1;print $0}'`

#系统内核
kernel=`uname -r`


echo "${ip}|${hostname}|${cpu_num}|${cpu}|${disk_num}|${disk_all}g|${disk_use}g|${free_all}g|${free_use}g|${brand:-None}|${type}|${sn:-None}|${system}|${kernel}|${salt_id}|${all_ip}|${ifconfig_info}"
