import threading
import queue
import time
# my own class for controlling LCD
from LCD import LCD

# Bluez gatt uart service (SERVER)
from bluetooth_uart_server.bluetooth_uart_server import ble_gatt_uart_loop

# extend this code so the value received via Bluetooth gets printed on the LCD
# (maybe together with you Bluetooth device name or Bluetooth MAC?)

def main():
    lcd_device = LCD()
    lcd_device.setup()
    i = 0
    rx_q = queue.Queue()
    tx_q = queue.Queue()
    device_name = "viola_rpi_bluetooth" # TODO: replace with your own (unique) device name
    threading.Thread(target=ble_gatt_uart_loop, args=(rx_q, tx_q, device_name), daemon=True).start()
    prev_incoming = 0
    while True:
        try:
            incoming = rx_q.get() # Wait for up to 1 second 
            if i == 0:
                lcd_device.display_message(f"Score:")
                i = 1

            if incoming!=prev_incoming:
                print("Score: {}".format(incoming))
                lcd_device.display_message(incoming, lcd_device.LCD_LINE_2)
                time.sleep(0.2)
                prev_incoming = incoming
        except Exception as e:
            pass # nothing in Q 

        # if i%5 == 0: # Send some data every 5 iterations
        #     tx_q.put("test{}".format(i))
        # i += 1
if __name__ == '__main__':
    main()


