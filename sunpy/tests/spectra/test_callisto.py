# -*- coding: utf-8 -*-
# Author: Florian Mayer <florian.mayer@bitsrc.org>

from __future__ import absolute_import

import os
import shutil

from tempfile import mkdtemp
from datetime import datetime

import numpy as np

import sunpy.data.test

from sunpy.data.sample import CALLISTO_IMAGE
from sunpy.spectra.sources.callisto import (
    CallistoSpectrogram, query, download, minimal_pairs
)


def test_read():
    ca = CallistoSpectrogram.read(CALLISTO_IMAGE)
    assert ca.start == datetime(2011, 9, 22, 10, 30, 0, 51000)
    assert (
        ca.t_init ==
        (datetime(2011, 9, 22, 10, 30) - datetime(2011, 9, 22)).seconds
    )
    assert ca.shape == (200, 3600)
    assert ca.t_delt == 0.25
    # Test linearity of time axis.
    assert np.array_equal(
        ca.time_axis, np.linspace(0, 0.25 * (ca.shape[1] - 1), ca.shape[1])
    )
    assert ca.dtype == np.uint8


def test_query():
    URL = 'http://soleil.i4ds.ch/solarradio/data/2002-20yy_Callisto/2011/09/22/'

    result = list(query(
        datetime(2011, 9, 22, 5), datetime(2011, 9, 22, 6), set(["BIR"])
    ))
    RESULTS = [
        "BIR_20110922_050000_01.fit.gz",
        "BIR_20110922_051500_01.fit.gz",
        "BIR_20110922_053000_01.fit.gz",
        "BIR_20110922_060000_01.fit.gz",
        "BIR_20110922_050000_03.fit.gz",
        "BIR_20110922_051500_03.fit.gz",
        "BIR_20110922_053000_03.fit.gz",
        "BIR_20110922_054500_03.fit.gz",
        "BIR_20110922_060000_03.fit.gz"
    ]

    RESULTS.sort()

    assert result == [URL + res for res in RESULTS]


def test_query_number():
    URL = 'http://soleil.i4ds.ch/solarradio/data/2002-20yy_Callisto/2011/09/22/'

    result = list(query(
        datetime(2011, 9, 22, 5), datetime(2011, 9, 22, 6), set([("BIR", 1)])
    ))
    RESULTS = [
        "BIR_20110922_050000_01.fit.gz",
        "BIR_20110922_051500_01.fit.gz",
        "BIR_20110922_053000_01.fit.gz",
        "BIR_20110922_060000_01.fit.gz",
    ]

    RESULTS.sort()

    assert result == [URL + res for res in RESULTS]


def test_download():
    directory = mkdtemp()
    try:
        result = query(
            datetime(2011, 9, 22, 5), datetime(2011, 9, 22, 6), set([("BIR", 1)])
        )
        RESULTS = [
            "BIR_20110922_050000_01.fit.gz",
            "BIR_20110922_051500_01.fit.gz",
            "BIR_20110922_053000_01.fit.gz",
            "BIR_20110922_060000_01.fit.gz",
        ]
        download(result, directory)
        assert sorted(os.listdir(directory)) == RESULTS
    finally:
        shutil.rmtree(directory)


def test_create_file():
    ca = CallistoSpectrogram.create(CALLISTO_IMAGE)
    assert np.array_equal(ca, CallistoSpectrogram.read(CALLISTO_IMAGE))


def test_create_file_kw():
    ca = CallistoSpectrogram.create(filename=CALLISTO_IMAGE)
    assert np.array_equal(ca, CallistoSpectrogram.read(CALLISTO_IMAGE))


def test_create_url():
    URL = (
        "http://soleil.i4ds.ch/solarradio/data/2002-20yy_Callisto/2011/09/22/"
        "BIR_20110922_050000_01.fit.gz"
    )
    ca = CallistoSpectrogram.create(URL)
    assert np.array_equal(ca, CallistoSpectrogram.read(URL))


def test_create_url_kw():
    URL = (
        "http://soleil.i4ds.ch/solarradio/data/2002-20yy_Callisto/2011/09/22/"
        "BIR_20110922_050000_01.fit.gz"
    )
    ca = CallistoSpectrogram.create(url=URL)
    assert np.array_equal(ca, CallistoSpectrogram.read(URL))


def test_create_single_glob():
    PATTERN = os.path.join(
        os.path.dirname(CALLISTO_IMAGE),
        "BIR_*"
    )
    ca = CallistoSpectrogram.create(PATTERN)
    assert np.array_equal(ca, CallistoSpectrogram.read(CALLISTO_IMAGE))


def test_create_single_glob_kw():
    PATTERN = os.path.join(
        os.path.dirname(CALLISTO_IMAGE),
        "BIR_*"
    )
    ca = CallistoSpectrogram.create(singlepattern=PATTERN)
    assert np.array_equal(ca, CallistoSpectrogram.read(CALLISTO_IMAGE))


def test_create_glob_kw():
    PATTERN = os.path.join(
        os.path.dirname(CALLISTO_IMAGE),
        "BIR_*"
    )
    ca = CallistoSpectrogram.create(pattern=PATTERN)[0]
    assert np.array_equal(ca, CallistoSpectrogram.read(CALLISTO_IMAGE))

def test_create_glob():
    PATTERN = os.path.join(
        os.path.dirname(sunpy.data.test.__file__),
        "BIR_*"
    )
    ca = CallistoSpectrogram.create(PATTERN)
    assert len(ca) == 2

def test_minimum_pairs_commotative():
    A = [0, 1, 2]
    B = [1, 2, 3]
    first = list(minimal_pairs(A, B))
    assert first == [(b, a, d) for a, b, d in minimal_pairs(B, A)]

def test_minimum_pairs_end():
    assert (
        list(minimal_pairs([0, 1, 2, 4], [1, 2, 3, 4])) ==
        [(1, 0, 0), (2, 1, 0), (3, 3, 0)]
    )

def test_minimum_pairs_end_more():
    assert (
        list(minimal_pairs([0, 1, 2, 4, 8], [1, 2, 3, 4])) ==
        [(1, 0, 0), (2, 1, 0), (3, 3, 0)]
    )

def test_minimum_pairs_end_diff():
    assert (
        list(minimal_pairs([0, 1, 2, 8], [1, 2, 3, 4])) ==
        [(1, 0, 0), (2, 1, 0), (3, 3, 4)]
    )

def test_closest():
    assert (
        list(minimal_pairs([50, 60], [0, 10, 20, 30, 40, 51, 52])) ==
        [(0, 5, 1), (1, 6, 8)]
    )