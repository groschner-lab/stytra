from stytra import Stytra, Protocol
from stytra.stimulation.stimuli.visual import (
    VideoStimulus
)
from lightparam import Param
import os
from pathlib import Path
import pandas as pd


class VideoProtocol(Protocol):
    name = "video_stimulus_concentric_rings"

    def __init__(self):
        super().__init__()



        # List all stimuli
        json_paths = r"C:/Users/grolab/PycharmProjects/stytra/stytra/birte_experiments/assets/stim_videos/20220909_rings_and_black_screen/"
        json_files = [file for file in os.listdir(json_paths) if file.endswith('.json')]
        dfs = []  # an empty list to store the data frames
        for file in json_files:
            data = pd.read_json(json_paths + file, orient='index')  # read data frame from json file
            filename = Path(file).stem
            name = pd.DataFrame.from_dict({"name": filename}, orient='index')
            full = pd.concat([data, name])
            dfs.append(full)  # append the data frame to the list

        temp = pd.concat(dfs, axis=1)  # concatenate all the data frames in the list.
        metadata_stimuli = temp.transpose().reset_index().drop(columns=['index'])

        unique_stimuli = metadata_stimuli.copy()
        nunique = unique_stimuli.apply(pd.Series.nunique)
        cols_to_drop = nunique[nunique == 1].index
        unique_stimuli = unique_stimuli.drop(cols_to_drop, axis=1)
        cols_to_sort = unique_stimuli.drop(columns="name").columns.values.tolist()
        unique_stimuli = unique_stimuli.sort_values(by=cols_to_sort).reset_index().drop(columns="index")

        unique_stimuli_list = unique_stimuli.astype(str).apply(lambda x: x.name + '_' + x)
        unique_stimuli_list = unique_stimuli_list.drop(columns='name')
        unique_stimuli_list = unique_stimuli_list.values.flatten().tolist()

        self.stimulus = Param(value=unique_stimuli_list[0], limits=unique_stimuli_list)
        self.json_paths = json_paths
        self.unique_stimuli_list = unique_stimuli_list
        self.unique_stimuli = unique_stimuli
        self.metadata_stimuli = metadata_stimuli

    def get_stim_sequence(self):
        stimuli = []
        stimulus = self.stimulus
        stimulus_index = self.unique_stimuli_list.index(stimulus)
        video_name = self.unique_stimuli.loc[stimulus_index, 'name']
        path = 'stim_videos/20220909_rings_and_black_screen/' + video_name + '.mp4'

        index = self.unique_stimuli_list.index(stimulus)
        name_stimulus = self.unique_stimuli.loc[index, 'name']  # used in queries
        framerate = float(self.metadata_stimuli.query("name == @name_stimulus").fps)
        video_duration = float(self.metadata_stimuli.query("name == @name_stimulus").video_duration)
        resolution_reduction_factor = float(self.metadata_stimuli.query("name == @name_stimulus").resolution_decreasing_factor)

        stimuli.append(VideoStimulus(video_path=path, framerate=framerate, duration=video_duration, resolution_reduction_factor=resolution_reduction_factor))

        return stimuli


if __name__ == "__main__":
    st = Stytra(protocol=VideoProtocol())
