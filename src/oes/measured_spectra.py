import json
import pickle
import warnings
from collections import OrderedDict

import lmfit
import numpy
import pandas
from asteval import valid_symbol_name

from oes.specdata import SpecDB, generate_spectrum, spectrum


class Parameters(object):
    """Class containing the parameters of the fit. Contains also instance
    of lmfit.Parameters class (as self.prms). The respective parameters can be
    accessed via __getitem__() method (i.e. brackets), just like in a
    dictionary. Apart from that contains also some extra information
    necessary for measured_spectra to run properly, such as number of
    pixels and list of relevant species.

    It is usually not necessary to explicitly call any class methods,
    as this is accomplished from MeasuredSpectra objects.
    """

    def __init__(self, *args, **kwargs):
        """
        wav_shift: an offset of the wavelength-axis in nm
        wav_step: mean step of the wavelength-axis

        slitf_gauss: gaussian HWHM of the slit function
        slitf_lorentz: lorentzian HWHM of the slit function

        baseline: *float* constant offset of the spectrum from zero

        baseline_slope: *float* accounts for non-constant baseline (necessary on some older spectrometers,
                        otherwise should be kept fixed at 0)

        simulations: list of specDB objects, or simply empty list []
        """
        self.number_of_pixels = kwargs.pop("number_of_pixels", 1024)
        self.prms = lmfit.Parameters()
        self.info = {"species": []}
        wav_shift = kwargs.pop("wav_shift", 0)
        self.prms.add("wav_shift", value=wav_shift)
        wav_step = kwargs.pop("wav_step", 1e-2)
        self.prms.add("wav_step", value=wav_step)

        gauss = kwargs.pop("slitf_gauss", 1e-9)
        lorentz = kwargs.pop("slitf_lorentz", 1e-9)
        self.prms.add("slitf_gauss", value=gauss)
        self.prms.add("slitf_lorentz", value=lorentz)

        baseline = kwargs.pop("baseline", 0)
        self.prms.add("baseline", value=baseline)

        baseline_slope = kwargs.pop("baseline_slope", 0)
        self.prms.add("baseline_slope", value=baseline_slope)

        simulations = kwargs.pop("simulations", None)
        if simulations is not None:
            for sim in simulations:
                self.add_specie(sim)

    def __getitem__(self, key):
        return self.prms.__getitem__(key)

    def keys(self):
        return self.prms.keys()

    def add_specie(self, specie, **kwargs):
        """
        specie: specDB object
        """
        Trot = kwargs.pop("Trot", 1e3)
        Tvib = kwargs.pop("Tvib", 1e3)
        intensity = kwargs.pop("intensity", 1)
        specie_name = specie.specie_name
        if valid_symbol_name(specie_name) and specie_name not in self.info["species"]:
            self.info["species"].append(specie_name)
            # self.info[specie_name+'_sim'] = specie # specDB object
            self.prms.add(specie_name + "_Trot", value=Trot)
            self.prms[specie_name + "_Trot"].min = 300
            self.prms[specie_name + "_Trot"].max = 10000
            self.prms.add(specie_name + "_Tvib", value=Tvib)
            self.prms[specie_name + "_Tvib"].min = 300
            self.prms[specie_name + "_Tvib"].max = 10000
            self.prms.add(specie_name + "_intensity", value=intensity)
            self.prms[specie_name + "_intensity"].min = 0
        else:
            msg = (
                "Specie '"
                + specie_name
                + "' not added: Invalid name or already added! See lmfit.Parameters for details."
            )
            warnings.warn(msg, Warning)

    def rm_species(self, specie):
        """
        Remove simulated spectrum of given specie.

        specie: string, name of the specie (eg. \'OH\')
        """
        self.info["species"].remove(specie)
        self.prms.pop(specie + "_Trot", 0)
        self.prms.pop(specie + "_Tvib", 0)
        self.prms.pop(specie + "_intensity", 0)

    def save(self, filename):
        with open(filename, "wb") as output:
            pickle.dump(self, output, pickle.HIGHEST_PROTOCOL)

    @staticmethod
    def load(filename):
        with open(filename, "rb") as input:
            return_val = pickle.load(input)
        return return_val


class MeasuredSpectra:
    """Class containing the measured data. Suitable for storing number of
    spectra (high numbers are possible, but it is not optimized to be
    memory efficient - all spectra will be loaded into the memory at
    initiating an instance of MeasuredSpectra). A reasonable strategy
    is to divide large measurements into several MeasuredSpectra
    objects.

    It also keeps references to spectral simulations and contains
    methods for least squares fitting.

    """

    def __init__(self, **kwargs):
        """Most of the kwargs are never used in the class methods and serve
        only for future reference - to allow the experimenter to keep
        track of the important metadata.

        The only exception is `spectra` that can be used to fill in
        the measured data. The format of this should be a list of
        iterables (tuples or lists) containing [identificator, data],
        where identificator can be a string or a number (can contain
        e.g. spatial position or delay after the trigger) and data
        should be in the form of a Spectrum object.

        kwargs:

        spectra: a nested OrderedDict with keys defined by the user (typically used
        for experimental info,  such as physical coordinates or experimental
        conditions). Each value contains again a dictionary with 'params' and 'spectrum'.
        'params' are of type Parameters,
        'spectrum' are Spectrum objects. The wavelengths are believed to be
        right except for a constant offset.

        spectra (OrderedDict)
          {spectrum_id: {'params': Parameters,
                        'spectrum': Spectrum}}

        at the time of init, only 'data' of each dict should be defined,
        the 'params' will be added by automatically by
        MeasuredSpectra.create_fit_parameters()

        filename: *string* - name of the file with the source data. Only for future reference, can be omitted.

        date: defaults to 0, but can be used to keep the date of the measurement. Format is arbitrary.

        time: defaults to 0, but can be used to keep the time of the measurement. Format is arbitrary.

        accumulations: to keep track of the number of accumulations.

        """

        self.filename = kwargs.pop("filename", "")
        self.date = kwargs.pop("date", 0)
        self.time = kwargs.pop("time", 0)
        self.accumulations = kwargs.pop("accumulations", 0)
        self.gatewidth = kwargs.pop("gatewidth", 0)
        self.regionofinterest_y = kwargs.pop("ROI_y", None)
        self.regionofinterest_x = kwargs.pop("ROI_x", None)

        self.spectra = kwargs.pop("spectra", OrderedDict())
        self.image_analysis_values = []
        self.image_analysis_values_used = []
        self.minimizer = None
        self.minimizer_result = None
        self.simulations = {}
        self.create_fit_parameters(**kwargs)

    @classmethod
    def from_csv(cls, filename, **genfromtxtargs):
        """Used to extract measured data from ASCII files containing the
        wavelengths in the first column and and intensity vectors of
        y-values in other columns. Delimiter can be set via genfromtxtargs:

        w1,y11,y21
        w2,y12,y22
        w3,y12,y23

        Other Parameters
        ----------------
        **genfromtxtargs: forwarded to :py:func:`numpy.genfromtxt`
            default : {"delimiter":','}
        ...

        """
        delimiter = genfromtxtargs.pop("delimiter", ",")
        dataarray = numpy.genfromtxt(filename, delimiter=delimiter, **genfromtxtargs)
        spec = OrderedDict()
        for i in range(1, dataarray.shape[1]):
            spec[i] = {
                "spectrum": spectrum.Spectrum(x=dataarray[:, 0], y=dataarray[:, i])
            }

        ret = MeasuredSpectra(filename=filename, spectra=spec)
        for spec in ret.spectra:
            s = ret.spectra[spec]
            step = numpy.mean(numpy.diff(s["spectrum"].x))
            if step <= 0:
                raise ValueError("The spectrum x-axis must be ordered ascendingly!")
            s["params"]["wav_step"].value = step
        return ret

    def add_specie(self, specie, specname, **kwargs):
        """use this spectral simulation for comparison with measured data.
                The reference to simulation object will be added
                to self.simulations and a string describing the specie will be
                added to Parameters.info dictionary.

        args:
           specie: specDB object
           specname: to which Parameters object the specie should be added

        """
        # specie_name = specie.specie_name
        if specie.specie_name not in self.simulations:
            self.simulations[specie.specie_name] = specie
        self.spectra[specname]["params"].add_specie(specie, **kwargs)

    def create_fit_parameters(self, **kwargs):
        """
            **kwargs:
        simulated_spectra: *list* of SpecDB objects

        wav_shift: a shift of the wavelength-axis in nm

        other kwargs are passed directly to Parameters.__init__()
        """
        simulated_spectra = kwargs.pop("simulated_spectra", [])
        for spec in self.spectra:
            if "params" not in self.spectra[spec]:
                self.spectra[spec]["params"] = Parameters(
                    number_of_pixels=len(self.spectra[spec]["spectrum"]), **kwargs
                )
                for specie in simulated_spectra:
                    self.add_specie(specie, spec, **kwargs)

    def save(self, filename):
        self.minimizer = None
        with open(filename, "wb") as output:
            pickle.dump(self, output, pickle.HIGHEST_PROTOCOL)

    def get_measured_spectrum(self, specname):
        s = self.spectra[specname]["spectrum"]
        wav_shift = self.spectra[specname]["params"]["wav_shift"].value
        return spectrum.Spectrum(x=s.x + wav_shift, y=s.y)

    def to_json(self, filename):
        spectra = OrderedDict()
        params = OrderedDict()
        for specname in self.spectra:
            if hasattr(self.spectra[specname]["spectrum"], "x"):
                spectra[str(specname)] = {
                    "x": list(self.spectra[specname]["spectrum"].x),
                    "y": list(self.spectra[specname]["spectrum"].y),
                }
            else:
                spectra[str(specname)] = list(self.spectra[specname]["spectrum"])

            par = self.spectra[specname]["params"]
            params[str(specname)] = {
                "number_of_pixels": par.number_of_pixels,
                "info": par.info,
                "prms": par.prms.dumps(),
            }

        simulations = []
        for simkey in self.simulations:
            simulations.append(simkey)
        to_save = {"spectra": spectra, "params": params, "simulations": simulations}

        with open(filename, "w") as fp:
            json.dump(to_save, fp)

    @staticmethod
    def from_json(filename):
        with open(filename, "r") as fp:
            loaded = json.load(fp, object_pairs_hook=OrderedDict)
        spectra = loaded["spectra"]
        # spec = []
        spec = OrderedDict()
        for s in spectra:
            if hasattr(spectra[s], "keys"):
                spec[s] = {
                    "spectrum": spectrum.Spectrum(
                        x=numpy.array(spectra[s]["x"]), y=numpy.array(spectra[s]["y"])
                    )
                }
            else:
                spec[s] = {"spectrum": numpy.array(spectra[s])}

        sims = {}
        for sim in loaded["simulations"]:
            sims[sim] = SpecDB(sim + ".db")

        for param, s in zip(loaded["params"], list(spec.keys())):
            to_app = Parameters(
                number_of_pixels=loaded["params"][param]["number_of_pixels"]
            )
            to_app.info = loaded["params"][param]["info"]
            try:
                to_app.prms.loads(loaded["params"][param]["prms"])
            except TypeError:
                for entry in json.loads(loaded["params"][param]["prms"]):
                    to_app.prms.add(
                        entry[0],
                        value=entry[1],
                        vary=entry[2],
                        min=entry[4],
                        max=entry[5],
                    )
            spec[s]["params"] = to_app

        ret = MeasuredSpectra(spectra=spec)

        ret.simulations = sims
        return ret

    def get_residuals(self, params: lmfit.Parameters, specname: str, **kwargs):
        """
        method with the desired signature for lmfit.minimize
        """
        convolve = kwargs.pop("convolve", True)
        step = params["wav_step"].value

        self.spectra[specname]["params"].prms = params
        our_params: Parameters = self.spectra[specname]["params"]

        measured_spec = self.get_measured_spectrum(specname)
        simulated_spec = generate_spectrum(
            our_params,
            step=step,
            sims=self.simulations,
            wmin=measured_spec.x.min(),
            wmax=measured_spec.x.max(),
        )

        return spectrum.compare_spectra(measured_spec, simulated_spec)

    def fit(self, specname, **kwargs):
        """Find optimal values of the fit parameters for spectrum identified by specname. The optimal values are then stored in self.spectra[specname]['params'], not returned!

        args:
        -----
        specname: identificator of spectrum to fit

        **kwargs:
        ---------
        maxiter: *int* maximal number of itertions, handy with slower optimization methods

        method: *string* see lmfit documentation for available methods

        by_peaks: *bool* defaults to False. If you own echelle spectrometer,
                  play around with enabling this option. Otherwise, leave it at false.
                  Never properly tested.

        return:
        -------
        result: *bool*, True if the fit converged successfully, False otherwise

        """

        print("********* specname = ", specname, " ************")
        kwargs["number_of_pixels"] = self.spectra[specname]["params"].number_of_pixels
        maxiter = kwargs.pop("maxiter", 2000)
        method = kwargs.pop("method", "leastsq")
        if method == "leastsq":
            self.minimizer = lmfit.Minimizer(
                self.get_residuals,
                self.spectra[specname]["params"].prms,
                fcn_args=(specname,),
                fcn_kws=kwargs,
                maxfev=maxiter,
            )
        else:
            self.minimizer = lmfit.Minimizer(
                self.get_residuals,
                self.spectra[specname]["params"].prms,
                fcn_args=(specname,),
                fcn_kws=kwargs,
                options={"maxiter": maxiter, "xtol": 0.05},
            )

        self.minimizer_result = self.minimizer.minimize(method=method)
        self.spectra[specname]["params"].prms = self.minimizer_result.params
        return self.minimizer_result

    def export_results(self, filename):
        """
        Save the results of the optimisation as csv file. Uses pandas.

        args:
        -----
        filename: *string* a name of the file, the data will be exported to.
                  Does NOT ask for confirmation before overwritng!
        """

        result = {"spectrum": [], "reduced_sumsq": []}

        for specie in self.simulations:
            result[specie + "_Trot"] = []
            result[specie + "_Trot_dev"] = []
            result[specie + "_Tvib"] = []
            result[specie + "_Tvib_dev"] = []
            result[specie + "_intensity"] = []
            result[specie + "_intensity_dev"] = []

        for specname in self.spectra:
            result["spectrum"].append(specname)
            # if the list of simulations is empty, do not calculate residuals
            if not self.spectra[specname]["params"].info["species"]:
                sumsq = numpy.nan
            else:
                residuals = self.get_residuals(
                    self.spectra[specname]["params"].prms, specname
                )

                sumsq = numpy.sum(residuals[~numpy.isinf(residuals)] ** 2)
                if hasattr(self.spectra[specname]["spectrum"], "y"):
                    y = self.spectra[specname]["spectrum"].y
                else:
                    y = self.spectra[specname]["spectrum"]
                sumsq /= numpy.sum(
                    y
                    - self.spectra[specname]["params"]["baseline"].value
                    - self.spectra[specname]["params"]["baseline_slope"]
                    * numpy.arange(len(self.spectra[specname]["spectrum"]))
                )
            result["reduced_sumsq"].append(sumsq)
            for specie in self.simulations:
                if specie in self.spectra[specname]["params"].info["species"]:
                    result[specie + "_Trot"].append(
                        self.spectra[specname]["params"][specie + "_Trot"].value
                    )

                    result[specie + "_Trot_dev"].append(
                        self.spectra[specname]["params"][specie + "_Trot"].stderr
                    )

                    result[specie + "_Tvib"].append(
                        self.spectra[specname]["params"][specie + "_Tvib"].value
                    )

                    result[specie + "_Tvib_dev"].append(
                        self.spectra[specname]["params"][specie + "_Tvib"].stderr
                    )

                    result[specie + "_intensity"].append(
                        self.spectra[specname]["params"][specie + "_intensity"].value
                    )

                    result[specie + "_intensity_dev"].append(
                        self.spectra[specname]["params"][specie + "_intensity"].stderr
                    )
                else:
                    result[specie + "_Trot"].append(numpy.nan)
                    result[specie + "_Tvib"].append(numpy.nan)
                    result[specie + "_Trot_dev"].append(numpy.nan)
                    result[specie + "_Tvib_dev"].append(numpy.nan)
                    result[specie + "_intensity"].append(numpy.nan)
                    result[specie + "_intensity_dev"].append(numpy.nan)

        out = pandas.DataFrame(result)
        out.to_csv(filename)
        return out
