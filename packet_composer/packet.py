from __future__ import annotations


class PacketFragment:
    def __init__(self, _field_name, _field_size, _padding_type, _fill_type):
        self.field_name = _field_name
        self.field_size = _field_size
        self.padding_type = _padding_type
        self.fill_type = _fill_type

    def field_name(self, _field_name) -> PacketFragment:
        self.field_name = _field_name
        return self

    def field_size(self, _field_size) -> PacketFragment:
        self.field_size = _field_size
        return self

    def padding_type(self, _padding_type) -> PacketFragment:
        self.padding_type = _padding_type
        return self

    def fill_type(self, _fill_type) -> PacketFragment:
        self.fill_type = _fill_type
        return self

    def print_java_field_declaration_using_builder(self):
        _field_size_build = f".fieldSize({self.field_size})" if self.field_size > 0 else ''
        _padding_type = f".paddingType({self.padding_type})" if self.padding_type else ''
        _fill_type = f".fillerType({self.fill_type})" if self.fill_type() else ''
        _additional_field_value = _field_size_build + _padding_type + _fill_type
        return f"private final PacketFragment {self.field_name} = PacketFragment.builder(){_additional_field_value}.build();"


class Packet:
    def __init__(self, _class_name: str, _packet_fragments: list):
        self.class_name: str = _class_name
        self.packet_fragments: list = _packet_fragments

    def print_java_class(self):
