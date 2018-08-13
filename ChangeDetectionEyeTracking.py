from __future__ import division
from __future__ import print_function

import sys
import random

import psychopy

import eyelinker

import changedetection


data_fields = [
    'Subject',
    'Condition',
    'Block',
    'Trial',
    'Timestamp',
    'TrialType',
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

instruct_text = [
    ('Welcome to the experiment. Press space to continue.'),
    ('In this experiment you will be remembering colors.\n\n'
     'Each trial will start with a fixation cross. '
     'Then, 6 squares with different colors will appear. '
     'Remember as many colors as you can.\n\n'
     'After a short delay, a square will reappear.\n\n'
     'If it has the SAME color, press the "S" key. '
     'If it has a DIFFERENT color, press the "D" key.\n'
     'If you are not sure, just take your best guess.\n\n'
     'You will get breaks in between blocks.\n\n'
     'Press space to continue.'),
]

fixated_instruct_text = (
    'For these sets of blocks, please keep your eyes on the fixation cross '
    'from when it appears until you are able to make your response.\n\n'
    'Press space to begin the experiment.'
)

freegaze_instruct_text = (
    'For these sets of blocks, you may move your eyes as you please.\n\n'
    'Press space to begin the experiment.'
)

number_of_blocks = 2
number_of_trials_per_block = 10


class EyeTrackingKtask(changedetection.Ktask):
    def __init__(self, **kwargs):
        self.tracker = None

        super(EyeTrackingKtask, self).__init__(**kwargs)

    def run(self):
        self.chdir()

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

        conditions = ['FreeGaze', 'Fixated']
        random.shuffle(conditions)

        for condition in conditions:
            if condition == 'FreeGaze':
                self.display_text_screen(text=freegaze_instruct_text)
            else:
                self.display_text_screen(text=fixated_instruct_text)

            for block_num in range(self.number_of_blocks):
                block = self.make_block()
                for trial_num, trial in enumerate(block):
                    data = self.run_trial(trial, block_num, trial_num)
                    data.update({'Condition': condition})
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
    instruct_text=instruct_text,
    monitor_distance=changedetection.distance_to_monitor,
    number_of_blocks=number_of_blocks,
    number_of_trials_per_block=number_of_trials_per_block,
)

experiment.run()
