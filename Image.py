import numpy as np
from PIL import Image as PILImage


class Image:
    def __init__(self, image_data):
        self.image_data = image_data
        self.modified_image_data = image_data.copy()
        ft = np.fft.fft2(image_data)
        self.ft = np.fft.fftshift(ft)
        self.modified_ft = self.ft.copy()
        self.size = image_data.shape

    def resize(self, new_size):
        """
        Resize the image to a new size
        :param new_size: (width, height)
        :return:
        """
        self.image_data = np.array(PILImage.fromarray(self.image_data).resize(new_size))
        self.modified_image_data = self.image_data.copy()
        ft = np.fft.fft2(self.modified_image_data)
        self.ft = np.fft.fftshift(ft)
        self.modified_ft = self.ft.copy()
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
        return self.modified_ft.real

    def get_log_real(self):
        data = self.get_real_part()
        data = data - data.min()
        return np.log1p(data)

    def get_log_imaginary(self):
        data = self.get_imaginary_part()
        data = data - data.min()
        return np.log1p(data)

    def get_imaginary_part(self):
        return self.modified_ft.imag

    def get_log_magnitude(self):
        return np.log1p(self.get_magnitude())

    def get_magnitude(self):
        return np.abs(self.modified_ft)

    def get_phase(self):
        return np.angle(self.modified_ft)

    def changeBrightnessContrast(self, brightness, contrast):
        mean = np.mean(self.image_data)
        self.modified_ft = self.ft.copy()
        (self - mean) * contrast + mean + brightness

    def __add__(self, other):
        self.modified_image_data = (self.image_data + other).astype(np.uint8)
        # assume no clipping occurred
        # add 2 * pi * other * delta(w)  (DC component) to the ft
        dc_index = tuple(x // 2 for x in self.size)
        self.modified_ft[dc_index] += 2 * np.pi * other
        return self

    def __sub__(self, other):
        self.modified_image_data = (self.image_data - other).astype(np.uint8)
        # assume no clipping occurred
        # subtract 2 * pi * other * delta(w)  (DC component) to the ft
        dc_index = tuple(x // 2 for x in self.size)
        self.modified_ft[dc_index] -= 2 * np.pi * other
        return self

    def __mul__(self, other):
        self.modified_image_data = (self.image_data * other).astype(np.uint8)
        self.modified_ft *= other
        return self

    def get_image_data(self):
        return np.clip(self.modified_image_data, 0, 255).astype(np.uint8)

    @staticmethod
    def from_file(file_path):
        image = PILImage.open(file_path)
        image = image.convert('L')
        image_data = np.array(image)
        return Image(image_data)

    @staticmethod
    def from_foureir_domain(ft_array):
        inverse = Image.normalize(np.abs(np.fft.ifft2(ft_array)))
        return Image(inverse)

    @staticmethod
    def placeholder_image():
        return Image.from_file("UI/placeholder.jpg")
