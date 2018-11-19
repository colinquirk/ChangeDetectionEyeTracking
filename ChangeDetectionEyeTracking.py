from __future__ import division
from __future__ import print_function

import os
import random
import sys
import traceback

# Necesssary to access psychopy paths
import psychopy  # noqa:F401

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
    'For these blocks, please keep your eyes on the fixation cross '
    'from when it appears until you are able to make your response.\n\n'
    'Try to blink only while making your response.\n\n'
    'Press space to continue.'
)

freegaze_instruct_text = (
    'For these blocks, you may move your eyes as you please.\n\n'
    'Try to blink only while making your response.\n\n'
    'Press space to continue.'
)

data_directory = os.path.join(
    os.path.expanduser('~'), 'Desktop', 'Colin', 'ChangeDetectionEyeTracking', 'Data')

sample_time = 0.75

number_of_blocks = 5
number_of_trials_per_block = 80


class EyeTrackingKtask(changedetection.Ktask):
    def __init__(self, **kwargs):
        self.quit = False  # Needed because eyetracker must shut down
        self.tracker = None

        super(EyeTrackingKtask, self).__init__(**kwargs)

    def quit_experiment(self):
        self.quit = True
        if self.experiment_window:
            self.display_text_screen('Quiting...', wait_for_input=False)
        if self.tracker:
            self.tracker.set_offline_mode()
            self.tracker.close_edf()
            self.tracker.transfer_edf()
            self.tracker.close_connection()

        super(EyeTrackingKtask, self).quit_experiment()

    def run(self):
        self.chdir()

        print('Note: EDF file will be overwritten if identical subject numbers are used!')
        ok = self.get_experiment_info_from_dialog(self.questionaire_dict)

        if not ok:
            print('Experiment has been terminated.')
            sys.exit(1)

        self.save_experiment_info()
        self.open_csv_data_file()
        self.open_window(screen=0)
        self.display_text_screen('Loading...', wait_for_input=False)

        self.tracker = eyelinker.EyeLinker(
            self.experiment_window,
            'CDET' + self.experiment_info['Subject Number'] + '.edf',
            'BOTH'
        )

        self.tracker.initialize_graphics()
        self.tracker.open_edf()
        self.tracker.initialize_tracker()
        self.tracker.send_calibration_settings()

        for instruction in self.instruct_text:
            self.display_text_screen(text=instruction)

        self.tracker.display_eyetracking_instructions()

        conditions = ['FreeGaze', 'Fixated']
        random.shuffle(conditions)

        for condition in conditions:
            if condition == 'FreeGaze':
                self.display_text_screen(text=freegaze_instruct_text)
            else:
                self.display_text_screen(text=fixated_instruct_text)

            for block_num in range(self.number_of_blocks):
                block = self.make_block()
                self.tracker.setup_tracker()
                self.display_text_screen(text='Get ready...', wait_for_input=False)
                psychopy.core.wait(2)
                for trial_num, trial in enumerate(block):
                    self.tracker.send_message('BLOCK %d' % block_num)
                    self.tracker.send_message('TRIAL %d' % trial_num)
                    status = '%s: Block %d, Trial %d' % (condition, block_num, trial_num)
                    self.tracker.send_status(status)
                    self.tracker.start_recording()
                    data = self.run_trial(trial, block_num, trial_num)
                    self.tracker.stop_recording()
                    data.update({'Condition': condition})
                    self.send_data(data)

                self.save_data_to_csv()

                if block_num + 1 != self.number_of_blocks:
                    self.display_break()

                    if condition == 'FreeGaze':
                        self.display_text_screen(text='Remember:\n\n' + freegaze_instruct_text)
                    else:
                        self.display_text_screen(text='Remember:\n\n' + fixated_instruct_text)

        self.display_text_screen(
            'The experiment is now over, please get your experimenter.',
            bg_color=[0, 0, 255], text_color=[255, 255, 255],
            wait_for_input=False)

        psychopy.core.wait(10)

        self.quit_experiment()


experiment = EyeTrackingKtask(
    experiment_name='EyeTrackingChangeDetection',
    data_fields=data_fields,
    data_directory=data_directory,
    instruct_text=instruct_text,
    monitor_distance=changedetection.distance_to_monitor,
    sample_time=sample_time,
    number_of_blocks=number_of_blocks,
    number_of_trials_per_block=number_of_trials_per_block,
)

if __name__ == '__main__':
    try:
        experiment.run()
    except Exception:
        print(traceback.format_exc())
        if not experiment.quit:
            experiment.quit_experiment()
