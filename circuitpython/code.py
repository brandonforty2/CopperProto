import time

import adafruit_mpr121
import board
import busio  # cap
import displayio  # display
import framebufferio  # display
import rgbmatrix  # display


class CopperProto:
    def __init__(self,
                 mpr_boop_pin,
                 display_folder,
                 display_bit_depth,
                 display_width,
                 display_height,
                 loop_seconds=1,
                 polling_rate_seconds=1,
                 ):
        self.i2c = None
        self.mpr121 = None
        self.display = None

        self.mpr_boop_pin = mpr_boop_pin
        self.display_folder = display_folder
        self.display_bit_depth = display_bit_depth
        self.display_width = display_width
        self.display_height = display_height

        self.loop_seconds = loop_seconds
        self.polling_rate_seconds = polling_rate_seconds

        self.setup_i2c()
        self.setup_capacitive()
        self.setup_display()

    def setup_i2c(self):
        assert self.i2c is None, "I2C being re-initialized"
        self.i2c = busio.I2C(board.SCL, board.SDA)

    def setup_capacitive(self):
        assert self.mpr121 is None, "mpr121 being re-initialized"
        assert self.i2c is not None, "I2C not yet initialized"
        self.mpr121 = adafruit_mpr121.MPR121(self.i2c)

    def setup_display(self):
        assert self.display is None, "Display being re-initialized"
        addr_pins = [board.MTX_ADDRA, board.MTX_ADDRB, board.MTX_ADDRC, board.MTX_ADDRD]
        rgb_pins = [
            board.MTX_R1,
            board.MTX_G1,
            board.MTX_B1,
            board.MTX_R2,
            board.MTX_G2,
            board.MTX_B2,
        ]
        clock_pin = board.MTX_CLK
        latch_pin = board.MTX_LAT
        oe_pin = board.MTX_OE

        displayio.release_displays()
        matrix = rgbmatrix.RGBMatrix(
            width=self.display_width,
            height=self.display_height,
            bit_depth=self.display_bit_depth,
            rgb_pins=rgb_pins,
            addr_pins=addr_pins,
            clock_pin=clock_pin,
            latch_pin=latch_pin,
            output_enable_pin=oe_pin
        )
        self.display = framebufferio.FramebufferDisplay(matrix)

    def get_boop(self) -> bool:
        assert self.mpr121 is not None, "mpr121 not yet initialized"
        return self.mpr121[self.mpr_boop_pin].value

    def display_image(self, image_name):
        assert self.display is not None, "Display not yet initialized"
        bitmap = displayio.OnDiskBitmap(open(f"{self.display_folder}/{image_name}.bmp", "rb"))
        tilegrid = displayio.TileGrid(
            bitmap,
            pixel_shader=bitmap.pixel_shader,
            tile_width=bitmap.width,
            tile_height=bitmap.height
        )

        group = displayio.Group()
        group.append(tilegrid)
        self.display.show(group)

    def run(self):
        # Check each sensor and see what their values are
        # Show face while sensor is depressed

        while True:
            # capacitive boop
            if self.get_boop():
                self.display_image("boop")
                while self.get_boop():
                    time.sleep(self.polling_rate_seconds)

            self.display_image("default")
            time.sleep(self.loop_seconds)


if __name__ == "__main__":
    copper = CopperProto(
        0,
        "faces",
        6,
        128,
        32,
        loop_seconds=1,
        polling_rate_seconds=1
    )
    copper.run()
