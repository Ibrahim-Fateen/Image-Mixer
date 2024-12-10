from PySide6.QtCore import QObject, Signal, QThread

import numpy as np
from Image import Image
from logger_config import setup_logger

logger = setup_logger(__name__)


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
            logger.debug(f"Region received as (x, y, w, h): {x}, {y}, {w}, {h}")
            part_selected = "low frequencies" if inside_is_selected else "high frequencies"
            logger.debug(f"Region selected: {part_selected}")
            if inside_is_selected:
                mask = np.zeros_like(self.images[0].image_data)
                mask[y:y + h, x:x + w] = 1
            else:
                mask = np.ones_like(self.images[0].image_data)
                mask[y:y + h, x:x + w] = 0
        return mask

    def mix_mag_phase(self, weights: []):
        """
        :param weights: A list of weights tuples for each image.
        The first element of the tuple is the magnitude weight and the second element is the phase weight.
            eg: [(0.3, 0.7), (0.7, 0.3)]
        :return: Image
        """
        mag_weights = self.__get_adjusted_weights([weight[0] for weight in weights])
        phase_weights = self.__get_adjusted_weights([weight[1] for weight in weights])
        mixed_magnitude = self.__mix_mag(mag_weights)
        self.first_component_mixed.emit()
        logger.info("Magnitude mixed")
        mixed_phase = self.__mix_phase(phase_weights)
        self.second_component_mixed.emit()
        logger.info("Phase mixed")
        complex_ft = mixed_magnitude * np.exp(1j * mixed_phase)
        complex_ft = np.fft.ifftshift(complex_ft)
        self.total_ft_found.emit()
        logger.info("Resultant FT found")
        image = Image.from_foureir_domain(complex_ft)
        self.ifft_computed.emit()
        logger.info("IFFT computed")
        return image

    def mix_real_imaginary(self, weights):
        """
        :param weights: A list of weights tuples for each image.
        The first element of the tuple is the real weight and the second element is the imaginary weight.
            eg: [(0.3, 0.7), (0.7, 0.3)]
        :return: Image
        """
        real_weights = self.__get_adjusted_weights([weight[0] for weight in weights])
        imaginary_weights = self.__get_adjusted_weights([weight[1] for weight in weights])
        mixed_real = self.__mix_real(real_weights)
        self.first_component_mixed.emit()
        logger.info("Real parts mixed")
        mixed_imaginary = self.__mix_imaginary(imaginary_weights)
        self.second_component_mixed.emit()
        logger.info("Imaginary parts mixed")
        complex_ft = mixed_real + 1j * mixed_imaginary
        complex_ft = np.fft.ifftshift(complex_ft)
        self.total_ft_found.emit()
        logger.info("Resultant FT found")
        image = Image.from_foureir_domain(complex_ft)
        self.ifft_computed.emit()
        logger.info("IFFT computed")
        return image

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
        real_parts = [image.get_real_part() * self.mask for image in self.images]
        mixed_real = np.zeros_like(real_parts[0])
        for real, weight in zip(real_parts, weights):
            mixed_real += real * weight
        return mixed_real

    def __mix_imaginary(self, weights):
        imaginary_parts = [image.get_imaginary_part() * self.mask for image in self.images]
        mixed_imaginary = np.zeros_like(imaginary_parts[0])
        for imaginary, weight in zip(imaginary_parts, weights):
            mixed_imaginary += imaginary * weight
        return mixed_imaginary

    @staticmethod
    def __get_adjusted_weights(weights):
        total = sum(weights)
        return [weight / total for weight in weights]


class MixingThread(QThread):
    result_ready = Signal(object)
    error_occurred = Signal(str)

    def __init__(self, mixer, weights, mode):
        super().__init__()
        self.mixer = mixer
        self.weights = weights
        self.mode = mode

    def run(self):
        try:
            if self.mode == 0:
                result_image = self.mixer.mix_mag_phase(self.weights)
            else:
                result_image = self.mixer.mix_real_imaginary(self.weights)
            self.result_ready.emit(result_image)
        except Exception as e:
            self.error_occurred.emit(str(e))
