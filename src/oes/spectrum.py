import logging
import warnings

import numpy as np
from scipy.interpolate import interp1d
from scipy.signal import fftconvolve
from scipy.special import wofz


class Spectrum(object):
    """An object holding x and y axis and implememnting some methods
    often used in processing of spectroscopic data.
    """

    def __init__(self, **kwargs):
        """

        kwargs:
        -------
        x: 1D numpy array of wavelengths (or wavenumbers, if you prefffer)

        y: 1D numpy array of intensities (or fluxes or signal strengths, whatever)

        x and y should be equally long (though it is not strictly
        forbidden, most of the methods will fail otherwise)

        """
        self.x = kwargs.pop("x", [])
        self.y = kwargs.pop("y", [])
        if len(self.y) > 0:
            self.maximum = np.max(self.y)
        else:
            self.maximum = None
        normalize = kwargs.pop("normalize", False)
        if normalize and self.maximum is not None:
            self.y /= self.maximum  # normalize intensities
        if len(self.x) != len(self.y):
            warnings.warn("Spectrum: length of x and y mismatch!", Warning)

    def __len__(self):
        lx = len(self.x)
        ly = len(self.y)
        if lx == ly:
            return lx
        else:
            warnings.warn("Spectrum: length of x and y mismatch!", Warning)
            return lx, ly

    def convolve_with_slit_function(self, **kwargs):
        """
        Broaden the peaks in the spectrum by Voigt profile and by a rectangle of given width.
        Changes state of the instance, returns nothing.

        **kwargs:
        ---------
        gauss: *float* gaussian HWHM, defaults to 0.1
        lorentz: *float* lorentzian HWHM, defaults to 1e-9
        step: *float* distance between pixels in nm

        return:
        -------
        None, modifies the spectrum in place
        """
        logging.debug("====////****convolve_with_slit_function****////====")
        gauss = kwargs.pop("gauss", 0.1)
        lorentz = kwargs.pop("lorentz", 1e-9)
        logging.debug("gauss = %s", gauss)
        logging.debug("lorentz =%f ", lorentz)
        slit = Voigt(self.x, gauss, lorentz, np.mean(self.x), 1)
        slit /= np.sum(slit)

        instrumental_step = kwargs.pop("step", None)
        numpoints = len(self.y)
        if instrumental_step is None:
            convolution_profile = slit[slit > max(slit) / 1000.0]
        else:
            # covolve with a rectangle of width equal to the instrumental step
            # to avoid losing thin lines
            simulated_step = self.x[1] - self.x[0]
            if instrumental_step / simulated_step < 1:
                msg = "Your simulated spectra resolution is more rough than experimental data."
                warnings.warn(msg, UserWarning)
                convolution_profile = slit[slit > max(slit) / 1000.0]
            else:
                instrumetal_step_profile = np.ones(
                    int(instrumental_step / simulated_step) + 1
                )
                if len(slit) >= len(instrumetal_step_profile):
                    convolution_profile_uncut = fftconvolve(
                        slit, instrumetal_step_profile, mode="same"
                    )
                else:
                    convolution_profile_uncut = fftconvolve(
                        instrumetal_step_profile, slit, mode="same"
                    )
                convolution_profile = convolution_profile_uncut[
                    convolution_profile_uncut > max(convolution_profile_uncut) / 1000
                ]

        self.y = fftconvolve(self.y, convolution_profile, mode="same")

        if not len(self.y) > 0:
            self.y = (
                np.ones(numpoints) * 1e100
            )  # if the array gets destroyed by fftconvolve,
            # set array to ridiculously huge values
        if any(np.isnan(self.y)):
            self.y[:] = 1e100
            logging.debug("conv = %s", self.y)
        return

    def refine_mesh(self, points_per_nm=3000):
        """
        adds artificial zeros in between lines. Usually used after creating
        a simulated spectrum before convolution with slit function.
        Necessary for later comparing simulation with measurement.

        return:
        Spectrum objects with pretty many points (or fine mesh, if you prefer)
        """

        start_spec = np.min(self.x) - 2  # prevent lines from falling to edges
        end_spec = np.max(self.x) + 2

        no_of_points = int(np.abs(end_spec - start_spec) * points_per_nm)

        spec = np.zeros((no_of_points, 2))

        spec[:, 0] = np.linspace(start_spec, end_spec, no_of_points)

        for i in range(len(self.x)):
            index = int((self.x[i] - start_spec) * points_per_nm + 0.5)
            spec[index, 1] += self.y[i]
        self.x = spec[:, 0]
        self.y = spec[:, 1]
        return spec


def match_spectra(sim_spec, exp_spec):
    """
    Take two Spectrum objects with different x-axes
    (the ranges must partially overlap)
    and return a tuple of Spectrum objects defined at the same x-points.
    This enables comparing.
    Args:
    ----
    exp_spec: *Spectrum object*, experimental spectrum
    sim_spec: *Spectrum object*, simulated spectrum.

    Returns:
    (Spectrum_simulated, Spectrum_experimental): a tuple of Spectrum objects, with identical x-axes.
    """
    if len(sim_spec.x) == 0:
        return (Spectrum(x=exp_spec.x, y=np.zeros_like(exp_spec.x)), exp_spec)

    if np.min(exp_spec.x) < np.min(sim_spec.x):
        sim_spec.x = np.concatenate(
            [[min(exp_spec.x)], [min(sim_spec.x) - 1e-3], sim_spec.x]
        )
        sim_spec.y = np.concatenate([[0], [0], sim_spec.y])
    if np.max(exp_spec.x) > np.max(sim_spec.x):
        sim_spec.x = np.concatenate(
            [sim_spec.x, [max(sim_spec.x) + 1e-3], [max(exp_spec.x)]]
        )
        sim_spec.y = np.concatenate([sim_spec.y, [0], [0]])
    interp = interp1d(sim_spec.x, sim_spec.y)
    y_interp = interp(exp_spec.x)

    ret = (Spectrum(x=exp_spec.x, y=y_interp), exp_spec)

    return ret


def compare_spectra(spectrum_exp, spectrum_sim):
    """
    spectrum_exp: Spectrum object
    spectrum_sim: Spectrum object
    The wavelength axes are expected to differ, but overlap

    returns: sqrt of (sum of squares of differences of the spectra divided
             by (the number of points)**2 )
    """
    matched = match_spectra(spectrum_sim, spectrum_exp)
    dif = matched[0].y - matched[1].y
    logging.debug("len(dif) = %i", len(dif))
    logging.debug("dif = ")
    logging.debug("%s", dif)
    return dif


def compare_spectra_weighted(spectrum_exp, spectrum_sim):
    """
    weight the sum of squared residuals by the measured intensity at given position.
    """
    dif = compare_spectra(spectrum_exp, spectrum_sim)
    dif *= spectrum_exp.y
    return dif


def compare_spectra_reduced_susmq(spectrum_exp, spectrum_sim):
    """
    compare spectra, take the residuals and divide them by
    (len of the measured spectrum)**2,
    usefull, if the length of the measurement is expected to vary during the
    minimization process.
    """
    dif = compare_spectra(spectrum_exp, spectrum_sim)
    ret = np.dot(dif, dif) / len(dif) ** 2
    logging.debug("sumsq = {:.8e}".format(ret))
    if np.isnan(ret):
        ret = 1e100
    print("sumsq = ", ret)
    return ret


def add_spectra(simulated_spectra, amplitudes):
    """
    calculate linear combination of several Spectrum objects

    args:
    -----
    simulated_spectra: list of Spectrum objects

    amplitudes: list of floats, coefficients in the linear combination

    return:
    ------
    Spectrum object - linear combination of several Spectrum objects


    """
    if not simulated_spectra:
        return Spectrum()
    added_spectra = np.zeros((len(simulated_spectra[0].x), 2))
    added_spectra[:, 0] = simulated_spectra[0].x
    for amplitude, spectrum in zip(amplitudes, simulated_spectra):
        added_spectra[:, 1] += amplitude * spectrum.y
    ret = Spectrum(x=added_spectra[:, 0], y=added_spectra[:, 1], normalize=False)
    return ret


def voigt(x, y):
    """
    Taken from `astro.rug.nl <http://www.astro.rug.nl/software/kapteyn-beta/kmpfittutorial.html?highlight=voigt#voigt-profiles/>`_

    The Voigt function is also the real part of
    `w(z) = exp(-z^2) erfc(iz)`, the complex probability function,
    which is also known as the Faddeeva function. Scipy has
    implemented this function under the name `wofz()`
    """
    z = x + 1j * y
    I = wofz(z).real
    return I


def Voigt(nu, alphaD, alphaL, nu_0, A, a=0, b=0):
    """
    Taken from `astro.rug.nl <http://www.astro.rug.nl/software/kapteyn-beta/kmpfittutorial.html?highlight=voigt#voigt-profiles/>`_

    The Voigt line shape in terms of its physical parameters

    Args:
      **nu**:  light frequency axis

      **alphaD**:  Doppler broadening HWHM

      **alphaL**:  Lorentzian broadening HWHM

      **nu_0**:  center of the line

      **A**:  integral under the line

      **a**:  constant background

      **b**:  slope of linearly changing background (bg = a + b*nu)

    Returns:
      **V**: The voigt profile on the nu axis
    """
    if alphaD == 0:
        alphaD = 1e-10
    if alphaL == 0:
        alphaL = 1e-10
    f = np.sqrt(np.log(2))
    x = (nu - nu_0) / alphaD * f
    y = alphaL / alphaD * f
    backg = a + b * nu
    V = A * f / (alphaD * np.sqrt(np.pi)) * voigt(x, y) + backg
    return V
