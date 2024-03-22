#!/bin/bash
path="/home/pi/${PROJECT}/python_application/apc/apc_upload.ini"
echo "[APC]" > $path

read -p "是否轉為APC格式 (Y/N) " choose
if [ "$choose" = "Y" ] || [ "$choose" = "y" ] || [ -z "$choose" ]
then
    echo "XML Version"
    echo "CSV = N" >> $path
else
    echo "CSV Version"
    echo "CSV = Y" >> $path
fi


echo "輸入儲存資料夾名稱 (Tool ID)"
echo "ex: AASPT500"
read -p 'Tool ID? ' _toolid
echo "EQP_ID = ${_toolid}" >> $path

echo "[FTP]" >> $path
read -p "FTP server IP位址？ " _host
read -p "FTP user name？ " _user
read -p "FTP user password？ " _password

echo "HOST = ${_host}" >> $path
echo "USER = ${_user}" >> $path
echo "PASSWORD = ${_password}" >> $path

cp /home/pi/$PROJECT/python_application/apc/cron_script /home/pi/$PROJECT/python_application/
docker restart ${PROJECT}_python_application_1
