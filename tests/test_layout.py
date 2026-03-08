from lightly_engineered.layout.mzm import mzm


def test_mzm_has_ports():
    c = mzm()
    assert "o1" in c.ports
    assert "o2" in c.ports
