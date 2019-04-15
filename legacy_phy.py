import xml.etree.ElementTree as ET

errcode = """                
<signaldefinition alt_name="Amplitude 2nd ref" name="Amplitude 2">
    <encoding bitsize="8" lsn="2" msn="3" reversed="0"/>
    <physical minimum="0" maximum="24.7" offset="0" factor="10" unit="" format=".1f">
        <errorcodes>
            <errorcode hexvalue="0x000" desc="IM_0"/>

            <errorcode hexvalue="0xFFE" desc="IM_6"/>
            <errorcode hexvalue="0xFFB" desc="IM_3"/>

            <errorcode hexvalue="0xFF9" desc="IM_1"/>
        </errorcodes>
    </physical>
    <default>0</default>
</signaldefinition>

"""


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

sigdef_with_errcode = """
<signaldefinition alt_name="Temperature" name="Temperature">
    <encoding bitsize="16" lsn="0" msn="3" reversed="0"/>
    <physical minimum="-40" maximum="165" offset="40" factor="128" unit="°C" format=".3f">
        <errorcodes>
        
            <errorcode hexvalue="0xFFFE" desc="IM_6"/>
            <errorcode hexvalue="0xFFFD" desc="IM_5"/>
            <errorcode hexvalue="0xFFFC" desc="IM_4"/>

         </errorcodes>   
    </physical>
    <default>0</default>
</signaldefinition>
"""

if __name__ == '__main__':
    signal_fragment = ET.fromstring(errcode)
    err_fragment = signal_fragment.find('physical').find('errorcodes')
    reserved_values = read_errorcodes(err_fragment)
    print("+++", reserved_values)
    min_r = min(reserved_values, key=reserved_values.get)
    #min_r = min(reserved_values.keys(), key=lambda x: x[1])
    print(min_r)
    print(sorted(reserved_values.keys())[1])