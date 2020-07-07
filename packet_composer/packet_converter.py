import constants
import os

from packet_composer.packet import Packet
from packet_composer.packet import PacketFragment
import pandas as pd


def extract_packets_info_from_file(_filename: str):
    _df = pd.read_excel(os.path.join(constants.INPUT_DIRECTORY, _filename))
    class_name_col = 'className'
    field_name_col = 'fieldName'
    value_col = 'value'
    field_size_col = 'fieldSize'
    filler_type_col = 'fillerType'
    filler_position_col = 'fillerPosition'

    _packets: list[:Packet] = []

    _packet = None
    for index, row in _df.iterrows():
        _class_name = row[class_name_col]
        if not pd.isna(_class_name):
            if _packet:
                _packets.append(_packet)
            _packet = Packet(_class_name, [])
        _field_name = row[field_name_col]
        if _packet and _field_name:
            _value = '' if pd.isna(row[value_col]) else row[value_col]
            _field_size = '' if pd.isna(row[field_size_col]) else row[field_size_col]
            _filler_type = '' if pd.isna(row[filler_type_col]) else row[filler_type_col]
            _filler_position = '' if pd.isna(row[filler_position_col]) else row[filler_position_col]

            packet_fragment = PacketFragment(_field_name, _value, _field_size, _filler_position, _filler_type)
            _packet.add_packet_fragment(packet_fragment)
    _packets.append(_packet)
    return _packets


packets = extract_packets_info_from_file('packet_input.xlsx')
print('=================================================')
for packet in packets:
    print(packet.compose_java_class())
    print('=================================================')
