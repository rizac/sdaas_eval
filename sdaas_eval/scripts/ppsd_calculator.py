'''
Implements an optimized version of the power spectral density (PSD) function
of the PPSD module of ObsPy. The function is the feature extractor for our
machine learning model (Ifsolation Forest) for anomaly detection in segments
amplitudes 
'''
import math
import time
import numpy as np
from matplotlib import mlab
from obspy.signal.util import prev_pow_2
from obspy.signal.spectral_estimation import PPSD, dtiny, fft_taper
from obspy.core.stream import read
from obspy.core.inventory import Inventory
from obspy.core.inventory.inventory import read_inventory


class old:
    '''container for the old functions used in the paper'''

    @staticmethod
    def psd_values(periods, raw_trace, inventory):
        periods = np.asarray(periods)
        try:
            ppsd_ = old.psd(raw_trace, inventory)
        except Exception as esc:
            raise ValueError('%s error when computing PSD: %s' %
                             (esc.__class__.__name__, str(esc)))
        # check first if we can interpolate ESPECIALLY TO SUPPRESS A WEIRD
        # PRINTOUT (numpy?): something like '5064 5062' which happens
        # on IndexError (len(ppsd_.psd_values)=0)
        if not len(ppsd_.psd_values):
            raise ValueError('Expected 1 psd array, no psd computed')
        val = np.interp(
            np.log10(periods),
            np.log10(ppsd_.period_bin_centers),
            ppsd_.psd_values[0]
        )
        val[periods < ppsd_.period_bin_centers[0]] = np.nan
        val[periods > ppsd_.period_bin_centers[-1]] = np.nan
        return val

    @staticmethod
    def psd(raw_trace, inventory):
        # tr = segment.stream(True)[0]
        dt = raw_trace.stats.endtime - raw_trace.stats.starttime  # total_seconds
        ppsd = PPSD(raw_trace.stats, metadata=inventory, ppsd_length=int(dt))
        ppsd.add(raw_trace)
        return ppsd


def psd_values(psd_periods, tr, metadata, special_handling=None,
               period_smoothing_width_octaves=1.0,
               period_step_octaves=0.125, method='old'):
    """
    Calculates the power spectral density (psd) of the given
    trace `tr`, and returns the values in dB at the given `psd_periods`.

    Note: all optional parameters should be left as they are,
        as the given parameter where those used for training.
        For any further information, see
        :class:`~obspy.signal.spectral_estimation.PPSD` and
        :class:`~obspy.signal.spectral_estimation.PPSD.__process`

    :psd_periods: numeric list/array of periods (in second)
    :param tr: obspy Trace
    :param metadata: Response information of instrument. It must be
        a :class:`~obspy.core.inventory.inventory.Inventory` (e.g. read from a
        StationXML file using
        :func:`~obspy.core.inventory.inventory.read_inventory` or fetched
        from a :mod:`FDSN <obspy.clients.fdsn>` webservice)
    """
    # if trace has a masked array we fill in zeros
    try:
        tr.data[tr.data.mask] = 0.0
    # if it is no masked array, we get an AttributeError
    # and have nothing to do
    except AttributeError:
        pass

    # merging some PPSD.__init__ stuff here:
    ppsd_length = tr.stats.endtime - tr.stats.starttime  # float, seconds
    stats = tr.stats
    sampling_rate = stats.sampling_rate
    # calculate derived attributes
    # nfft is determined mimicking the fft setup in McNamara&Buland
    # paper:
    # (they take 13 segments overlapping 75% and truncate to next lower
    #  power of 2)
    #  - take number of points of whole ppsd segment (default 1 hour)
    nfft = ppsd_length * sampling_rate
    #  - make 13 single segments overlapping by 75%
    #    (1 full segment length + 25% * 12 full segment lengths)
    nfft = nfft / 4.0
    #  - go to next smaller power of 2 for nfft
    nfft = prev_pow_2(nfft)
    #  - use 75% overlap
    #    (we end up with a little more than 13 segments..)
    nlap = int(0.75 * nfft)

    # calculate the specturm. Using matlab for this seems weird (as the PPSD
    # has a strong focus on outputting plots, it makes sense, here not so much)
    # but the function basically computes an fft and then its power spectrum.
    # (also remember: matlab will be always available as ObsPy dependency)
    spec, _freq = mlab.psd(tr.data, nfft, sampling_rate,
                           detrend=mlab.detrend_linear, window=fft_taper,
                           noverlap=nlap, sides='onesided',
                           scale_by_freq=True)

    # leave out first entry (offset)
    spec = spec[1:]
    freq = _freq[1:]

    # working with the periods not frequencies later so reverse spectrum
    spec = spec[::-1]

    # Here we remove the response using the same conventions
    # since the power is squared we want to square the sensitivity
    # we can also convert to acceleration if we have non-rotational data
    if special_handling == "ringlaser":
        # in case of rotational data just remove sensitivity
        spec /= metadata['sensitivity'] ** 2
    # special_handling "hydrophone" does instrument correction same as
    # "normal" data
    else:
        # determine instrument response from metadata
        try:
            resp = _get_response(tr, metadata, nfft)
        except Exception as e:
            msg = ("Error getting response from provided metadata:\n"
                   "%s: %s\n"
                   "Skipping time segment(s).")
            msg = msg % (e.__class__.__name__, str(e))
            # warnings.warn(msg)
            # return False
            raise ValueError(msg)

        resp = resp[1:]
        resp = resp[::-1]
        # Now get the amplitude response (squared)
        respamp = np.absolute(resp * np.conjugate(resp))
        # Make omega with the same conventions as spec
        w = 2.0 * math.pi * freq
        w = w[::-1]
        # Here we do the response removal
        # Do not differentiate when `special_handling="hydrophone"`
        if special_handling == "hydrophone":
            spec = spec / respamp
        else:
            spec = (w ** 2) * spec / respamp
    # avoid calculating log of zero
    idx = spec < dtiny
    spec[idx] = dtiny

    # go to dB
    spec = np.log10(spec)
    spec *= 10

    # setup variables for the final smoothed spectral values:
    smoothed_psd = []
    _psd_periods = 1.0 / freq[::-1]
    psd_periods = np.asarray(psd_periods)

    if method == 'old':
        # smooth the spectrum: for any period P in psd_periods[i] compute a
        # time-dependent range [Pmin, Pmax] around P, and then compute the
        # smoothed spectrum at index i as the mean of spec on [Pmin, Pmax].
        # and computing their mean: for any period P in psd_periods we compute
        # the smoothed spectrum on the period immediately before and after P,
        # we append those two "bounding" values to an array, and we later
        # linearly interpolate the array with our psd_values
        period_bin_centers = []
        period_limits = (_psd_periods[0], _psd_periods[-1])
        # calculate smoothed periods
        for periods_bins in \
                _setup_yield_period_binning(psd_periods,
                                            period_smoothing_width_octaves,
                                            period_step_octaves, period_limits):
            period_bin_left, period_bin_center, period_bin_right = periods_bins
            _spec_slice = spec[(period_bin_left <= _psd_periods) &
                               (_psd_periods <= period_bin_right)]
            smoothed_psd.append(_spec_slice.mean())
            period_bin_centers.append(period_bin_center)
        # interpolate. Use log10 as it was used for training (from tests,
        # linear interpolation does not change much anyway)
        val = np.interp(
            np.log10(psd_periods),
            np.log10(period_bin_centers),
            smoothed_psd
        )
        val[psd_periods < period_bin_centers[0]] = np.nan
        val[psd_periods > period_bin_centers[-1]] = np.nan
    else:
        # the width of frequencies we average over for every bin is controlled
        # by period_smoothing_width_octaves (default one full octave)
        period_smoothing_width_factor = \
            2 ** period_smoothing_width_octaves
        period_smoothing_width_factor_sqrt = \
            (period_smoothing_width_factor ** 0.5)

#         period_bins_left = psd_periods / period_smoothing_width_factor_sqrt
#         period_bins_right = period_bins_left * period_smoothing_width_factor
#         period_bins_left = period_bins_left.reshape((len(psd_periods), 1))
#         period_bins_right = period_bins_right.reshape((len(psd_periods), 1))
#         spc_tiled = np.tile(spec, (len(period_bins_left), 1))
#         spc_tiled[(period_bins_left > _psd_periods) |
#                   (_psd_periods > period_bins_right)] = np.nan
#         val = np.nanmean(spc_tiled, axis=1)

        for psd_period in psd_periods:
            # calculate left/right edge and center of psd_period bin
            # set first smoothing bin's left edge such that the center
            # frequency is psd_period
            period_bin_left = psd_period / period_smoothing_width_factor_sqrt
            period_bin_right = period_bin_left * period_smoothing_width_factor
            id1 = np.searchsorted(_psd_periods, period_bin_left, side='left')
            id2 = np.searchsorted(_psd_periods, period_bin_right, side='right')
            smoothed_psd.append(spec[id1:id2].mean())
#             _spec_slice = spec[(period_bin_left <= _psd_periods) &
#                                (_psd_periods <= period_bin_right)]
#             smoothed_psd.append(_spec_slice.mean())
        val = np.array(smoothed_psd)

    return val


def _get_response(tr, metadata, nfft):
    '''Returns the response from the given trace and the given metadata'''
    # This function is the same as _get_response_from_inventory
    # but we keep the original PPSd skeleton to show how it
    # might be integrated with new metadata object. For the
    # moment `metadata` must be an Inventory object
    if isinstance(metadata, Inventory):
        return _get_response_from_inventory(tr, metadata, nfft)
#         elif isinstance(self.metadata, Parser):
#             return self._get_response_from_parser(tr)
#         elif isinstance(self.metadata, dict):
#             return self._get_response_from_paz_dict(tr)
#         elif isinstance(self.metadata, (str, native_str)):
#             return self._get_response_from_resp(tr)
#     else:
#         msg = "Unexpected type for `metadata`: %s" % type(self.metadata)
#         raise TypeError(msg)
    msg = "Unexpected type for `metadata`: %s" % type(metadata)
    raise TypeError(msg)


def _get_response_from_inventory(tr, metadata, nfft):
    inventory = metadata
    delta = 1.0 / tr.stats.sampling_rate
    id_ = "%(network)s.%(station)s.%(location)s.%(channel)s" % tr.stats
    response = inventory.get_response(id_, tr.stats.starttime)
    resp, _ = response.get_evalresp_response(t_samp=delta, nfft=nfft,
                                             output="VEL")
    return resp


def _get_period_binning(psd_period, period_smoothing_width_octaves,
                        period_step_octaves):
    # we step through the period range at step width controlled by
    # period_step_octaves (default 1/8 octave)
    # period_step_factor = 2 ** period_step_octaves

    # the width of frequencies we average over for every bin is controlled
    # by period_smoothing_width_octaves (default one full octave)
    period_smoothing_width_factor = \
        2 ** period_smoothing_width_octaves
    # calculate left/right edge and center of psd_period bin
    # set first smoothing bin's left edge such that the center frequency is
    # psd_period
    per_left = (psd_period /
                (period_smoothing_width_factor ** 0.5))
    per_right = per_left * period_smoothing_width_factor
    return per_left, per_right


def _setup_yield_period_binning(psd_periods, period_smoothing_width_octaves,
                                period_step_octaves, period_limits):
    """
    Set up period binning, i.e. tuples/lists [Pleft, Pcenter, Pright], from
    `period_limits[0]` up to `period_limits[1]`. Then, for any period P
    in psd_periods, yields the binnings [Pleft1, Pcenter1, Pright1] and
    [Pleft2, Pcenter2, Pright2] such as Pcenter1 <= P <= Pcenter2, and so on.
    The total amount of binnings yielded is always even and
    at most 2 * len(psd_periods)
    """
    if period_limits is None:
        period_limits = (psd_periods[0], psd_periods[-1])
    # we step through the period range at step width controlled by
    # period_step_octaves (default 1/8 octave)
    period_step_factor = 2 ** period_step_octaves
    # the width of frequencies we average over for every bin is controlled
    # by period_smoothing_width_octaves (default one full octave)
    period_smoothing_width_factor = \
        2 ** period_smoothing_width_octaves
    # calculate left/right edge and center of first period bin
    # set first smoothing bin's left edge such that the center frequency is
    # the lower limit specified by the user (or the lowest period in the
    # psd)
    per_left = (period_limits[0] /
                (period_smoothing_width_factor ** 0.5))
    per_right = per_left * period_smoothing_width_factor
    per_center = math.sqrt(per_left * per_right)

    # build up lists
    # per_octaves_left = [per_left]
    # per_octaves_right = [per_right]
    # per_octaves_center = [per_center]
    previous_periods = per_left, per_center, per_right

    idx = np.argwhere(psd_periods > per_center)[0][0]
    psdlen = len(psd_periods)

    # do this for the whole period range and append the values to our lists
    while per_center < period_limits[1] and idx < psdlen:
        # move left edge of smoothing bin further
        per_left *= period_step_factor
        # determine right edge of smoothing bin
        per_right = per_left * period_smoothing_width_factor
        # determine center period of smoothing/binning
        per_center = math.sqrt(per_left * per_right)
        # yield if:
        if previous_periods[1] <= psd_periods[idx] and per_center >= psd_periods[idx]:
            yield previous_periods
            yield per_left, per_center, per_right
            idx += 1

        previous_periods = per_left, per_center, per_right


if __name__ == "__main__":

    from os.path import dirname, join, sys

#     for N in [100, 1000, 10000, 100000]:
#         a = np.arange(0, N, dtype=float)
#         i1, i2 = int(1.0*len(a)/4.0), int(3.0*len(a)/4.0)
#         v1, v2 = a[i1], a[i2]
#         tmean = []
#         tsearch = []
#         for tries in range(10):
#             t = time.time()
#             a[(a>v1) & (a<=v2)].mean()
#             tmean.append(time.time() -t)
#             t = time.time()
#             i1 = np.searchsorted(a, v1, side='left')
#             i2 = np.searchsorted(a, v1, side='right')
#             a[i1:i2].mean()
#             tsearch.append(time.time() -t)
#         tmean, tsearch = np.array(tmean), np.array(tsearch)
#         print(f'array with {len(a)} elements (sorted ascending)')
#         print(f'Computational costs (in seconds)')
#         print(f'Using expr (min median max):       {tmean.min():.5f}, {np.median(tmean):.5f}, {tmean.max():.5f} ')
#         print(f'Using bin search (min median max): {tsearch.min():.5f}, {np.median(tsearch):.5f}, {tsearch.max():.5f} ')
# 
#     sys.exit(0)
    
    trace, inv = 'trace_GE.APE.mseed', 'inventory_GE.APE.xml'
    # trace, inv = 'GE.FLT1..HH?.mseed', 'GE.FLT1.xml'
    stream = read(join(dirname(__file__), 'miniseed', trace))
    inv = read_inventory(join(dirname(__file__), 'miniseed', inv))
    periods = [.2, 5]  # [0.05, 0.2, 2, 5, 9, 20]
    print(f'Periods to calculate on test miniseed: {periods}')
    t = time.time()
    _ = old.psd_values(periods, stream[0], inv)
    t = time.time()-t
    print(f'Old method, values: {str(_)}, time: {t} s')
    t = time.time()
    _ = psd_values(periods, stream[0], inv)
    t = time.time()-t
    print(f'New method (old func), values: {str(_)}, time: {t} s')
    t = time.time()
    _ = psd_values(periods, stream[0], inv, method='new')
    t = time.time()-t
    print(f'New method (new func), values: {str(_)}, time: {t} s')
    