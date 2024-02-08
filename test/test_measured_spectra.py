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

    return meas_spec

def test_fit(measured_spectra):
    for specname in measured_spectra.spectra:
        measured_spectra.fit(specname, maxiter=1)