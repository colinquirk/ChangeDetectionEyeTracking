from __future__ import division
from __future__ import print_function

import sys

import psychopy

import eyelinker

import changedetection


data_fields = [
    'Block',
    'Trial',
    'Timestamp',
    'FreeGaze',
    'Condition',
    'SetSize',
    'RT',
    'CRESP',
    'RESP',
    'ACC',
    'LocationTested',
    'Locations',
    'SampleColors',
    'TestColors',
]


class EyeTrackingKtask(changedetection.Ktask):
    def __init__(self, **kwargs):
        self.tracker = None

        super(EyeTrackingKtask, self).__init__(**kwargs)

    def run(self):
        self.chdir(self)

        ok = self.get_experiment_info_from_dialog(self.questionaire_dict)

        if not ok:
            print('Experiment has been terminated.')
            sys.exit(1)

        self.save_experiment_info()
        self.open_csv_data_file()
        self.open_window(screen=0)
        self.display_text_screen('Loading...', wait_for_input=False)

        for instruction in self.instruct_text:
            self.display_text_screen(text=instruction)

        for block_num in range(self.number_of_blocks):
            block = self.make_block()
            for trial_num, trial in enumerate(block):
                data = self.run_trial(trial, block_num, trial_num)
                self.send_data(data)

            self.save_data_to_csv()

            if block_num + 1 != self.number_of_blocks:
                self.display_break()

        self.display_text_screen(
            'The experiment is now over, please get your experimenter.',
            bg_color=[0, 0, 255], text_color=[255, 255, 255])

        self.quit_experiment()


experiment = EyeTrackingKtask(
    experiment_name='EyeTrackingChangeDetection',
    data_fields=data_fields,
    monitor_distance=changedetection.distance_to_monitor
)

print(experiment.data_fields)
