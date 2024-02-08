import pytest
from oes.specdata import SpecDB
from oes.measured_spectra import MeasuredSpectra
import pathlib

DATA_DIR = pathlib.Path(__file__).parent


@pytest.fixture
def oh_ax():
    return SpecDB("OHAX.db")


@pytest.fixture
def measured_spectra(oh_ax):
    meas_spec = MeasuredSpectra.from_csv(DATA_DIR / "OH_310nm_surfatron_80Hz_mod.csv")
    for spec_name in meas_spec.spectra:
        meas_spec.add_specie(oh_ax, spec_name)
        meas_spec.spectra[spec_name]["params"]["wav_shift"].value = -0.02
        meas_spec.spectra[spec_name]["params"]["slitf_gauss"].value = 2.5e-2
        meas_spec.spectra[spec_name]["params"]["slitf_lorentz"].value = 2.5e-2
        meas_spec.spectra[spec_name]["params"]["slitf_gauss"].min = 0
        meas_spec.spectra[spec_name]["params"]["slitf_lorentz"].min = 0

    return meas_spec


def test_fit(measured_spectra):
    for specname in measured_spectra.spectra:
        measured_spectra.fit(specname)
        m = measured_spectra.get_measured_spectrum(specname)
        res = measured_spectra.get_residuals(
            measured_spectra.spectra[specname]["params"].prms,
            specname,
            number_of_pixels=len(m),
        )
        assert (m.y - m.y.min()).sum() / (
            res - res.min()
        ).sum() > 1.1  # residuals are smaller than the original data

        break  # it takes time and testing one fit is enough
