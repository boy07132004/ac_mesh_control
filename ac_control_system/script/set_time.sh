sudo timedatectl set-timezone Asia/Taipei


read -p "是否有 NTP Server IP [Y/n] " choose

if [ "$choose" = "Y" ] || [ "$choose" = "y" ] || [ -z "$choose" ]
then
    read -p '請輸入 NTP IP: ' _ip
    sudo ntpdate $_ip &&  \
    (crontab -l ; \
    echo "@daily sudo ntpdate ${_ip} >> ~/ntplog.txt"; \
    echo "@reboot sleep 30 && ntpdate ${_ip} >> ~/ntplog.txt"; \
    ) | crontab - && \
    exit
fi
echo "NTP設定失敗,請手動輸入日期"
read -p '請輸入日期 [ex: 20210713]  ' _date
read -p '請輸入現在時間 [ex: 23:59]  ' _time

sudo date -s "${_date} ${_time}"
