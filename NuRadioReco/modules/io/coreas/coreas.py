import numpy as np
from NuRadioReco.utilities import units
from radiotools import helper as hp
from radiotools import coordinatesystems
import NuRadioReco.framework.sim_station
import NuRadioReco.framework.base_trace
import NuRadioReco.framework.electric_field

from NuRadioReco.framework.parameters import stationParameters as stnp
from NuRadioReco.framework.parameters import channelParameters as chp
from NuRadioReco.framework.parameters import electricFieldParameters as efp

# conversion_fieldstrength_cgs_to_SI = 2.99792458e4 * 1e-6
conversion_fieldstrength_cgs_to_SI = 2.99792458e10 * units.micro * units.volt / units.meter


def get_angles(corsika):
    zenith = np.deg2rad(corsika['inputs'].attrs["THETAP"][0])
    azimuth = hp.get_normalized_angle(3 * np.pi / 2. + np.deg2rad(corsika['inputs'].attrs["PHIP"][0]))  # conert to auger cs
    Bx, Bz = corsika['inputs'].attrs["MAGNET"]
    B_inclination = np.arctan2(Bz, Bx)
#     B_declination = hp.get_declination(hp.get_magnetic_field_vector(site='mooresbay'))
#     azimuth -= B_declination
    B_strength = (Bx ** 2 + Bz ** 2) ** 0.5 * units.micro * units.tesla
    magnetic_field_vector = B_strength * hp.spherical_to_cartesian(np.pi * 0.5 + B_inclination, 0 + np.pi * 0.5)  # in arianna cooordinates north is + 90 deg
    return zenith, azimuth, magnetic_field_vector


def calculate_simulation_weights(positions):
    """Calculate weights according to the area that one simulated position represents.
    Weights are therefore given in units of area.
    Note: The volume of a 2d convex hull is the area."""

    import scipy.spatial as spatial
    weights = np.zeros_like(positions[:, 0])
    vor = spatial.Voronoi(positions[:, :2])  # algorithm will find no solution if flat simulation is given in 3d.
    for p in range(0, weights.shape[0]):
        weights[p] = spatial.ConvexHull(vor.vertices[vor.regions[vor.point_region[p]]]).volume
    return weights


def make_sim_station(station_id, corsika, observer, channel_ids,  weight=None):
    """
    creates an ARIANNA sim station from the observer object of the coreas hdf5 file

    Parameters
    ----------
    station_id: station id
        the id of the station to create
    corsika : hdf5 file object
        the open hdf5 file object of the corsika hdf5 file
    observer: hdf5 observer object
    weight: weight of individual station
        weight corresponds to area covered by station

    Returns
    -------
    sim_station: sim station
        ARIANNA simulated station object
    """
    # loop over all coreas stations, rotate to ARIANNA CS and save to simulation branch
    zenith, azimuth, magnetic_field_vector = get_angles(corsika)

    position = observer.attrs['position']

    data = np.copy(observer)
    data[:, 1], data[:, 2] = -observer[:, 2], observer[:, 1]

    # convert to SI units
    data[:, 0] *= units.second
    data[:, 1] *= conversion_fieldstrength_cgs_to_SI
    data[:, 2] *= conversion_fieldstrength_cgs_to_SI
    data[:, 3] *= conversion_fieldstrength_cgs_to_SI

    cs = coordinatesystems.cstrafo(zenith, azimuth, magnetic_field_vector=magnetic_field_vector)
    efield = cs.transform_from_magnetic_to_geographic(data[:, 1:].T)
    efield = cs.transform_from_ground_to_onsky(efield)

    # prepend trace with zeros to not have the pulse directly at the start
    n_samples_prepend = efield.shape[1]
    efield2 = np.zeros((3, n_samples_prepend + efield.shape[1]))
    efield2[0] = np.append(np.zeros(n_samples_prepend), efield[0])
    efield2[1] = np.append(np.zeros(n_samples_prepend), efield[1])
    efield2[2] = np.append(np.zeros(n_samples_prepend), efield[2])

    antenna_position = np.zeros(3)
    antenna_position[0], antenna_position[1], antenna_position[2] = -position[1] * units.cm, position[0] * units.cm, position[2] * units.cm

    antenna_position = cs.transform_from_magnetic_to_geographic(antenna_position)
    sampling_rate = 1. / (corsika['CoREAS'].attrs['TimeResolution'] * units.second)
    sim_station = NuRadioReco.framework.sim_station.SimStation(station_id, position=antenna_position)
    electric_field = NuRadioReco.framework.electric_field.ElectricField(channel_ids)
    electric_field.set_trace(efield2, sampling_rate)
    electric_field.set_parameter(efp.ray_path_type, 'direct')
    electric_field.set_parameter(efp.zenith, zenith)
    electric_field.set_parameter(efp.azimuth, azimuth)
    sim_station.add_electric_field(electric_field)
    sim_station.set_parameter(stnp.azimuth, azimuth)
    sim_station.set_parameter(stnp.zenith, zenith)
    energy = corsika['inputs'].attrs["ERANGE"][0] * units.GeV
    sim_station.set_parameter(stnp.cr_energy, energy)
    sim_station.set_magnetic_field_vector(magnetic_field_vector)
    sim_station.set_parameter(stnp.cr_energy_em, corsika["highlevel"].attrs["Eem"])
    sim_station.set_is_cosmic_ray()

    sim_station.set_simulation_weight(weight)
    return sim_station
