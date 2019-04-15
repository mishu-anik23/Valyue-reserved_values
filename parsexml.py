import os
import xml.etree.cElementTree as ET
from signaldef import *
from parsexml import *


def get_version(xml_root):
    if xml_root.tag != 'sentconfiguration':
        raise ValueError("The root element of an XML signal definition must be <sentconfiguration>")
    version = int(xml_root.get('version', '1'))
    return version


def parse_predefined_signals(xml_node):
    """Extract frame control (FC) and data consistency check (DCC) from <frame> element"""
    local_context = {}
    for predef_signal in xml_node.findall('predefinedsignal'):
        if predef_signal.attrib['name'] == 'FC':
            fc = predef_signal.attrib['framecounter']
            local_context['fc'] = fc
    return local_context


def parse_frame(xml_node, context):
    """Extract signal definitions from <frame> element"""
    local_context = context.copy()

    local_context.update(parse_predefined_signals(xml_node))
    signals = [
        create_signal(signal_definition, context=local_context)
        for signal_definition in xml_node.findall('signaldefinition')
    ]
    return signals


def parse_bus(xml_bustree, context):
    """
    Extract signal definitions from <bus> element
    :return signal list and mode ('simplex' or 'multiplex')
    """
    local_context = context.copy()
    mode = xml_bustree.attrib['mode']
    local_context['mode'] = mode
    signals = []
    for xml_frametree in xml_bustree.iterfind('frame'):
        signals += parse_frame(xml_frametree, context=context)
    return signals, mode


def get_sig_by_fc(sigconfdct, fc):
    """Retrieve all signals that match a given framecounter.

    :param fc: frame counter to look for
    :return: List of Signal objects that match the frame counter.
    """
    multiplex_signals = sigconfdct['multiplex']
    signals = [signal
               for signal in multiplex_signals
               if signal.frame_number == fc
               ]
    return signals



def read_sigdef(xml_filename):
    """
    Read signal configuration from signaldefinition.xml file
    :param xml_filename: path to signalconfiguration file (XML)
    """
    # try:
    #     xml_tree = ET.parse(xml_filename)
    # except ET.ParseError as exc:
    #     raise DataError("Could not parse {}: {}".format(xml_filename, exc))

    xml_tree = ET.parse(xml_filename)

    context = dict()  # store properties from higher levels of XML that are needed at lower levels
    context['version'] = get_version(xml_tree.getroot())
    sigconf = {'multiplex': [], 'simplex': []}
    xml_bustrees = xml_tree.findall('.//bus')
    for xml_bustree in xml_bustrees:
        mode_signals, mode = parse_bus(xml_bustree, context)
        sigconf[mode] = mode_signals[:]
    return sigconf


if __name__ == '__main__':
    xml_file_path = os.path.join(os.getcwd(), "signaldefinition.xml")
    sig_conf = read_sigdef(xml_file_path)
    frames = []
    for fc in range(16):
        frame = get_sig_by_fc(sig_conf, fc)
        if frame:
            frames.append(frame)
            #print("***", frame)
    print(frames)
    print(len(frames))
