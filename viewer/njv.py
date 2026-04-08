#!/usr/bin/env python3
"""
njv.py - BJData/Binary JSON viewer with SOA support
Usage: python3 njv.py file.jdb [--max-data 100] [--max-str 200] [--debug] [--big-endian]
"""
import sys, struct, json
from collections import OrderedDict

def make_markers(big_endian=False):
    e = ">" if big_endian else "<"
    return {
        b'Z': (0, None), b'N': (0, None), b'T': (0, None), b'F': (0, None),
        b'i': (1, e+'b'), b'U': (1, e+'B'), b'I': (2, e+'h'), b'u': (2, e+'H'),
        b'l': (4, e+'i'), b'm': (4, e+'I'), b'L': (8, e+'q'), b'M': (8, e+'Q'),
        b'h': (2, e+'e'), b'd': (4, e+'f'), b'D': (8, e+'d'), b'C': (1, e+'B'), b'B': (1, e+'B'),
    }

INT_TYPES = {b'i', b'U', b'I', b'u', b'l', b'm', b'L', b'M'}
NUM_TYPES = INT_TYPES | {b'h', b'd', b'D'}
FIXED_TYPES = NUM_TYPES | {b'C', b'B'}

class BJDataReader:
    def __init__(self, data, max_data=100, max_str=200, debug=False, big_endian=False):
        self.data, self.pos, self.max_data, self.max_str = data, 0, max_data, max_str
        self.debug, self.depth, self.markers = debug, 0, make_markers(big_endian)

    def log(self, msg):
        if self.debug: print(f"# {self.pos:6}: {'  '*self.depth}{msg}")

    def remaining(self): return len(self.data) - self.pos

    def read(self, n):
        if self.pos + n > len(self.data): raise EOFError(f"EOF at {self.pos}")
        result = self.data[self.pos:self.pos+n]
        self.pos += n
        return result

    def peek(self, n=1): return self.data[self.pos:self.pos+n]

    def read_int(self, marker=None):
        if marker is None: marker = self.read(1)
        size, fmt = self.markers[marker]
        return struct.unpack(fmt, self.read(size))[0]

    def read_string(self):
        length = self.read_int()
        return self.read(length).decode('utf-8', errors='replace') if length else ""

    def read_typed_values(self, marker, count):
        if marker in (b'T', b'F'): return [self.read(1) == b'T' for _ in range(count)]
        size, fmt = self.markers[marker]
        if count * size > self.remaining(): return "<truncated>"
        if count > self.max_data:
            vals = [struct.unpack(fmt, self.read(size))[0] for _ in range(min(8, count))]
            self.read((count - len(vals)) * size)
            return f"<{count} values: {vals[:4]}...>"
        return [struct.unpack(fmt, self.read(size))[0] for _ in range(count)]

    def read_value(self):
        marker = self.read(1)
        self.log(f"marker: {chr(marker[0]) if 32 <= marker[0] < 127 else marker.hex()}")
        if marker == b'Z': return None
        if marker == b'N': return self.read_value()
        if marker == b'T': return True
        if marker == b'F': return False
        if marker in NUM_TYPES:
            size, fmt = self.markers[marker]
            return struct.unpack(fmt, self.read(size))[0]
        if marker == b'C': return chr(self.read(1)[0])
        if marker == b'B': return self.read(1)[0]
        if marker in (b'S', b'H'): return self.read_string()
        if marker == b'E': return self.read_extension()
        if marker == b'[': self.log("array ["); return self.read_array()
        if marker == b'{': self.log("object {"); return self.read_object()
        raise ValueError(f"Unknown marker {marker!r} at {self.pos-1}")

    def read_array(self):
        self.depth += 1
        elem_type, count = None, None
        if self.peek() == b'$':
            self.read(1)
            elem_type = self.read(1)
            self.log(f"type: {chr(elem_type[0])}")
            if elem_type == b'{':
                result = self.read_soa('row', True)
                self.depth -= 1
                return result
        if self.peek() == b'#':
            self.read(1)
            if self.peek() == b'[':
                self.read(1)
                col_major = self.peek() == b'['
                if col_major: self.read(1)
                dims = self.read_dims()
                if col_major and self.peek() == b']': self.read(1)
                result = self.read_nd_array(elem_type, dims, col_major)
                self.depth -= 1
                return result
            count = self.read_int()
            self.log(f"count: {count}")
        if count is not None and elem_type:
            result = self.read_typed_values(elem_type, count)
        elif count is not None:
            result = [self.read_value() for _ in range(count)]
        else:
            result = []
            while self.peek() != b']': result.append(self.read_value())
            self.read(1)
        self.depth -= 1
        return result

    def read_dims(self):
        elem_type, count = None, None
        if self.peek() == b'$': self.read(1); elem_type = self.read(1)
        if self.peek() == b'#': self.read(1); count = self.read_int()
        if count and elem_type: dims = self.read_typed_values(elem_type, count)
        elif count: dims = [self.read_int() for _ in range(count)]
        else:
            dims = []
            while self.peek() != b']': dims.append(self.read_value())
            self.read(1)
        self.log(f"dims: {dims}")
        return dims

    def read_nd_array(self, elem_type, dims, col_major):
        total = 1
        for d in dims: total *= d
        size, fmt = self.markers[elem_type]
        if total * size > self.remaining(): return f"<{dims} {'col' if col_major else 'row'}: truncated>"
        if total > self.max_data:
            vals = [struct.unpack(fmt, self.read(size))[0] for _ in range(min(8, total))]
            self.read((total - len(vals)) * size)
            return f"<{dims} {'col' if col_major else 'row'}: {vals[:4]}...>"
        return [struct.unpack(fmt, self.read(size))[0] for _ in range(total)]

    def read_object(self):
        self.depth += 1
        elem_type, count = None, None
        if self.peek() == b'$':
            self.read(1)
            elem_type = self.read(1)
            self.log(f"type: {chr(elem_type[0])}")
            if elem_type == b'{':
                result = self.read_soa('column', True)
                self.depth -= 1
                return result
        if self.peek() == b'#':
            self.read(1)
            count = self.read_int()
            self.log(f"count: {count}")
        result, i = OrderedDict(), 0
        while (count is None and self.peek() != b'}') or (count is not None and i < count):
            key = self.read(self.read_int()).decode('utf-8', errors='replace')
            self.log(f"key: {key}")
            if elem_type:
                size, fmt = self.markers[elem_type]
                result[key] = struct.unpack(fmt, self.read(size))[0]
            else:
                result[key] = self.read_value()
            i += 1
        if count is None: self.read(1)
        self.depth -= 1
        return result

    # === SOA Support ===
    def read_soa(self, layout, brace_consumed=False):
        self.log(f"SOA {layout}-major")
        schema = self.read_schema(brace_consumed)
        while self.peek() == b'N': self.read(1)
        if self.peek() != b'#': raise ValueError(f"Expected # after SOA schema at {self.pos}")
        self.read(1)
        if self.peek() == b'[':
            self.read(1)
            col_major = self.peek() == b'['
            if col_major: self.read(1)
            dims = self.read_dims()
            if col_major and self.peek() == b']': self.read(1)
            count = 1
            for d in dims: count *= d
        else:
            count = self.read_int()
            dims = [count]
        self.log(f"SOA count={count} dims={dims}")
        return {"_SOA_": layout, "_dims_": dims, "_records_": self.decode_soa(schema, count, layout)}

    def read_schema(self, brace_consumed=False):
        if not brace_consumed and self.read(1) != b'{': raise ValueError("Expected { for schema")
        schema = []
        while self.peek() != b'}':
            name = self.read(self.read_int()).decode('utf-8')
            schema.append(self.read_field_type(name))
        self.read(1)
        self.log(f"schema: {[(f['name'], f.get('enc', f['type'])) for f in schema]}")
        return schema

    def read_field_type(self, name):
        marker = self.peek()
        # Fixed-size numeric types
        if marker in FIXED_TYPES:
            self.read(1)
            size, fmt = self.markers[marker]
            return {'name': name, 'type': 'fixed', 'bytes': size, 'fmt': fmt, 'marker': marker}
        # Boolean
        if marker in (b'T', b'F'):
            self.read(1)
            return {'name': name, 'type': 'bool', 'bytes': 1}
        # Null placeholder
        if marker == b'Z':
            self.read(1)
            return {'name': name, 'type': 'null', 'bytes': 0}
        # Fixed-length string/highprec
        if marker in (b'S', b'H'):
            self.read(1)
            return {'name': name, 'type': 'str', 'enc': 'fixed', 'bytes': self.read_int()}
        # Array types
        if marker == b'[':
            self.read(1)
            if self.peek() == b'$':
                self.read(1)
                inner = self.read(1)
                # Dict-based string: [$S#<n><strings>
                if inner in (b'S', b'H'):
                    self.read(1)  # #
                    num_entries = self.read_int()
                    dictionary = [self.read_string() for _ in range(num_entries)]
                    index_bytes = 1 if num_entries <= 255 else (2 if num_entries <= 65535 else 4)
                    index_marker = b'U' if index_bytes == 1 else (b'u' if index_bytes == 2 else b'm')
                    return {'name': name, 'type': 'str', 'enc': 'dict', 'bytes': index_bytes,
                            'dict': dictionary, 'index_marker': index_marker}
                # Offset-based string: [$<int-type>]
                if inner in INT_TYPES:
                    self.read(1)  # ]
                    size, fmt = self.markers[inner]
                    return {'name': name, 'type': 'str', 'enc': 'offset', 'bytes': size,
                            'index_marker': inner, 'index_fmt': fmt}
            # Fixed array: [ddd] or [TTT]
            elems, total_bytes = [], 0
            while self.peek() != b']':
                elem_marker = self.read(1)
                if elem_marker in FIXED_TYPES:
                    size, fmt = self.markers[elem_marker]
                    elems.append({'type': 'fixed', 'bytes': size, 'fmt': fmt, 'marker': elem_marker})
                    total_bytes += size
                elif elem_marker in (b'T', b'F'):
                    elems.append({'type': 'bool', 'bytes': 1})
                    total_bytes += 1
            self.read(1)
            return {'name': name, 'type': 'array', 'elems': elems, 'bytes': total_bytes}
        # Nested struct
        if marker == b'{':
            self.read(1)
            sub_schema = self.read_schema(True)
            return {'name': name, 'type': 'struct', 'schema': sub_schema,
                    'bytes': sum(f['bytes'] for f in sub_schema)}
        raise ValueError(f"Unknown schema type {marker!r} at {self.pos}")

    def read_extension(self):
        typeid = self.read_int()
        bytelen = self.read_int()
        payload = self.read(bytelen)
        return f"<ext:{typeid}:{payload.hex()}>"

    def decode_soa(self, schema, count, layout):
        record_bytes = sum(field['bytes'] for field in schema)
        payload = self.read(record_bytes * count)
        # Read offset tables and string buffers for offset-based fields
        for field in schema:
            if field.get('enc') == 'offset':
                size, fmt = self.markers[field['index_marker']][0], field['index_fmt']
                field['offsets'] = [struct.unpack(fmt, self.read(size))[0] for _ in range(count + 1)]
                field['strbuf'] = self.read(field['offsets'][-1]).decode('utf-8', errors='replace') if field['offsets'][-1] else ""
        # Decode based on layout
        if layout == 'column':
            columns, pos = {}, 0
            for field in schema:
                field_bytes = field['bytes'] * count
                columns[field['name']] = self.decode_column(field, payload[pos:pos+field_bytes], count)
                pos += field_bytes
            return [OrderedDict((f['name'], columns[f['name']][i]) for f in schema) for i in range(count)]
        else:  # row-major
            records = []
            for i in range(count):
                record, pos = OrderedDict(), i * record_bytes
                for field in schema:
                    record[field['name']] = self.decode_field(field, payload[pos:pos+field['bytes']], i)
                    pos += field['bytes']
                records.append(record)
            return records

    def decode_column(self, field, data, count):
        ftype, fbytes = field['type'], field['bytes']
        if ftype == 'fixed':
            return [struct.unpack(field['fmt'], data[i*fbytes:(i+1)*fbytes])[0] for i in range(count)]
        if ftype == 'bool':
            return [data[i] == ord('T') for i in range(count)]
        if ftype == 'null':
            return [None] * count
        if ftype == 'str':
            enc = field['enc']
            if enc == 'fixed':
                return [data[i*fbytes:(i+1)*fbytes].decode('utf-8', errors='replace').rstrip('\x00') for i in range(count)]
            if enc == 'dict':
                idx_fmt = self.markers[field['index_marker']][1]
                return [field['dict'][struct.unpack(idx_fmt, data[i*fbytes:(i+1)*fbytes])[0]] for i in range(count)]
            if enc == 'offset':
                results = []
                for i in range(count):
                    idx = struct.unpack(field['index_fmt'], data[i*fbytes:(i+1)*fbytes])[0]
                    results.append(field['strbuf'][field['offsets'][idx]:field['offsets'][idx+1]])
                return results
        if ftype == 'array':
            results = []
            for i in range(count):
                arr, pos = [], 0
                for elem in field['elems']:
                    elem_data = data[i*fbytes+pos:i*fbytes+pos+elem['bytes']]
                    if elem['type'] == 'fixed':
                        arr.append(struct.unpack(elem['fmt'], elem_data)[0])
                    else:
                        arr.append(elem_data[0] == ord('T'))
                    pos += elem['bytes']
                results.append(arr)
            return results
        if ftype == 'struct':
            return [self.decode_struct(field['schema'], data[i*fbytes:(i+1)*fbytes]) for i in range(count)]
        return [None] * count

    def decode_field(self, field, data, idx):
        ftype = field['type']
        if ftype == 'fixed': return struct.unpack(field['fmt'], data)[0]
        if ftype == 'bool': return data[0] == ord('T')
        if ftype == 'null': return None
        if ftype == 'str':
            enc = field['enc']
            if enc == 'fixed': return data.decode('utf-8', errors='replace').rstrip('\x00')
            if enc == 'dict': return field['dict'][struct.unpack(self.markers[field['index_marker']][1], data)[0]]
            if enc == 'offset':
                idx = struct.unpack(field['index_fmt'], data)[0]
                return field['strbuf'][field['offsets'][idx]:field['offsets'][idx+1]]
        if ftype == 'array':
            arr, pos = [], 0
            for elem in field['elems']:
                if elem['type'] == 'fixed':
                    arr.append(struct.unpack(elem['fmt'], data[pos:pos+elem['bytes']])[0])
                else:
                    arr.append(data[pos] == ord('T'))
                pos += elem['bytes']
            return arr
        if ftype == 'struct': return self.decode_struct(field['schema'], data)
        return None

    def decode_struct(self, schema, data):
        result, pos = OrderedDict(), 0
        for field in schema:
            result[field['name']] = self.decode_field(field, data[pos:pos+field['bytes']], 0)
            pos += field['bytes']
        return result


def format_value(value, max_data=100, max_str=200, indent=0):
    prefix = "  " * indent
    if value is None: return "null"
    if isinstance(value, bool): return "true" if value else "false"
    if isinstance(value, str):
        if value.startswith("<") and "..." in value: return value
        displayed = value if len(value) <= max_str else value[:max_str//2] + "..." + value[-max_str//2:]
        return f'"{displayed}"'
    if isinstance(value, (int, float)): return repr(value)
    if isinstance(value, list):
        if not value: return "[]"
        if len(value) > max_data: return f"<array[{len(value)}]: {value[:4]}...>"
        if len(value) <= 10 and all(isinstance(x, (int, float, bool, str)) and (not isinstance(x, str) or len(x) < 20) for x in value):
            short = "[" + ", ".join(format_value(x, max_data, max_str) for x in value) + "]"
            if len(short) < 80: return short
        return "[\n" + ",\n".join(prefix + "  " + format_value(x, max_data, max_str, indent+1) for x in value) + "\n" + prefix + "]"
    if isinstance(value, dict):
        if not value: return "{}"
        if "_SOA_" in value:
            records = value["_records_"]
            header = f"<SOA {value['_SOA_']} dims={value['_dims_']}>"
            if len(records) > max_data:
                return header + " [\n" + ",\n".join(prefix + "  " + format_value(r, max_data, max_str, indent+1) for r in records[:4]) + f",\n{prefix}  ...({len(records)-4} more)\n{prefix}]"
            return header + " [\n" + ",\n".join(prefix + "  " + format_value(r, max_data, max_str, indent+1) for r in records) + "\n" + prefix + "]"
        if len(value) > max_data: return f"<object[{len(value)}]>"
        return "{\n" + ",\n".join(prefix + f'  "{k}": ' + format_value(v, max_data, max_str, indent+1) for k, v in value.items()) + "\n" + prefix + "}"
    return str(value)


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 njv.py <file> [--max-data N] [--max-str N] [--debug] [--big-endian]")
        sys.exit(1)
    filename, max_data, max_str = sys.argv[1], 100, 200
    debug = "--debug" in sys.argv
    big_endian = "--big-endian" in sys.argv or "--be" in sys.argv
    for i, arg in enumerate(sys.argv):
        if arg == "--max-data": max_data = int(sys.argv[i+1])
        if arg == "--max-str": max_str = int(sys.argv[i+1])
    with open(filename, "rb") as f: data = f.read()
    print(f"# File: {filename} ({len(data)} bytes)\n")
    # Try JSON first
    if len(data) >= 2 and chr(data[0]) in '{[' and chr(data[1]) in ' \t\n\r"0123456789-[{':
        try:
            print(format_value(json.loads(data.decode('utf-8'), object_pairs_hook=OrderedDict), max_data, max_str))
            return
        except: pass
    # Parse as BJData
    reader = BJDataReader(data, max_data, max_str, debug, big_endian)
    try:
        print(format_value(reader.read_value(), max_data, max_str))
        if reader.remaining() > 0: print(f"\n# {reader.remaining()} bytes remaining")
    except Exception as e:
        print(f"Error at {reader.pos}: {e}")
        if debug: import traceback; traceback.print_exc()
        start, end = max(0, reader.pos-32), min(len(data), reader.pos+64)
        print(f"\nHex [{start}:{end}]:")
        for i in range(start, end, 16):
            chunk = data[i:min(i+16, end)]
            print(f"  {i:04d}: {chunk.hex()}  {''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)}")

if __name__ == "__main__": main()