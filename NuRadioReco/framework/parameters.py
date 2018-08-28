from enum import Enum


class stationParameters(Enum):
    nu_zenith = 1  # the zenith angle of the incoming neutrino direction
    nu_azimuth = 2  # the azimuth angle of the incoming neutrino direction
    nu_energy = 3  # the energy of the neutrino
    nu_flavor = 4  # the flavor of the neutrino
    ccnc = 5  # neutral current of charged current interaction
    nu_vertex = 6  # the neutrino vertex position
    inelasticity = 7  # inelasiticy ot neutrino interaction
    triggered = 8  # flag if station was triggered or not
    cr_energy = 9  # the cosmic-ray energy
    cr_zenith = 10  # zenith angle of the cosmic-ray incoming direction 
    cr_azimuth = 11  # azimuth angle of the cosmic-ray incoming direction
    channels_max_amplitude = 12  # the maximum amplitude of all channels (considered in the trigger module)
    zenith = 13  # the zenith angle of the incoming signal direction (WARNING: this parameter is not well defined as the incoming signal direction might be different for different channels)
    azimuth = 14  # the azimuth angle of the incoming signal direction (WARNING: this parameter is not well defined as the incoming signal direction might be different for different channels)


class channelParameters(Enum):
    zenith = 1  # zenith angle of the incoming signal direction
    azimuth = 2  # azimuth angle of the incoming signal direction
    ray_path_type = 3  # the type of the ray tracing solution ('direct', 'refracted' or 'reflected')
    maximum_amplitude = 4  # the maximum ampliude of the absolute number of trace
    SNR = 5  # an dictionary of various signal-to-noise ratio definitions
     
