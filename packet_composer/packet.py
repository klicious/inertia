from __future__ import annotations


class PacketFragment:
    def __init__(self, _field_name, _value, _field_size, _filler_position, _filler_type):
        self.field_name = _field_name
        self.value = _value
        self.field_size = _field_size
        self.filler_position = _filler_position
        self.filler_type = _filler_type

    def field_name(self, _field_name) -> PacketFragment:
        self.field_name = _field_name
        return self

    def value(self, _value) -> PacketFragment:
        self.value = _value
        return self

    def get_field_size(self):
        return int(self.field_size) if self.field_size else 0

    def field_size(self, _field_size) -> PacketFragment:
        self.field_size = _field_size
        return self

    def filler_position(self, _filler_position) -> PacketFragment:
        self.filler_position = _filler_position
        return self

    def fill_type(self, _fill_type) -> PacketFragment:
        self.filler_type = _fill_type
        return self

    def compose_java_field_declaration_using_builder(self):
        _field_size_str = self.get_field_size() if self.get_field_size() > 0 else ''
        _field_size_build = f".fieldSize({_field_size_str})"
        _padding_type = f".filler_position({self.filler_position})" if self.filler_position else ''
        _filler_type = f".fillerType({self.filler_type})" if self.filler_type else ''
        _additional_field_value = _field_size_build + _padding_type + _filler_type
        return f"private final PacketFragment {self.field_name}" \
               f" = PacketFragment.builder(){_additional_field_value}.build();"


class Packet:
    def __init__(self, _class_name: str, _packet_fragments: list):
        self.class_name: str = _class_name if _class_name else ''
        self.packet_fragments: list = _packet_fragments if _packet_fragments else []

    def compose_java_class(self):
        _annotations = f"@Data\n" \
                       f"@Builder\n" \
                       f"@NoArgsConstructor\n" \
                       f"@AllArgsConstructor\n"
        _field_declarations = ''
        for _packet_fragment in self.packet_fragments:
            _field_declarations += f"    {_packet_fragment.compose_java_field_declaration_using_builder()}\n"

        return f"{_annotations}" \
               f"public class {self.class_name} {{\n" \
               f"{_field_declarations}" \
               f"}}"

    def add_packet_fragment(self, packet_fragment: PacketFragment):
        self.packet_fragments.append(packet_fragment)
