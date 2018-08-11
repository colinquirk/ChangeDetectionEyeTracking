from __future__ import division
from __future__ import print_function

import psychopy

import eyelinker

import changedetection


experiment = changedetection.Ktask(
    experiment_name=changedetection.exp_name,
    data_fields=changedetection.data_fields,
    monitor_distance=changedetection.distance_to_monitor
)

experiment.run()
