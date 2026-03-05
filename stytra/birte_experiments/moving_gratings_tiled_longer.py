import numpy as np
import pandas as pd
from stytra import Stytra
from stytra.stimulation import Protocol
from stytra.stimulation.stimuli import SeamlessImageStimulus, InterpolatedStimulus, CombinerStimulus
import qimage2ndarray
from lightparam import Param


def create_pattern(mm_px, wave_shape, wave_period, color_1, color_2, path):
    width = int(wave_period / mm_px)
    x = np.arange(width) / width
    xx, yy = np.meshgrid(x, x)  # grid of points

    W = np.sin(xx * 2 * np.pi)
    W = ((W + 1) / 2)[:, :, np.newaxis]  # normalize and add color axis

    if wave_shape == "square":
        W = (W > 0.5).astype(np.uint8)  # binarize for square gratings

    # Multiply by color:
    _pattern = W * color_1 + (1 - W) * color_2

    _qbackground = qimage2ndarray.array2qimage(_pattern)
    _qbackground.save(path)


class CombinedMovingTiledGrating(Protocol):
    name = "moving_gratings_tiled_longer"

    def __init__(self):
        super().__init__()
        self.grating_shape = Param("square", limits=["sine", "square"])
        self.grating_period_deg = Param(45, limits=(1, 1000))  # in degrees
        self.grating_velocity_deg_s = Param(45.0, limits=(0.0, 1000.0))
        self.contrast = Param(100.0, limits=(0, 255))
        self.duration = Param(30, limits=(0,10000)) # in seconds
        self.rotation = Param(0, limits=(0,360)) # in degrees

    def get_stim_sequence(self):
        shape = self.grating_shape
        contrast = self.contrast

        grating_period_deg = self.grating_period_deg
        grating_velocity_deg = self.grating_velocity_deg_s
        duration = self.duration
        rotation = np.deg2rad(-self.rotation)

        mm_px = 0.0825  # hardcoded for use with curved Royole screen (1920 x 1440)
        w = 1920

        grating_period_mm = grating_period_deg / 180 * w * mm_px
        velocity_mm = grating_velocity_deg / 180 * w * mm_px * 2 # the 2 doesn't make sense to me but otherwise it's too slow

        c1 = 127.5 + contrast / 2
        c2 = 127.5 - contrast / 2

        Stim = type("stim", (SeamlessImageStimulus, InterpolatedStimulus), {})

        create_pattern(mm_px=mm_px, wave_shape=shape, wave_period=grating_period_mm, color_1=(c1, c1, c1), color_2=(c2, c2, c2),
                       path="assets/generated_pattern.png")

        # Use two points to specify the velocity step to be interpolated:
        t = [0, duration]
        vel = np.array([velocity_mm, velocity_mm])
        df = pd.DataFrame(dict(t=t, vel_x=vel))

        s_a = Stim(
                background="generated_pattern.png",
                df_param=df,
                # clip_mask=[0, 0, 1, 1],
                rotation=rotation)

        stimuli = [s_a]
        return stimuli


if __name__ == "__main__":
    st = Stytra(protocol=CombinedMovingTiledGrating())

