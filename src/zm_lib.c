#include "zm_lib.h"

static const char *TAG = "ZM_LIB";

mdf_err_t uart_init(int uart_num, int rx, int tx, int baud)
{
    uart_config_t uart_config = {
        .baud_rate = baud,
        .data_bits = UART_DATA_8_BITS,
        .parity = UART_PARITY_DISABLE,
        .stop_bits = UART_STOP_BITS_1,
        .flow_ctrl = UART_HW_FLOWCTRL_DISABLE};

    ESP_ERROR_CHECK(uart_param_config(uart_num, &uart_config));
    ESP_ERROR_CHECK(uart_set_pin(uart_num, tx, rx, UART_PIN_NO_CHANGE, UART_PIN_NO_CHANGE));
    ESP_ERROR_CHECK(uart_driver_install(uart_num, 1024 * 2, 0, 0, NULL, 0));

    return MDF_OK;
}

mdf_err_t zm_broadcast(const char *msg)
{
    mdf_err_t ret = MDF_OK;
    wifi_sta_list_t wifi_sta_list = {0x0};
    mwifi_data_type_t data_type = {0};
    data_type.compression = true;

    char json_message[MAX_MESSAGE_SIZE];

    esp_wifi_ap_get_sta_list(&wifi_sta_list);
    for (int i = 0; i < wifi_sta_list.num; i++)
    {
        ESP_LOGI(TAG, "Send to MAC: " MACSTR, MAC2STR(wifi_sta_list.sta[i].mac));
        size_t size = snprintf(json_message, MAX_MESSAGE_SIZE, "%s", msg);
        ret = mwifi_write(wifi_sta_list.sta[i].mac, &data_type, json_message, size, true);

        if (ret != MDF_OK)
        {
            ESP_LOGE(TAG, "Send failed MAC:" MACSTR, MAC2STR(wifi_sta_list.sta[i].mac));
        }
    }

    return ret;
}

mdf_err_t report_to_root(int rssi, int layer)
{
    int size;
    char msg[MAX_MESSAGE_SIZE];
    mdf_err_t ret;
    mwifi_data_type_t data_type = {0};
    data_type.compression = true;

    int on_off = control_ac_with_cmd(0);
    int work_mode = control_ac_with_cmd(3);
    int locked = control_ac_with_cmd(6);
    int curr_temp = control_ac_with_cmd(14);
    int set_temp = control_ac_with_cmd(15);
    int wind_speed = control_ac_with_cmd(9);
    int valve = control_ac_with_cmd(13);

    size = snprintf(msg, MAX_MESSAGE_SIZE, "{\"device\":\"%s\",\"value\":[%d,%d,%d,%d,%d,%d,%d],\"rssi\":%d, \"layer\":%d}", LOCAL_NAME,
                    on_off, work_mode, locked, curr_temp, set_temp, wind_speed, valve,
                    rssi, layer);

    ret = mwifi_write(NULL, &data_type, msg, size, true);
    printf("%d = %s\n", ret, msg);

    if (ret != MDF_OK)
        ESP_LOGE(TAG, "node > root error");

    return ret;
}

mdf_err_t return_value_to_root(int origin_cmd, int value)
{
    int size;
    char msg[MAX_MESSAGE_SIZE];
    mdf_err_t ret;
    mwifi_data_type_t data_type = {0};
    data_type.compression = true;

    size = snprintf(msg, MAX_MESSAGE_SIZE, "{\"device\":\"%s\", \"cmd\":%d, \"value\":%d}", LOCAL_NAME, origin_cmd, value);
    ret = mwifi_write(NULL, &data_type, msg, size, true);
    printf("%d = %s\n", ret, msg);

    if (ret != MDF_OK)
        ESP_LOGE(TAG, "node > root error");

    return ret;
}

mdf_err_t msg_parse(const char *msg, int rssi, int layer)
{
    mdf_err_t res = MDF_OK;
    int cmd_ret = -1;
    cJSON *json_root = NULL;
    cJSON *json_addr = NULL;
    cJSON *json_group = NULL;
    cJSON *json_cmd = NULL;
    cJSON *json_manual_cmd = NULL;

    json_root = cJSON_Parse(msg);
    if (!json_root)
    {
        ESP_LOGE(TAG, "cJSON_Parse, msg format error, data: %s", msg);
        return MDF_FAIL;
    }

    json_cmd = cJSON_GetObjectItem(json_root, "cmd");
    json_addr = cJSON_GetObjectItem(json_root, "dest");
    json_group = cJSON_GetObjectItem(json_root, "group");
    json_manual_cmd = cJSON_GetObjectItem(json_root, "manual");

    if (json_addr) // To specific device
    {
        if (strcmp(json_addr->valuestring, LOCAL_NAME) == 0)
        {
            if (json_manual_cmd)
            {
                if ((res = parse_manual_cmd(json_manual_cmd)) == MDF_FAIL)
                {
                    ESP_LOGE(TAG, "MANUAL CMD ERROR.");
                };
                goto end;
            }
            else if (json_cmd)
            {
                cmd_ret = control_ac_with_cmd(json_cmd->valueint);
                //
                report_to_root(rssi, layer);
                //
                if (cmd_ret >= 0)
                    return_value_to_root(json_cmd->valueint, cmd_ret);
                else if (cmd_ret < -1)
                {
                    ESP_LOGE(TAG, "CONTOL ERROR.");
                    res = MDF_FAIL;
                    goto end;
                }
            }
            else
            {
                ESP_LOGE(TAG, "Command not found.");
                res = MDF_FAIL;
                goto end;
            }
        }
        else
        {
            zm_broadcast(msg);
        }
    }
    else if (json_group) // To group or all devices
    {
        if (strcmp(json_group->valuestring, LOCAL_GROUP) == 0 || strcmp(json_group->valuestring, "all") == 0)
        {
            if (json_manual_cmd)
            {
                if ((res = parse_manual_cmd(json_manual_cmd)) == MDF_FAIL)
                {
                    ESP_LOGE(TAG, "MANUAL CMD ERROR.");
                };
                goto end;
            }
            else if (json_cmd)
            {
                cmd_ret = control_ac_with_cmd(json_cmd->valueint);
                //
                report_to_root(rssi, layer);
                //
                if (cmd_ret >= 0)
                    return_value_to_root(json_cmd->valueint, cmd_ret);
                else if (cmd_ret < -1)
                {
                    ESP_LOGE(TAG, "CONTOL ERROR.");
                    res = MDF_FAIL;
                    goto end;
                }
            }
            else
            {
                ESP_LOGE(TAG, "Command not found.");
                res = MDF_FAIL;
                goto end;
            }
        }

        zm_broadcast(msg);
    }
    else // Address not found
    {
        ESP_LOGE(TAG, "cJSON_Parse, address not found, data: %s", msg);
        res = MDF_FAIL;
        goto end;
    }

end:
    cJSON_Delete(json_root);
    return res;
}

mdf_err_t parse_manual_cmd(const cJSON *manuel_cmd)
{
    mdf_err_t res = MDF_OK;
    uint8_t cmd[8];
    cJSON *elem = NULL;

    if (!cJSON_IsArray(manuel_cmd))
    {
        ESP_LOGE(TAG, "cmd isn't an array.");
        res = MDF_FAIL;
        goto end;
    }
    if (cJSON_GetArraySize(manuel_cmd) != 8)
    {
        ESP_LOGE(TAG, "cmd size error.");
        res = MDF_FAIL;
        goto end;
    }
    for (int i = 0; i < 8; i++)
    {
        elem = cJSON_GetArrayItem(manuel_cmd, i);
        if (!cJSON_IsNumber(elem))
        {
            ESP_LOGE(TAG, "cmd element data type error.");
            res = MDF_FAIL;
            goto end;
        }
        cmd[i] = elem->valueint;
    }
    control_ac_with_rs485(cmd);

end:
    return res;
}