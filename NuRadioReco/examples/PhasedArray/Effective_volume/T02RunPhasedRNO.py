"""
This file runs a phased array trigger simulation. The phased array configuration
in this file is similar to one of the proposed ideas for RNO: 3 GS/s, 8 antennas
at a depth of ~50 m, 30 primary phasing directions. In order to run, we need
a detector file and a configuration file, included in this folder. To run
the code, type:

python T02RunPhasedRNO.py input_neutrino_file.hdf5 4antennas_100m_1.5GHz.json
config_RNO.yaml output_NuRadioMC_file.hdf5 output_NuRadioReco_file.nur

The antenna positions can be changed in the detector position. The config file
defines de bandwidth for the noise RMS calculation. The properties of the phased
array can be changed in the current file - phasing angles, triggering channels,
bandpass filter and so on.

WARNING: this file needs NuRadioMC to be run.
"""

from __future__ import absolute_import, division, print_function
import argparse
# import detector simulation modules
import NuRadioReco.modules.efieldToVoltageConverter
import NuRadioReco.modules.trigger.simpleThreshold
import NuRadioReco.modules.phasedarray.triggerSimulator
import NuRadioReco.modules.channelResampler
import NuRadioReco.modules.channelBandPassFilter
import NuRadioReco.modules.channelGenericNoiseAdder
from NuRadioReco.utilities import units
from NuRadioMC.simulation import simulation
from NuRadioReco.utilities.traceWindows import get_window_around_maximum
import numpy as np
import logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger("runstrawman")

# initialize detector sim modules
efieldToVoltageConverter = NuRadioReco.modules.efieldToVoltageConverter.efieldToVoltageConverter()
efieldToVoltageConverter.begin(debug=False)
triggerSimulator = NuRadioReco.modules.phasedarray.triggerSimulator.triggerSimulator()
channelResampler = NuRadioReco.modules.channelResampler.channelResampler()
channelBandPassFilter = NuRadioReco.modules.channelBandPassFilter.channelBandPassFilter()
channelGenericNoiseAdder = NuRadioReco.modules.channelGenericNoiseAdder.channelGenericNoiseAdder()
thresholdSimulator = NuRadioReco.modules.trigger.simpleThreshold.triggerSimulator()

main_low_angle = -50 * units.deg
main_high_angle = 50 * units.deg
phasing_angles = np.arcsin(np.linspace(np.sin(main_low_angle), np.sin(main_high_angle), 30))

<<<<<<< HEAD
left_edge_around_max = 20 * units.ns
right_edge_around_max = 40 * units.ns


=======
>>>>>>> Removing the pre-threshold for the phased array examples. Switching to diode windows instead of hardcoded window
class mySimulation(simulation.simulation):

    def _detector_simulation(self):
        # start detector simulation
        efieldToVoltageConverter.run(self._evt, self._station, self._det)  # convolve efield with antenna pattern
        # downsample trace to 3 Gs/s
        new_sampling_rate = 3 * units.GHz
        channelResampler.run(self._evt, self._station, self._det, sampling_rate=new_sampling_rate)

        cut_times = get_window_around_maximum(self._station)

        # Bool for checking the noise triggering rate
        check_only_noise = False

<<<<<<< HEAD
        for channel in self._station.iter_channels():  # loop over all channels (i.e. antennas) of the station

            times = channel.get_times()
            argmax = np.argmax(np.abs(channel.get_trace()))
            max_times.append(times[argmax])
            if check_only_noise:
=======
        if check_only_noise:
            for channel in self._station.iter_channels():
>>>>>>> Removing the pre-threshold for the phased array examples. Switching to diode windows instead of hardcoded window
                trace = channel.get_trace() * 0
                channel.set_trace(trace, sampling_rate=new_sampling_rate)

<<<<<<< HEAD
        left_time = np.min(max_times) - left_edge_around_max
        right_time = np.max(max_times) + right_edge_around_max

<<<<<<< HEAD
        if self._is_simulate_noise():
            max_freq = 0.5 / self._dt
            norm = self._get_noise_normalization(self._station.get_id())  # assuming the same noise level for all stations
            channelGenericNoiseAdder.run(self._evt, self._station, self._det, amplitude=self._Vrms, min_freq=0 * units.MHz,
                                         max_freq=max_freq, type='rayleigh', bandwidth=norm)
=======
=======
>>>>>>> Removing the pre-threshold for the phased array examples. Switching to diode windows instead of hardcoded window
        noise = True

        if noise:
            max_freq = 0.5 * new_sampling_rate
            min_freq = 0 * units.MHz
            norm = self._get_noise_normalization(self._station.get_id())  # assuming the same noise level for all stations
            Vrms = self._Vrms / (norm / (max_freq-min_freq)) ** 0.5  # normalize noise level to the bandwidth its generated for
            channelGenericNoiseAdder.run(self._evt, self._station, self._det, amplitude=Vrms, min_freq=min_freq,
                                         max_freq=max_freq, type='rayleigh')
>>>>>>> Fixing bug regarding the noise amplitude. Now noise is calculated with the correct sampling rate

        # bandpass filter trace, the upper bound is higher then the sampling rate which makes it just a highpass filter
        channelBandPassFilter.run(self._evt, self._station, self._det, passband=[132 * units.MHz, 1150 * units.MHz],
                                  filter_type='butter', order=8)
        channelBandPassFilter.run(self._evt, self._station, self._det, passband=[0, 700 * units.MHz],
                                  filter_type='butter', order=10)

<<<<<<< HEAD
<<<<<<< HEAD
        # Setting the trace values far from the amplitude maxima to zero
        # to reduce the noise trigger rate
        for channel in self._station.iter_channels():

            times = channel.get_times()
            left_bin = np.argmin(np.abs(times - left_time))
            right_bin = np.argmin(np.abs(times - right_time))
            trace = channel.get_trace()
<<<<<<< HEAD
<<<<<<< HEAD
            trace[0:left_bin] = 0
            trace[right_bin:None] = 0
            channel.set_trace(trace, sampling_rate=new_sampling_rate)

        # first run a simple threshold trigger
        triggerSimulator.run(self._evt, self._station, self._det,
<<<<<<< HEAD
<<<<<<< HEAD
                             threshold=2.3 * self._Vrms,  # see phased trigger module for explanation
=======
                             threshold=2.45 * self._Vrms, # see phased trigger module for explanation
>>>>>>> Changing from 8 to 4 antennas for the RNO project
=======
=======
            #trace[0:left_bin] = 0
            #trace[right_bin:None] = 0
            #channel.set_trace(trace, sampling_rate = new_sampling_rate)
=======
            trace[0:left_bin] = 0
            trace[right_bin:None] = 0
            channel.set_trace(trace, sampling_rate = new_sampling_rate)
>>>>>>> Removing commented lines

        # first run a simple threshold trigger
        trig = triggerSimulator.run(self._evt, self._station, self._det,
>>>>>>> Changing trigger name
=======
        # first run a simple threshold trigger
=======
        # run the phasing trigger
>>>>>>> Remove unused variables, correct comments
        triggerSimulator.run(self._evt, self._station, self._det,
>>>>>>> Removing the pre-threshold for the phased array examples. Switching to diode windows instead of hardcoded window
                             threshold=2.2 * self._Vrms, # see phased trigger module for explanation
>>>>>>> Fixing bug regarding the noise amplitude. Now noise is calculated with the correct sampling rate
                             triggered_channels=None,  # run trigger on all channels
<<<<<<< HEAD
                             trigger_name='primary_and_secondary_phasing',  # the name of the trigger
=======
                             trigger_name='primary_phasing', # the name of the trigger
>>>>>>> Changing trigger name
                             phasing_angles=phasing_angles,
                             secondary_phasing_angles=None,
                             coupled=False,
                             ref_index=1.75,
                             cut_times=cut_times)

parser = argparse.ArgumentParser(description='Run NuRadioMC simulation')
parser.add_argument('--inputfilename', type=str,
                    help='path to NuRadioMC input event list', default='0.00_12_00_1.00e+16_1.00e+19.hdf5')
parser.add_argument('--detectordescription', type=str,
                    help='path to file containing the detector description', default='4antennas_100m_1.5GHz.json')
parser.add_argument('--config', type=str,
                    help='NuRadioMC yaml config file', default='config_RNO.yaml')
parser.add_argument('--outputfilename', type=str,
                    help='hdf5 output filename', default='output_PA_RNO.hdf5')
parser.add_argument('--outputfilenameNuRadioReco', type=str, nargs='?', default=None,
                    help='outputfilename of NuRadioReco detector sim file')
args = parser.parse_args()

sim = mySimulation(eventlist=args.inputfilename,
                            outputfilename=args.outputfilename,
                            detectorfile=args.detectordescription,
                            outputfilenameNuRadioReco=args.outputfilenameNuRadioReco,
                            config_file=args.config)
sim.run()
