#ifndef ZM_LIB_H
#define ZM_LIB_H

#include "mwifi.h"
#include "mdf_common.h"
#include "ac_control.h"

#define MAX_MESSAGE_SIZE 500
#define LOCAL_GROUP "_____"
#define LOCAL_NAME "_____"
#define DHT_LOCAL_NAME CONFIG_LOCAL_NAME

mdf_err_t zm_broadcast(const char *msg);
mdf_err_t report_to_root(int type, int rssi, int layer);
mdf_err_t parse_manual_cmd(const cJSON *manuel_cmd);
mdf_err_t uart_init(int uart_num, int rx, int tx, int baud);
mdf_err_t msg_parse(const char *msg, int rssi, int layer);
mdf_err_t report_to_root_dht(int type, int rssi, int layer);

enum REPORT_TYPE
{
    HEARTBEAT,
    RECV,
    REPORT_NOW,
};

#endif // ZM_LIB_H