#include "ac_control.h"

static const char *TAG = "ac_control";

int control_ac_with_cmd(int cmd_idx)
{
    if (cmd_idx < 0 || cmd_idx >= sizeof(CMD_SET) / (8 * sizeof(uint8_t)))
    {
        ESP_LOGE(TAG, "CMD IDX ERROR, IDX : %d", cmd_idx);
        return CMD_IDX_ERROR;
    }

    return control_ac_with_rs485(CMD_SET[cmd_idx]);
}

int control_ac_with_rs485(const uint8_t *cmd)
{
    uint8_t data[BUF_SIZE_485];
    uint8_t len;

    uart_write_bytes(UART_NUM_2, cmd, 8);
    len = uart_read_bytes(UART_NUM_2, data, BUF_SIZE_485, PACKET_READ_TICS * 10);

    if (cmd[1] <= 0x04 && len > 5)
        return (data[3] << 8 | data[4]);
    else
        return NO_RETURN_VALUE;
}
