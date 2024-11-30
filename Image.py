import numpy as np
from PIL import Image as PILImage


class Image:
    def __init__(self, image_data):
        self.image_data = image_data
        ft = np.fft.fft2(image_data)
        self.ft = np.fft.fftshift(ft)
        self.size = image_data.shape

    def resize(self, new_size):
        """
        Resize the image to a new size
        :param new_size: (width, height)
        :return:
        """
        self.image_data = np.array(PILImage.fromarray(self.image_data).resize(new_size))
        ft = np.fft.fft2(self.image_data)
        self.ft = np.fft.fftshift(ft)
        self.size = self.image_data.shape

    def get_ft_image(self, component):
        if component == "Real":
            data = self.get_real_part()
        elif component == "Imaginary":
            data = self.get_imaginary_part()
        elif component == "Magnitude":
            data = self.get_log_magnitude()
        else:
            data = self.get_phase()
        data = self.normalize(data)
        return data

    @staticmethod
    def normalize(data):
        data = data - data.min()
        data = data / data.max()
        data = data * 255
        data = data.astype(np.uint8)
        return data

    def get_real_part(self):
        return self.ft.real

    def get_imaginary_part(self):
        return self.ft.imag

    def get_log_magnitude(self):
        return np.log1p(self.get_magnitude())

    def get_magnitude(self):
        return np.abs(self.ft)

    def get_phase(self):
        return np.angle(self.ft)

    def changeBrightnessContrast(self, brightness, contrast):
        # could be slow due to fft, might need redesign
        self.image_data = self.image_data * contrast + brightness
        ft = np.fft.fft2(self.image_data)
        self.ft = np.fft.fftshift(ft)
        self.size = self.image_data.shape

    @staticmethod
    def from_file(file_path):
        image = PILImage.open(file_path)
        image = image.convert('L')
        image_data = np.array(image)
        return Image(image_data)

    @staticmethod
    def from_mixer():
        pass