import os

from PIL import Image, ImageDraw, ImageFont
from waveshare_epd import epd2in66

from data.plot import Plot
from presentation.observer import Observer

SCREEN_HEIGHT = epd2in66.EPD_WIDTH  # 152
SCREEN_WIDTH = epd2in66.EPD_HEIGHT  # 296

FONT_SMALL = ImageFont.truetype(
    os.path.join(os.path.dirname(__file__), os.pardir, 'Roses.ttf'), 8)
FONT_LARGE = ImageFont.truetype(
    os.path.join(os.path.dirname(__file__), os.pardir, 'PixelSplitter-Bold.ttf'), 26)

class Epd2in66(Observer):

    def __init__(self, observable, mode):
        super().__init__(observable=observable)
        self.epd = epd2in66.EPD()
        self.screen_image = self._init_display(self.epd)
        self.screen_draw = ImageDraw.Draw(self.screen_image)
        self.mode = mode

    @staticmethod
    def _init_display(epd):
        epd.init(1)
        epd.Clear()
        screen_image = Image.new('1', (SCREEN_WIDTH, SCREEN_HEIGHT), 255)
        epd.display(epd.getbuffer(screen_image))
        epd.init(1)
        return screen_image

    def form_image(self, prices, screen_draw):
        screen_draw.rectangle((0, 0, SCREEN_WIDTH, SCREEN_HEIGHT), fill="#ffffff")
        screen_draw = self.screen_draw
        if self.mode == "candle":
            Plot.candle(prices, size=(SCREEN_WIDTH - 45, 120), position=(41, 0), draw=screen_draw)
        else:
            last_prices = [x[3] for x in prices]
            Plot.line(last_prices, size=(SCREEN_WIDTH - 42, 115), position=(42, 0), draw=screen_draw)

        flatten_prices = [item for sublist in prices for item in sublist]
        Plot.y_axis_labels(flatten_prices, FONT_SMALL, (0, 0), (38, 115), draw=screen_draw)
        screen_draw.line([(10, 125), (SCREEN_WIDTH-10, 125)]) #esquerra a dreta
        screen_draw.line([(39, 4), (39, 120)]) #separador entre minmax i chart
        screen_draw.line([(85, 130), (85, SCREEN_HEIGHT)]) #separador entre moneda i valor
        Plot.caption(flatten_prices[len(flatten_prices) - 1], 126, SCREEN_WIDTH, FONT_LARGE, screen_draw)

    def update(self, data):
        self.form_image(data, self.screen_draw)
        screen_image_rotated = self.screen_image.rotate(180)
        # TODO: add a way to switch bewen partial and full update
        # epd.presentation(epd.getbuffer(screen_image_rotated))
        self.epd.display(self.epd.getbuffer(screen_image_rotated))

    @staticmethod
    def close():
        epd2in66.epdconfig.module_exit()
