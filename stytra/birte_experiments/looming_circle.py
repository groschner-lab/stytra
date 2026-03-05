import numpy as np
import pandas as pd
import math

from stytra import Stytra
from stytra.stimulation import Protocol
from stytra.stimulation.stimuli import InterpolatedStimulus, CurvedScreenCircleStimulus, CombinerStimulus, TriggerSquare
from lightparam import Param


class LoomingStimulus(InterpolatedStimulus, CurvedScreenCircleStimulus):
    name = "looming_curved_screen_stimulus"


class CombinedLoomingTriggerPixel(Protocol):
    name = "combined_looming_curved_screen_triggerpixel_protocol"

    def __init__(self):

        super().__init__()



        self.x_pos = Param(0.5, limits=(0.0, 1.0))
        self.y_pos = Param(0.5, limits=(0.0, 1.0))
        self.ratio_lv = Param(100, limits=(1, 1000))
        self.max_loom_diameter = Param(180, limits=(1, 180))
        self.contrast = Param(50, limits=(-255, 255))
        self.looming_duration = Param(25, limits=(1, 1000.0))

    def get_stim_sequence(self):
        start_trigger_duration = 2
        ratio_lv = self.ratio_lv





        looming_duration = self.looming_duration
        contrast = self.contrast
        max_loom_diameter = self.max_loom_diameter

        stimuli = []

        # Looming stimulus
        time = np.arange(-looming_duration, 0, 0.0005)
        df = pd.DataFrame(dict(time_ms=time * 1000))
        df['angle'] = df.apply(lambda row: 2 * math.atan(-ratio_lv / row.time_ms) * (180 / np.pi), axis=1)
        df['include'] = df['angle'].apply(lambda x: 'True' if x <= max_loom_diameter else 'False')
        df_include = df.query("include == 'True'")
        df_include['radius'] = df_include['angle'] / 2
        radius_df = df_include.drop(columns=['include', 'angle']).rename(columns={'time_ms': 't'})
        radius_df['t'] = radius_df['t'] / 1000 + looming_duration + start_trigger_duration
        radius_df = radius_df.reset_index(drop=True)

        bc = 127.5 + contrast/2
        cc = 127.5 - contrast/2

        stimuli_loom = LoomingStimulus(
                background_color=(bc, bc, bc),
                circle_color=(cc, cc, cc),
                df_param=radius_df,
                origin=(self.x_pos, self.y_pos),
                curved_screen=True
            )


        # Trigger pixel
        last_t = radius_df.iloc[-1, 0]


        
        active_df = pd.DataFrame(
            dict(
                t=[0, 1, 1, 1.2, 1.2, 1.3, 1.3, 1.5, 1.5, 1.6, 1.6, 1.8, 1.8, start_trigger_duration,
                   last_t + 3, last_t + 3, last_t + 3.2, last_t + 3.2,
                   last_t + 3.3, last_t + 3.3, last_t + 3.5, last_t + 3.5, last_t + 4],
                active=[False, False, True, True, False, False, True, True, False, False, True, True, False, False,
                        False, True, True, False, False, True, True, False, False]
            )
        )

        triggerpixel = TriggerSquare(df_param=active_df)

        stimuli.append(CombinerStimulus([stimuli_loom, triggerpixel]))
        return stimuli


if __name__ == "__main__":
    # We make a new instance of Stytra with this protocol as the only option:

    s = Stytra(protocol=CombinedLoomingTriggerPixel())
