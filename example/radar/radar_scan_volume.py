# -*- coding: utf-8 -*-
# Copyright (c) 2018-2021, earthobservations developers.
# Distributed under the MIT License. See LICENSE.rst for more info.
"""
=====
About
=====
Example for DWD radar sites data in OPERA HDF5 (ODIM_H5) format using wetterdienst and wradlib. # noqa
Derived from https://gist.github.com/kmuehlbauer/ac990569e6ad38a49412fc74a2035c37.

See also:
- https://docs.wradlib.org/en/stable/notebooks/fileio/wradlib_radar_formats.html#OPERA-HDF5-(ODIM_H5) # noqa

This program will request the most recent complete SWEEP_VOL data
for Boostedt and plot the outcome with matplotlib.


=====
Setup
=====
::

    brew install gdal
    pip install wradlib

"""
import logging
import os
from itertools import chain

import matplotlib.pyplot as pl
import wradlib as wrl

from wetterdienst.dwd.radar import (
    DWDRadarData,
    DWDRadarDataFormat,
    DWDRadarDataSubset,
    DWDRadarDate,
    DWDRadarParameter,
    DWDRadarSite,
)

logging.basicConfig(level=logging.INFO)
log = logging.getLogger()


def plot(data: wrl.io.XRadVolume):
    """
    Convenience function for plotting radar data.
    """

    # Get first sweep in volume.
    swp0 = data[0].data

    # Georeference Data.
    swp0 = swp0.pipe(wrl.georef.georeference_dataset)

    # Plot and display data using cartopy.
    fig = pl.figure(figsize=(20, 8))
    ax1 = fig.add_subplot(121, aspect="equal")
    swp0.DBZH[0].plot(x="x", y="y", ax=ax1)
    ax2 = fig.add_subplot(122, aspect="equal")
    swp0.VRADH[0].plot(x="x", y="y", ax=ax2)


def radar_info(data: dict):
    """
    Display data from radar request.
    """
    print(data)
    return

    print("Keys:", data.keys())

    log.info("Data")
    for key, value in data.items():
        print(f"- {key}: {value}")


def radar_scan_volume():

    request_velocity = DWDRadarData(
        parameter=DWDRadarParameter.SWEEP_VOL_VELOCITY_H,
        start_date=DWDRadarDate.MOST_RECENT,
        site=DWDRadarSite.BOO,
        fmt=DWDRadarDataFormat.HDF5,
        subset=DWDRadarDataSubset.POLARIMETRIC,
    )
    request_reflectivity = DWDRadarData(
        parameter=DWDRadarParameter.SWEEP_VOL_REFLECTIVITY_H,
        start_date=DWDRadarDate.MOST_RECENT,
        site=DWDRadarSite.BOO,
        fmt=DWDRadarDataFormat.HDF5,
        subset=DWDRadarDataSubset.POLARIMETRIC,
    )

    log.info(
        f"Acquiring radar SWEEP_VOL data for {DWDRadarSite.BOO} at "
        f"{request_velocity.start_date}"
    )

    # Submit requests.
    results = chain(
        request_velocity.collect_data(), request_reflectivity.collect_data()
    )

    # Collect list of buffers.
    files = list(map(lambda item: item.data, results))

    # Decode data using wradlib.
    data = wrl.io.open_odim(files)

    # Output debug information.
    radar_info(data)

    # Plot and display data.
    plot(data)
    pl.show()

    # Remove temporary files.
    for tmpfile in files:
        os.unlink(tmpfile)


def main():
    radar_scan_volume()


if __name__ == "__main__":
    main()
