from PySide6.QtCore import QThread, Signal


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
