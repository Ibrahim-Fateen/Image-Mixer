from PySide6.QtCore import QObject, Signal

import numpy as np
from Image import Image


class Mixer(QObject):
    first_component_mixed = Signal()
    second_component_mixed = Signal()
    total_ft_found = Signal()
    ifft_computed = Signal()

    def __init__(self, images: [Image], region=None):
        """
        :param images:
        :param region: a tuple containing (inside_is_selected boolean, (x, y, width, height))
        """
        super().__init__()
        self.images = images
        self.mask = self.__get_mask(region)

    def __get_mask(self, region):
        mask = np.ones_like(self.images[0].image_data)
        if region:
            inside_is_selected, x, y, w, h = region
            if inside_is_selected:
                mask = np.zeros_like(self.images[0].image_data)
                mask[y:y + h, x:x + w] = 1
            else:
                mask = np.ones_like(self.images[0].image_data)
                mask[y:y + h, x:x + w] = 0
        return mask

    def mix_mag_phase(self, weights: []):
        """
        :param weights: A list of weights dict for each image.
            eg: [{"Magnitude": 0.3, "Phase": 0.7}, {"Magnitude": 0.7, "Phase": 0.3}]
        :return: Image
        """
        mag_weights = [weight[0] for weight in weights]
        phase_weights = [weight[1] for weight in weights]
        mixed_magnitude = self.__mix_mag(mag_weights)
        self.first_component_mixed.emit()
        mixed_phase = self.__mix_phase(phase_weights)
        self.second_component_mixed.emit()
        complex_ft = mixed_magnitude * np.exp(1j * mixed_phase)
        complex_ft = np.fft.ifftshift(complex_ft)
        self.total_ft_found.emit()
        image = Image.from_foureir_domain(complex_ft)
        self.ifft_computed.emit()
        return image

    def mix_real_imaginary(self, weights):
        pass

    def __mix_phase(self, weights):
        """
        Mix the phase of the images based on a weighted vector approach
        :param weights: Array of weights between 0 and 1, must match the number of images provided
        :return: The resultant complex matrix combining the phases of all images provided
        """
        phases = [(image.get_phase() * self.mask).astype(float) for image in self.images]
        phase_vectors = [np.exp(1j * phase) for phase in phases]
        mixed_phase_vector = np.sum([vec * weight for vec, weight in zip(phase_vectors, weights)], axis=0)
        return np.angle(mixed_phase_vector)

    def __mix_mag(self, weights):
        magnitudes = [image.get_magnitude() * self.mask for image in self.images]
        mixed_magnitude = np.zeros_like(magnitudes[0])
        for magnitude, weight in zip(magnitudes, weights):
            mixed_magnitude += magnitude * weight
        return mixed_magnitude

    def __mix_real(self, weights):
        pass

    def __mix_imaginary(self, weights):
        pass
