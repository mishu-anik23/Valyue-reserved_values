import pytest
from signaldef import *

input_sig_level_old = """
<signaldefinition alt_name="Level signal 1" name="Level signal 2 - Combi-sensor">
    <encoding bitsize="16" lsn="0" msn="3" reversed="0"/>
    <physical minimum="0" maximum="600" offset="0" factor="100" unit="mm" format=".2f"/>
    <default>0</default>
</signaldefinition>
"""

input_sig_temp_old = """
<signaldefinition alt_name="Temperature" name="Temperature">
    <encoding bitsize="16" lsn="0" msn="3" reversed="0"/>
    <physical minimum="-40" maximum="165" offset="40" factor="128" unit="°C" format=".3f"/>
    <default>0</default>
</signaldefinition>
"""

input_sig_temp_new = """
<signaldefinition alt_name="Temperature" name="Temperature">
    <encoding bitsize="16" lsn="0" msn="3" reversed="0"/>
    <physical_sae x1="-40" x2="165" y1="1" y2="26241" unit="°C" format=".3f"/>
    <default>0</default>
</signaldefinition>
"""

input_sig_temp_both = """
<signaldefinition alt_name="Temperature" name="Temperature">
    <encoding bitsize="16" lsn="0" msn="3" reversed="0"/>
    <physical minimum="-40" maximum="165" offset="40" factor="128" unit="°C" format=".3f"/>
    <physical_sae x1="-40" x2="165" y1="1" y2="26241" bitwidth="16"/>
    <default>0</default>
</signaldefinition>
"""

input_sig_temp_no_phy = """
<signaldefinition alt_name="Temperature" name="Temperature">
    <encoding bitsize="16" lsn="0" msn="3" reversed="0"/>
    <default>0</default>
</signaldefinition>
"""


def test_old_phy_to_new_phy_level():
    bitwidth = 16
    expected = Physical(x1=0, x2=600, y1=1, y2=60001, bitwidth=bitwidth, unit='mm', format='.2f' )
    ret_phy = Physical.from_xml(input_sig_level_old, bitwidth=bitwidth)
    assert ret_phy == expected


def test_old_phy_to_new_phy_temp():
    bitwidth = 16
    expected = Physical(x1=-40, x2=165, y1=1, y2=26241, bitwidth=bitwidth, unit='°C', format='.3f')
    ret_phy = Physical.from_xml(input_sig_temp_old, bitwidth=bitwidth)
    assert ret_phy == expected


def test_new_phy_to_new_phy_temp():
    bitwidth = 16
    expected = Physical(x1=-40, x2=165, y1=1, y2=26241, bitwidth=bitwidth, unit='°C', format='.3f')
    ret_phy = Physical.from_xml(input_sig_temp_new, bitwidth=bitwidth)

    assert expected.bitwidth == ret_phy.bitwidth
    assert expected.x1 == ret_phy.x1
    assert expected.x2 == ret_phy.x2
    assert expected.y1 == ret_phy.y1
    assert expected.y2 == ret_phy.y2
    assert expected.unit == ret_phy.unit
    assert expected.format == ret_phy.format

    assert ret_phy == expected


def test_both_phy_temp():
    bitwidth = 16
    expected = Physical(x1=-40, x2=165, y1=1, y2=26241, bitwidth=bitwidth, unit='°C', format='.3f')
    with pytest.raises(ValueError) as exc:
        ret_phy = Physical.from_xml(input_sig_temp_both, bitwidth=bitwidth)
        assert 'contains both' in str(exc)


def test_no_phy_temp():
    bitwidth = 16
    expected = Physical(x1=-40, x2=165, y1=1, y2=26241, bitwidth=bitwidth, unit='°C', format='.3f')
    with pytest.raises(ValueError) as exc:
        ret_phy = Physical.from_xml(input_sig_temp_both, bitwidth=bitwidth)
        assert 'does not contain' in str(exc)


def test_old_phy_attrs_to_new_phy_attrs():
    bitwidth = 16
    ret_phy = Physical.from_xml(input_sig_temp_old, bitwidth=bitwidth)

    assert ret_phy.x1 == -40
    assert ret_phy.x2 == 165
    assert ret_phy.y1 == 1
    assert ret_phy.y2 == 26241
    assert ret_phy.bitwidth == 16
    assert ret_phy.unit == "°C"
    assert ret_phy.format == ".3f"


def test_new_phy_attrs_to_new_phy_attrs():
    bitwidth = 16
    ret_phy = Physical.from_xml(input_sig_temp_new, bitwidth=bitwidth)

    assert ret_phy.x1 == -40
    assert ret_phy.x2 == 165
    assert ret_phy.y1 == 1
    assert ret_phy.y2 == 26241
    assert ret_phy.bitwidth == 16
    assert ret_phy.unit == "°C"
    assert ret_phy.format == ".3f"


if __name__ == "__main__":
    pytest.main([__file__])