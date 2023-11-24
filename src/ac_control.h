#ifndef AC_CONTROL_H
#define AC_CONTROL_H

#define PACKET_READ_TICS (100 / portTICK_PERIOD_MS)
#define BUF_SIZE_485 100
#define CMD_LENGTH 18

#define NO_RETURN_VALUE -1
#define CMD_IDX_ERROR -2

#include "mwifi.h"
#include "mdf_common.h"
#include "driver/uart.h"

int control_ac_with_cmd(int cmd_idx);
int control_ac_with_rs485(uint8_t *cmd);

/*
< Name > <Device> <Func> <Register> < Value > <  CRC  >
POWER_ON   0x02    0x06  0x00 0x02  0x00 0x01 0xE9 0xF9
*/
static const uint8_t CMD_SET[][8] = {
    {0x02, 0x03, 0x00, 0x02, 0x00, 0x01, 0x25, 0xF9}, // 0  讀取開/關機狀態
    {0x02, 0x03, 0x00, 0x01, 0x00, 0x01, 0xD5, 0xF9}, // 1  讀取冷氣工作模式
    {0x02, 0x03, 0x00, 0x03, 0x00, 0x01, 0x74, 0x39}, // 2  讀取副控面鎖定狀態
    {0x02, 0x03, 0x00, 0x05, 0x00, 0x01, 0x94, 0x38}, // 3  讀取室內溫度
    {0x02, 0x03, 0x00, 0x06, 0x00, 0x01, 0x64, 0x38}, // 4  讀取溫度設定值
    {0x02, 0x03, 0x00, 0x0D, 0x00, 0x01, 0x15, 0xFA}, // 5  讀取風速狀態

    {0x02, 0x06, 0x00, 0x02, 0x00, 0x01, 0xE9, 0xF9}, // 6  寫入開機狀態
    {0x02, 0x06, 0x00, 0x02, 0x00, 0x00, 0x28, 0x39}, // 7  寫入關機狀態

    {0x02, 0x06, 0x00, 0x01, 0x00, 0x01, 0x19, 0xF9}, // 8  寫入冷氣Cool模式
    {0x02, 0x06, 0x00, 0x01, 0x00, 0x02, 0x59, 0xF8}, // 9  寫入冷氣Fan模式

    {0x02, 0x06, 0x00, 0x03, 0x00, 0x00, 0x79, 0xF9}, // 10 寫入副控面板不鎖定狀態
    {0x02, 0x06, 0x00, 0x03, 0x00, 0x01, 0xB8, 0x39}, // 11 寫入副控面板鎖定狀態

    {0x02, 0x06, 0x00, 0x06, 0x01, 0x04, 0x69, 0xAB}, // 12 寫入設定溫度26度
    {0x02, 0x06, 0x00, 0x06, 0x01, 0x0E, 0xE9, 0xAC}, // 13 寫入設定溫度27度
    {0x02, 0x06, 0x00, 0x06, 0x01, 0x18, 0x68, 0x62}, // 14 寫入設定溫度28度

    {0x02, 0x06, 0x00, 0x0D, 0x00, 0x01, 0xD9, 0xFA}, // 15 寫入風速High
    {0x02, 0x06, 0x00, 0x0D, 0x00, 0x02, 0x99, 0xFB}, // 16 寫入風速Mid
    {0x02, 0x06, 0x00, 0x0D, 0x00, 0x03, 0x58, 0x3B}, // 17 寫入風速Low
    {0x02, 0x06, 0x00, 0x06, 0x00, 0xC8, 0x68, 0x6E}, // 18 溫度20度
};

#endif // AC_CONTROL_H