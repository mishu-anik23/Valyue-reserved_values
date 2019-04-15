"""
Functions and classes to define the SENT signal according to SAE J2716 specification.
"""

import numbers
import xml.etree.ElementTree as ET
from math import floor
from collections import namedtuple
from xml.etree import cElementTree as ET

from signalrow_valid import *


SignalDetails = namedtuple('SignalDetails', ['name', 'minimum', 'maximum', 'unit',
                                             'validate', 'indicate', 'default', 'format', 'frame'])

def intorfloat(x):
    """Convert string input to int if possible, otherwise try converting to float

    Numeric input (instances of numbers.Real) will be returned unchanged.
    Other input that cannot be converted to int or float will raise a ValueError.
    """
    if isinstance(x, numbers.Real):
        return x
    try:
        return int(x)
    except ValueError:
        return float(x)


def high_clamp(bitwidth):
    return (1 << bitwidth) - 8


def calc_y2(x1, x2, resolution):
    y1 = 1
    phy_range_diff = x2 - x1
    y2 = (phy_range_diff / resolution) + y1
    return y1, y2


def spec_conti(minimum, maximum, resolution, bitwidth, errorcodes, offset=None):
    offset_y_low = 0
    if errorcodes:
        min_raw_value = min(errorcodes, key=errorcodes.get)
        if min_raw_value == 0:
            offset_y_low = 1

    if offset is not None:
        offset = offset_y_low
    range_diff = intorfloat(maximum) - intorfloat(minimum)
    offset_y_high = (range_diff / float(resolution)) + offset

    phy_obj = Physical(x1=minimum, x2=maximum, y1=offset_y_low, y2=offset_y_high, bitwidth=bitwidth,
                       errorcodes=errorcodes)
    return phy_obj


def create_signal(xml_signaldefinition, context=None):
    """
    Create a SignalDefinition object with frame control value for the XML signal definition
    :param context:
    :param xml_signaldefinition: XML fragment or ElementTree node for <signaldefinition>
    :return: SignalDefinition object
    """
    """Return a SignalDefinition object for the XML signal definition with frame control set
    """
    signal = SignalDefinition.from_xml(xml_signaldefinition, context=context)
    # print("***", signal)
    return signal


def get_default(xml_signaldefinition):
    """
    Get the value from the xml <default> tag
    :return signal default value (as a number), or None if the tag does not exist
    """
    default = xml_signaldefinition.find('default')
    try:
        return intorfloat(default.text)
    except AttributeError:
        return None


class SignalEncoding:

    def __init__(self, bitsize=None):
        self.bitsize = int(bitsize)

    def __repr__(self):
        template = "SignalEncoding(bitsize={0.bitsize})"
        return template.format(self)

    def __eq__(self, other):
        return self.bitsize == other.bitsize

    @classmethod
    def from_xml(cls, xml_fragment):
        """Create Encoding object from an XML fragment
        :param context:
        """
        if isinstance(xml_fragment, str):
            xml_fragment = ET.fromstring(xml_fragment)
        encoding = xml_fragment.find('encoding')
        if encoding is None:
            raise ValueError("XML fragment does not contain an <encoding> tag")
        return cls(encoding.attrib['bitsize'])


class Physical:
    """
    Physical represents the translation between raw signal values measured in sensor domain and
    physical units given in the Tkinter Entry widget by user.
    """
    def __init__(self, x1, x2, y1, y2, bitwidth, unit=None, format=None, errorcodes=None):
        try:
            self.x1 = intorfloat(x1)
            self.x2 = intorfloat(x2)
        except TypeError:
            raise ValueError("Missing or non-numeric input for x1 or x2")
        # if unit is None:
        #     raise ValueError("Parameter unit must be given")
        self.y1 = int(y1)
        self.y2 = int(y2)
        self.bitwidth = bitwidth
        self.unit = unit
        self.format = format
        self.errorcodes = errorcodes
        #self.low_clamp = 1
        #self.high_clamp = high_clamp(bitwidth)
        self.max_raw = (1 << self.bitwidth) - 1
        self.reserved_values = {}


    def __repr__(self):
        template = "Physical(x1={0.x1}, x2={0.x2}, y1={0.y1}, y2={0.y2}, bitwidth={0.bitwidth!r}," \
                   "errorcodes={0.errorcodes!r})"
        return template.format(self)

    def __eq__(self, other):
        attrs = ['x1', 'x2', 'y1', 'y2', 'bitwidth', 'unit', 'format']
        return all(getattr(self, attr) == getattr(other, attr) for attr in attrs)

    @property
    def min_reserved_value(self):
        if self.reserved_values:
            return min(self.reserved_values, key=self.reserved_values.get)
        else:
            return 0

    @property
    def low_clamp(self):
        if self.min_reserved_value == 0:
            return 1
        else:
            return 0

    @property
    def high_clamp(self):
        if self.min_reserved_value != 0:
            return self.min_reserved_value
        elif not self.reserved_values:
            return self.max_raw
        else:
            return sorted(self.reserved_values.keys())[1]

    @classmethod
    def from_xml(cls, xml_fragment, bitwidth):
        if isinstance(xml_fragment, str):
            xml_fragment = ET.fromstring(xml_fragment)
        physical_sae = xml_fragment.find('physical_sae')
        physical = xml_fragment.find('physical')
        bitfield = xml_fragment.find('isbitfield')

        if physical_sae is None and physical is None:
            raise ValueError("XML fragment does not contain a <physical_sae> or <physical> tag")
        elif physical_sae is not None and physical is not None:
            raise ValueError("XML fragment contains both <physical_sae> and <physical> tag")
        else:
            if physical_sae is not None:
                errorcodes_xml = physical_sae.find('errorcodes')
                errorcodes = read_errorcodes(errorcodes_xml)
                phy_obj = Physical(**physical_sae.attrib, bitwidth=bitwidth, errorcodes=errorcodes)
            else:
                errorcodes_xml = physical.find('errorcodes')
                errorcodes = read_errorcodes(errorcodes_xml)
                print(errorcodes)
                minimum = intorfloat(physical.attrib['minimum'])
                maximum = intorfloat(physical.attrib['maximum'])
                resolution = 1 / (intorfloat(physical.attrib['factor']))
                offset = intorfloat(physical.attrib['offset'])
                phy_obj = spec_conti(minimum, maximum, resolution, bitwidth, errorcodes, offset)
                phy_obj.format = physical.attrib['format']
                phy_obj.unit = physical.attrib['unit']
        return phy_obj

    def raw2phys(self, raw_value):
        """
        Convert a raw value to a physical value according to SAE J2716 specification.
        :param raw_value: raw value (int)
        :return: physical value as a number (float or int)
        """
        slope = (self.y2 - self.y1) / (self.x2 - self.x1)
        physical_value = self.x1 + (raw_value - self.y1) / slope
        return physical_value

    def phy2raw(self, phys_value):
        """
        Convert a physical value to a raw value according to SAE J2716 specification.
        :param phys_value: physical value as a number (float or int)
        :return: raw value (int)
        """
        slope = (self.y2 - self.y1) / (self.x2 - self.x1)
        raw_val = floor((self.y1 + slope * (phys_value - self.x1)) + 0.5)
        # print(raw_val)
        if raw_val <= self.low_clamp:
            raw_val = self.low_clamp
        elif raw_val >= self.high_clamp:
            raw_val = self.high_clamp
        return raw_val

    def set_reserved_values(self, xml_fragment_errcode):
        for errcode in xml_fragment_errcode:
            raw_value = int(errcode.attrib['hexvalue'], 16)
            self.reserved_values[raw_value] = errcode.attrib['desc']


    def reserved_value(self, raw_value):
        upper_limit = self.max_raw + 1
        index = upper_limit - raw_value
        indicator_message_list = ["IM_0", "IM_1", "IM_2", "IM_3", "IM_4", "IM_5", "IM_6", "IM_7"]
        if raw_value == 0:
            indicator_message = indicator_message_list[0]
        elif 1 <= index <= 7:
            indicator_message = indicator_message_list[index]
        else:
            indicator_message = ""
        return indicator_message

    def validate_raw_value(self, raw_val):
        if raw_val >= self.max_raw:
            ret_val, status = 0, Status.ERROR.name
        else:
            ret_val, status = raw_val, Status.WARNING.name
        return ret_val, status

    def validate_phy_value(self, phy_value):
        if self.min_reserved_value == 0:
            start_lower_range = 2
            end_upper_range = self.high_clamp - 1
        else:
            start_lower_range = 1
            end_upper_range = self.max_raw
        end_lower_range = self.y1 - 1
        start_upper_range = self.y2 + 1
        # end_upper_range = (1 << self.bitwidth) - 9

        converted_raw_value = self.phy2raw(phy_value)

        if self.x1 <= phy_value <= self.x2:
            signal_quality = Status.OK.name
        elif converted_raw_value == self.y1 or converted_raw_value == self.y2:
            signal_quality = Status.WARNING.name
        elif (start_lower_range <= converted_raw_value <= end_lower_range or
              start_upper_range <= converted_raw_value <= end_upper_range):
            signal_quality = Status.WARNING.name
        else:
            signal_quality = Status.ERROR.name
        return converted_raw_value, signal_quality


class SignalDefinition:
    """
    The SignalDefinition class stores all the information contained in a <signaldefinition> tag
    """

    def __init__(self, name, minimum, maximum, unit, physical, alt_name=None, encoding=None,
                 default=None, frame_number=None, context=None):

        context = context or {}

        self.name = name
        self.alt_name = alt_name
        self.minimum = minimum
        self.maximum = maximum
        self.unit = unit
        self.physical = physical
        self.encoding = encoding
        self.default = default
        self.frame_number = frame_number
        self.frame_number = context.get('fc', frame_number)
        if self.frame_number is not None:
            self.frame_number = int(self.frame_number)

    def __repr__(self):
        return ('SignalDefinition(name={!r}, alt_name={!r}, minimum={!r}, maximum={!r}, unit={!r},'
                ' encoding={}), physical={}, default={!r}, frame_number={!r})'.
                format(self.name, self.alt_name, self.minimum, self.maximum, self.unit,
                       self.encoding, self.physical, self.default, self.frame_number))

    def __eq__(self, other):
        attrs = ['name', 'alt_name', 'minimum', 'maximum', 'unit', 'encoding', 'physical', 'default', 'frame_number']
        return all(getattr(self, a) == getattr(other, a) for a in attrs)

    @property
    def display_format(self):
        return self.physical.format

    @classmethod
    def from_xml(cls, xml_fragment, context=None):
        """
        Create a SignalDefinition from an XML fragment
        :param context:
        :param xml_fragment: an ElementTree element or a XML string beginning with <signaldefinition>
        :return: SignalDefinition object including encoding and physical range information
        """
        context = context or {}
        if isinstance(xml_fragment, str):
            xml_fragment = ET.fromstring(xml_fragment)
        if xml_fragment.tag != 'signaldefinition':
            raise ValueError("XML fragment is not a <signaldefinition>")

        encoding = SignalEncoding.from_xml(xml_fragment)
        physical = Physical.from_xml(xml_fragment, encoding.bitsize)
        # print("####", physical)
        return cls(
            name=xml_fragment.attrib['name'],
            alt_name=xml_fragment.attrib['alt_name'],
            minimum=str(physical.x1),
            maximum=str(physical.x2),
            unit=str(physical.unit),
            encoding=encoding,
            physical=physical,
            default=get_default(xml_fragment),
            context=context,
        )

    def str2number(self, entry_input):
        try:
            if entry_input[:2] == '0x':
                base = 16
                entry_type = EntryType.RAW.name
            elif entry_input[:2] == '0b':
                base = 2
                entry_type = EntryType.RAW.name
            else:
                base = 10
                entry_type = EntryType.PHYSICAL.name
            converted_value = int(entry_input, base)
        except ValueError:
            try:
                converted_value = float(entry_input)
                entry_type = EntryType.PHYSICAL.name
            except ValueError:
                return 0, EntryType.INVALID.name
        return converted_value, entry_type

    def validate_str_entry(self, str_entry):
        value, typ = self.str2number(str_entry)
        if typ == EntryType.RAW.name:
            raw_val, status = self.physical.validate_raw_value(value)
        elif typ == EntryType.PHYSICAL.name:
            raw_val, status = self.physical.validate_phy_value(value)
        else:
            raw_val, status = 0, Status.ERROR.name
        return raw_val, status

    def get_signal_details(self):
        obj_sig_detail = SignalDetails(self.name,
                                       self.minimum,
                                       self.maximum,
                                       self.unit,
                                       self.validate_str_entry,
                                       bg_color_indicator,
                                       self.default,
                                       self.display_format,
                                       self.frame_number)
        return obj_sig_detail


def read_errorcodes(errorcodes_xml):
    if not errorcodes_xml:
        return {}
    if isinstance(errorcodes_xml, str):
        errorcodes_xml = ET.fromstring(errorcodes_xml)
    reserved_values = {}
    for errcode in errorcodes_xml:
        raw_value = int(errcode.attrib['hexvalue'], 16)
        reserved_values[raw_value] = errcode.attrib['desc']
    return reserved_values