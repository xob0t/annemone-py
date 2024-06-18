import ctypes
import time

ctypes.CDLL("./hidapi.dll")


class LEDController:
    known_pids = [0x8008, 0x8009, 0xA292, 0xA293]
    AnnePro2_layout = [
        {"key": "esc", "matrix_id": 0},
        {"key": "1", "matrix_id": 1},
        {"key": "2", "matrix_id": 2},
        {"key": "3", "matrix_id": 3},
        {"key": "4", "matrix_id": 4},
        {"key": "5", "matrix_id": 5},
        {"key": "6", "matrix_id": 6},
        {"key": "7", "matrix_id": 7},
        {"key": "8", "matrix_id": 8},
        {"key": "9", "matrix_id": 9},
        {"key": "0", "matrix_id": 10},
        {"key": "minus", "matrix_id": 11},
        {"key": "equals", "matrix_id": 12},
        {"key": "backspace", "matrix_id": 13},
        {"key": "tab", "matrix_id": 14},
        {"key": "q", "matrix_id": 15},
        {"key": "w", "matrix_id": 16},
        {"key": "e", "matrix_id": 17},
        {"key": "r", "matrix_id": 18},
        {"key": "t", "matrix_id": 19},
        {"key": "y", "matrix_id": 20},
        {"key": "u", "matrix_id": 21},
        {"key": "i", "matrix_id": 22},
        {"key": "o", "matrix_id": 23},
        {"key": "p", "matrix_id": 24},
        {"key": "lbracket", "matrix_id": 25},
        {"key": "rbracket", "matrix_id": 26},
        {"key": "backslash", "matrix_id": 27},
        {"key": "caps", "matrix_id": 28},
        {"key": "a", "matrix_id": 29},
        {"key": "s", "matrix_id": 30},
        {"key": "d", "matrix_id": 31},
        {"key": "f", "matrix_id": 32},
        {"key": "g", "matrix_id": 33},
        {"key": "h", "matrix_id": 34},
        {"key": "j", "matrix_id": 35},
        {"key": "k", "matrix_id": 36},
        {"key": "l", "matrix_id": 37},
        {"key": "semicolon", "matrix_id": 38},
        {"key": "apostrophe", "matrix_id": 39},
        {"key": "enter", "matrix_id": 40},
        {"key": "deadkey1", "matrix_id": None},
        {"key": "leftshift", "matrix_id": 41},
        {"key": "deadkey2", "matrix_id": None},
        {"key": "z", "matrix_id": 42},
        {"key": "x", "matrix_id": 43},
        {"key": "c", "matrix_id": 44},
        {"key": "v", "matrix_id": 45},
        {"key": "b", "matrix_id": 46},
        {"key": "n", "matrix_id": 47},
        {"key": "m", "matrix_id": 48},
        {"key": "comma", "matrix_id": 49},
        {"key": "dot", "matrix_id": 50},
        {"key": "slash", "matrix_id": 51},
        {"key": "rightshift", "matrix_id": 52},
        {"key": "deadkey3", "matrix_id": None},
        {"key": "leftctrl", "matrix_id": 53},
        {"key": "deadkey4", "matrix_id": None},
        {"key": "leftsuper", "matrix_id": 54},
        {"key": "leftalt", "matrix_id": 55},
        {"key": "deadkey5", "matrix_id": None},
        {"key": "deadkey6", "matrix_id": None},
        {"key": "space", "matrix_id": 56},
        {"key": "deadkey7", "matrix_id": None},
        {"key": "deadkey8", "matrix_id": None},
        {"key": "rightalt", "matrix_id": 57},
        {"key": "fn", "matrix_id": 58},
        {"key": "context", "matrix_id": 59},
        {"key": "rightctrl", "matrix_id": 60},
        {"key": "deadkey9", "matrix_id": None},
    ]

    service_data = [0, 123, 16, 65]
    static_message = [0, 0, 125]
    command_info = [32, 3, 255]

    def __init__(self):
        self.keyboard = self.initialize_keyboard()

    def initialize_keyboard(self):
        import hid

        keyboard_info = next(
            (
                item
                for item in hid.enumerate()
                if item["vendor_id"] == 0x04D9
                and item["interface_number"] == 1
                and item["product_id"] in self.known_pids
            ),
            None,
        )

        if keyboard_info is None:
            raise Exception("No compatible devices found")
        else:
            return hid.Device(path=keyboard_info["path"])

    def set_individual_keys(self, matrix_state):
        array_of_rgb_values = [
            matrix_state[key["key"]] if key["key"] in matrix_state else [0, 0, 0]
            for key in self.AnnePro2_layout
        ]
        messages = self.generate_multi_color(
            [rgb for sublist in array_of_rgb_values for rgb in sublist]
        )

        sent_bytes = 0
        for message in messages:
            sent_bytes += self.write(message)
        return sent_bytes

    def set_multi_color_led(self, led_matrix):
        led_matrix_flattened = [rgb for sublist in led_matrix for rgb in sublist]
        array_of_rgb_values = [
            led_matrix_flattened[key["matrix_id"]]
            if key["matrix_id"] is not None
            else [0, 0, 0]
            for key in self.AnnePro2_layout
        ]
        messages = self.generate_multi_color(
            [rgb for sublist in array_of_rgb_values for rgb in sublist]
        )

        sent_bytes = 0
        for message in messages:
            sent_bytes += self.write(message)
        return sent_bytes

    def generate_multi_color(self, array_of_rgb_values):
        real_command_info_length = len(self.command_info) + 1
        max_message_length = 55 - real_command_info_length
        array_of_rgb_values_copy = array_of_rgb_values[:]
        messages_to_send_amount = (
            len(array_of_rgb_values_copy) + max_message_length - 1
        ) // max_message_length
        val_1 = len(array_of_rgb_values_copy) % max_message_length
        val_2 = max_message_length if val_1 == 0 else val_1
        hid_command = []

        for p in range(messages_to_send_amount):
            e = (messages_to_send_amount << 4) + p
            a = (
                val_2 + real_command_info_length
                if messages_to_send_amount - 1 == p
                else max_message_length + real_command_info_length
            )
            hid_command.append(
                self.service_data
                + [e, a]
                + self.static_message
                + self.command_info
                + [2]
                + array_of_rgb_values_copy[:max_message_length]
            )
            array_of_rgb_values_copy = array_of_rgb_values_copy[max_message_length:]

        return hid_command

    def set_single_color_led(self, rgb):
        return self.write(self.generate_one_color(rgb))

    def generate_one_color(self, rgb_color):
        return (
            self.service_data
            + [16, 7]
            + self.static_message
            + self.command_info
            + [1]
            + rgb_color
        )

    def write(self, message):
        byte_message = bytes(message)
        start_time = time.time()
        # Needed due to Anne Pro 2 ignoring commands when they're sent faster than 50ms apart from each other.
        while time.time() < start_time + 0.05:
            pass

        return self.keyboard.write(byte_message)


# if __name__ == "__main__":
#     controller = LEDController()
#     blue_color = [0, 255, 255]
#     key_colors = {"space": blue_color}
#     controller.set_individual_keys(key_colors)
