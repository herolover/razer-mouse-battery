#include <libusb.h>

#include <array>
#include <format>
#include <iostream>
#include <thread>

union transaction_id_union {
    unsigned char id;
    struct transaction_parts {
        unsigned char device : 3;
        unsigned char id : 5;
    } parts;
};

union command_id_union {
    unsigned char id;
    struct command_id_parts {
        unsigned char direction : 1;
        unsigned char id : 7;
    } parts;
};

struct razer_report {
    unsigned char status;
    union transaction_id_union transaction_id; /* */
    unsigned short remaining_packets; /* Big Endian */
    unsigned char protocol_type; /*0x0*/
    unsigned char data_size;
    unsigned char command_class;
    union command_id_union command_id;
    unsigned char arguments[80];
    unsigned char crc;/*xor'ed bytes of report*/
    unsigned char reserved; /*0x0*/
};

unsigned char razer_calculate_crc(struct razer_report* report)
{
    /*second to last byte of report is a simple checksum*/
    /*just xor all bytes up with overflow and you are done*/
    unsigned char crc = 0;
    unsigned char *_report = (unsigned char*)report;

    unsigned int i;
    for(i = 2; i < 88; i++) {
        crc ^= _report[i];
    }

    return crc;
}

razer_report send_request(libusb_device_handle* device_handle, unsigned char command_class, unsigned char command_id, unsigned char data_size)
{
    constexpr uint16_t index = 0;
    constexpr uint16_t value = 0x300;
    constexpr size_t timeout_ms = 100;
    constexpr size_t wait_ms = 60;

    razer_report request{};
    request.transaction_id.id = 0xff;
    request.command_class = command_class;
    request.command_id.id = command_id;
    request.data_size = data_size;
    request.crc = razer_calculate_crc(&request);

    auto res = libusb_control_transfer(
        device_handle,
        LIBUSB_REQUEST_TYPE_CLASS | LIBUSB_RECIPIENT_INTERFACE | LIBUSB_ENDPOINT_OUT,
        LIBUSB_REQUEST_SET_CONFIGURATION,
        value,
        index,
        reinterpret_cast<unsigned char *>(&request),
        sizeof(request),
        timeout_ms);
    if (res <= 0)
    {
        throw std::runtime_error(std::format("Request failed: {}", res));
    }

    std::this_thread::sleep_for(std::chrono::milliseconds(wait_ms));

    razer_report response{};
    res = libusb_control_transfer(
        device_handle,
        LIBUSB_REQUEST_TYPE_CLASS | LIBUSB_RECIPIENT_INTERFACE | LIBUSB_ENDPOINT_IN,
        0x01,
        value,
        index,
        reinterpret_cast<unsigned char *>(&response),
        sizeof(response),
        timeout_ms);
    if (res <= 0)
    {
        throw std::runtime_error(std::format("Response failed: {}", res));
    }

    return response;
}

double get_battery_level(libusb_device_handle* device_handle)
{
    auto response = send_request(device_handle, 0x07, 0x80, 0x02);
    return response.arguments[1] / 255.0 * 100.0;
}

bool get_is_charging(libusb_device_handle* device_handle)
{
    auto response = send_request(device_handle, 0x07, 0x84, 0x02);
    return response.arguments[1] != 0;
}

int main(int argc, char* argv[])
{
    libusb_context* context = nullptr;
    libusb_init(&context);

    auto device_handle = libusb_open_device_with_vid_pid(context, 0x1532, 0x007b);
    if (device_handle == nullptr)
    {
        std::cerr << "Device not found" << std::endl;
        return -1;
    }

    double battery_level = get_battery_level(device_handle);
    bool is_charging = get_is_charging(device_handle);
    std::cout << std::format("Battery level: {}\nIs charging: {}", battery_level, is_charging) << std::endl;

    libusb_close(device_handle);

    libusb_exit(context);

    return 0;
}
