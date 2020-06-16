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

    def compose_java_field_declaration_using_builder(self):
        _field_size_build = f".fieldSize({self.field_size})" if self.field_size > 0 else ''
        _padding_type = f".paddingType({self.padding_type})" if self.padding_type else ''
        _fill_type = f".fillerType({self.fill_type})" if self.fill_type() else ''
        _additional_field_value = _field_size_build + _padding_type + _fill_type
        return f"private final PacketFragment {self.field_name} = PacketFragment.builder(){_additional_field_value}.build();"


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
            _field_declarations = f"    {_packet_fragment.print_java_field_declaration_using_builder()}\n"

        return f"{_annotations}" \
               f"public class {self.class_name} {{" \
               f"{_field_declarations}" \
               f"}}"

    def add_packet_fragment(self, packet_fragment: PacketFragment):
        self.packet_fragments.append(packet_fragment)

