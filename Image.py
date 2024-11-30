import numpy as np
from PIL import Image as PILImage


class Image:
    def __init__(self, image_data):
        self.image_data = image_data
        self.ft = np.fft.fft2(image_data)
        self.size = image_data.shape

    def resize(self, new_size):
        """
        Resize the image to a new size
        :param new_size: (width, height)
        :return:
        """
        self.image_data = np.array(PILImage.fromarray(self.image_data).resize(new_size))
        self.ft = np.fft.fft2(self.image_data)
        self.size = self.image_data.shape
        pass

    def get_real_part(self):
        return self.ft.real

    def get_imaginary_part(self):
        return self.ft.imag

    def get_magnitude(self):
        return np.abs(self.ft)

    def get_phase(self):
        return np.angle(self.ft)

    @staticmethod
    def from_file(file_path):
        image = PILImage.open(file_path)
        image = image.convert('L')
        image_data = np.array(image)
        return Image(image_data)

    @staticmethod
    def from_mixer():
        pass