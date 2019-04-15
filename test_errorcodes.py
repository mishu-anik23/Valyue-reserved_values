import xml.etree.cElementTree as ET
from signaldef import read_errorcodes


def test_errcodes_standard_no_errcode():
    errorcodes = None
    expected = {}
    assert read_errorcodes(errorcodes) == expected


def test_errcodes_standard_emptystring():
    errorcodes = ""
    expected = {}
    assert read_errorcodes(errorcodes) == expected


def test_errcodes_standard_no_errcodes():
    errcodes = ET.fromstring("<errorcodes/>")
    expected = {}
    assert read_errorcodes(errcodes) == expected


def test_errcodes_standard_errcode():
    errcodes = """
<errorcodes>
<errorcode hexvalue="0x0000" desc="IM_0"/>
<errorcode hexvalue="0xFFFF" desc="IM_7"/>
<errorcode hexvalue="0xFFFE" desc="IM_6"/>
<errorcode hexvalue="0xFFFD" desc="IM_5"/>
<errorcode hexvalue="0xFFFC" desc="IM_4"/>
<errorcode hexvalue="0xFFFB" desc="IM_3"/>
<errorcode hexvalue="0xFFFA" desc="IM_2"/>
<errorcode hexvalue="0xFFF9" desc="IM_1"/>
</errorcodes>   
"""
    expected = {0x0000: 'IM_0', 0xFFFF: 'IM_7', 0xFFFE: 'IM_6', 0xFFFD: 'IM_5', 0xFFFC: 'IM_4',
                0xFFFB: 'IM_3', 0xFFFA: 'IM_2', 0xFFF9: 'IM_1'}
    assert read_errorcodes(errcodes) == expected
