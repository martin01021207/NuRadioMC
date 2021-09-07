import numpy as np
import uproot
import NuRadioReco.framework.event
import NuRadioReco.framework.station
import NuRadioReco.framework.channel
from NuRadioReco.utilities import units
import astropy.time
import glob


class RNOGDataReader:

    def __init__(self, filenames, *args, **kwargs):
        self.__filenames = filenames
        self.__event_ids = None
        self.__run_numbers = None
        self.__sampling_rate = 3.2 * units.GHz #TODO: 3.2 at the beginning of deployment. Will change to 2.4 GHz after firmware update eventually, but info not yet contained in the .root files. Read out once available.
        self.__parse_event_ids()
        self.__parse_run_numbers()
        self.__i_events_per_file = np.zeros((len(self.__filenames), 2), dtype=int)
        i_event = 0
        for i_file, filename in enumerate(filenames):
            file = self.__open_file(filename)
            events_in_file = file['waveforms'].num_entries
            self.__i_events_per_file[i_file] = [i_event, i_event + events_in_file]
            i_event += events_in_file

    def get_filenames(self):
        return self.__filenames

    def get_event_ids(self):
        if self.__event_ids is None:
            return self.__parse_event_ids()
        return self.__event_ids

    def __parse_event_ids(self):
        self.__event_ids = np.array([], dtype=int)
        for filename in self.__filenames:
            file = self.__open_file(filename)
            self.__event_ids = np.append(self.__event_ids, file['waveforms']['event_number'].array(library='np').astype(int))

    def get_run_numbers(self):
        if self.__run_numbers is None:
            self.__parse_run_numbers()
        return self.__run_numbers

    def __parse_run_numbers(self):
        self.__run_numbers = np.array([], dtype=int)
        for filename in self.__filenames:
            file = self.__open_file(filename)
            self.__run_numbers = np.append(self.__run_numbers, file['header']['run_number'].array(library='np').astype(int))

    def __open_file(self, filename):
        file = uproot.open(filename)
        if 'combined' in file:
            file = file['combined']
        return file

    def get_n_events(self):
        return self.get_event_ids().shape[0]

    def get_event_i(self, i_event):
        event = NuRadioReco.framework.event.Event(self.get_run_numbers()[i_event], self.get_event_ids()[i_event])
        for i_file, filename in enumerate(self.__filenames):
            if self.__i_events_per_file[i_file, 0] <= i_event < self.__i_events_per_file[i_file, 1]:
                i_event_in_file = i_event - self.__i_events_per_file[i_file, 0]
                file = self.__open_file(self.__filenames[i_file])
                station = NuRadioReco.framework.station.Station((file['waveforms']['station_number'].array(library='np')[i_event_in_file]))
                # station not set properly in first runs, try from header
                if station.get_id() == 0 and 'header' in file:
                    station = NuRadioReco.framework.station.Station((file['header']['station_number'].array(library='np')[i_event_in_file]))
                station.set_is_neutrino()

                if 'header' in file:
                    unix_time = file['header']['trigger_time'].array(library='np')[i_event_in_file]
                    event_time = astropy.time.Time(unix_time, format='unix')
                    station.set_station_time(event_time)

                waveforms = file['waveforms']['radiant_data[24][2048]'].array(library='np', entry_start=i_event_in_file, entry_stop=(i_event_in_file+1))
                for i_channel in range(waveforms.shape[1]):
                    channel = NuRadioReco.framework.channel.Channel(i_channel)
                    channel.set_trace(waveforms[0, i_channel]*units.mV, self.__sampling_rate)
                    station.add_channel(channel)
                event.set_station(station)
                return event
        return None

    def get_event(self, event_id):
        for header_file_name in self.__filenames:
            header_file = uproot.open(header_file_name)
            for header_key in header_file.keys():
                run_numbers = header_file[header_key]['run_number'].array(library='np').astype(int)
                event_ids = header_file[header_key]['event_number'].array(library='np').astype(int)
                event_search = np.where((run_numbers == event_id[0]) & (event_ids == event_id[1]))[0]
                print(header_file[header_key]['trigger_time'].array())
                event = NuRadioReco.framework.event.Event(event_id[0], event_id[1])
                for header_event_index in event_search:
                    station = NuRadioReco.framework.station.Station(header_file[header_key]['station_number'].array(entry_start=header_event_index, entry_stop=header_event_index + 1, library='np').astype(int)[0])
                    event.set_station(station)
                    for waveform_file_name in self.__waveform_files:
                        waveform_file = uproot.open(waveform_file_name)
                        for waveform_key in waveform_file.keys():
                            waveform_run_numbers = waveform_file[waveform_key]['run_number'].array(library='np').astype(int)
                            waveform_event_ids = waveform_file[waveform_key]['event_number'].array(library='np').astype(int)
                            waveform_search = np.where((waveform_run_numbers == event_id[0]) & (waveform_event_ids == event_id[1]))[0]
                            for waveform_event_index in waveform_search:
                                waveform_data = waveform_file[waveform_key]['radiant_data[24][2048]'].array(entry_start=waveform_event_index, entry_stop=waveform_event_index + 1, library='np')[0]
                                for i_channel in range(waveform_data.shape[0]):
                                    channel = NuRadioReco.framework.channel.Channel(i_channel)
                                    channel.set_trace(waveform_data[i_channel], 3.2)
                                    station.add_channel(channel)
                return event
        return None

    def get_events(self):
        for ev_i in range(self.get_n_events()):
            yield self.get_event_i(ev_i)

    def get_detector(self):
        return None

    def get_header(self):
        return None
