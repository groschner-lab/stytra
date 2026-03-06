from stytra import Stytra, Protocol
from stytra.stimulation.stimuli.visual import (
    VideoStimulus
)
from lightparam import Param
import os
from pathlib import Path
import pandas as pd


class VideoProtocol(Protocol):
    name = "video_stimulus_gratings_loop"
    def __init__(self):
        super().__init__()
        self.duration = Param(30, limits=(0, 10000))  # in seconds

        # List all stimuli
        json_paths = r"assets/stim_videos/20260306_gratings_loop/"
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
        unique_stimuli = unique_stimuli.astype(str).apply(lambda x: x.name + '_' + x)
        unique_stimuli["name"] = unique_stimuli["name"].str.replace('name_', '')
        unique_stimuli["combined"] = unique_stimuli.drop(columns='name').astype(str).apply(lambda x: '_'.join(x), axis=1)
        unique_stimuli = unique_stimuli[["name", "combined"]]

        unique_stimuli_list = unique_stimuli["combined"].values.flatten().tolist()

        self.stimulus = Param(value=unique_stimuli_list[0], limits=unique_stimuli_list)
        self.json_paths = json_paths
        self.unique_stimuli_list = unique_stimuli_list
        self.unique_stimuli = unique_stimuli
        self.metadata_stimuli = metadata_stimuli

    def get_stim_sequence(self):
        stimuli = []
        stimulus = self.stimulus  # From a stale config?
        duration = self.duration

        # Check if restored stimulus value is in the list of valid options!
        # If not, fall back to the first item in the list!
        if stimulus not in self.unique_stimuli_list:
            print(f"Warning: Stored stimulus '{stimulus}' is not valid for this protocol.")
            stimulus = self.unique_stimuli_list[0]  # Fallback to a valid default
            print(f"Falling back to default stimulus: '{stimulus}'")

        stimulus_index = self.unique_stimuli_list.index(stimulus)
        print(f"Using stimulus index: {stimulus_index}")

        video_name = self.unique_stimuli.loc[stimulus_index, 'name']

        # os.path.join avoids issues with slashes:
        path = os.path.join('stim_videos', '20260306_gratings_loop', video_name + '.mp4')

        name_stimulus = self.unique_stimuli.loc[stimulus_index, 'name']
        framerate = float(self.metadata_stimuli.query("name == @name_stimulus").fps.iloc[0])
        video_duration = duration #float(self.metadata_stimuli.query("name == @name_stimulus").video_duration.iloc[0])
        resolution_reduction_factor = float(
            self.metadata_stimuli.query("name == @name_stimulus").resolution_decreasing_factor.iloc[0])

        stimuli.append(VideoStimulus(video_path=path, framerate=framerate, duration=video_duration,
                                     resolution_reduction_factor=resolution_reduction_factor, loop=True))

        return stimuli


if __name__ == "__main__":
    st = Stytra(protocol=VideoProtocol())
