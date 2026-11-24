"""

"""
import json
import struct
from pathlib import Path

import numpy as np

from src.geometry.mesh import TriMesh


def write_stl(mesh: TriMesh, path, name: str = 'psr') -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    normals = mesh.face_normals.astype('<f4')
    tris = mesh.triangles.astype('<f4')
    record = np.zeros(len(mesh.faces), dtype=[('n', '<f4', 3), ('v', '<f4', (3, 3)), ('attr', '<u2')])
    record['n'], record['v'] = normals, tris
    header = name.encode('ascii', 'replace')[:80].ljust(80, b' ')
    with open(path, 'wb') as fh:
        fh.write(header)
        fh.write(struct.pack('<I', len(mesh.faces)))
        fh.write(record.tobytes())
    return path


def read_stl_triangle_count(path) -> int:
    with open(path, 'rb') as fh:
        fh.seek(80)
        return struct.unpack('<I', fh.read(4))[0]


def _pad(data: bytes, fill: bytes) -> bytes:
    return data + fill * ((4 - len(data) % 4) % 4)


def write_glb(mesh: TriMesh, path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    positions = mesh.vertices.astype('<f4')
    indices = mesh.faces.astype('<u4').reshape(-1)
    pos_bytes, idx_bytes = positions.tobytes(), indices.tobytes()
    pos_len = len(pos_bytes)
    binary = _pad(pos_bytes + idx_bytes, b'\x00')
    lo = positions.min(axis=0).tolist() if len(positions) else [0, 0, 0]
    hi = positions.max(axis=0).tolist() if len(positions) else [0, 0, 0]
    gltf = {
        'asset': {'version': '2.0', 'generator': 'psr-backend'},
        'scene': 0,
        'scenes': [{'nodes': [0]}],
        'nodes': [{'mesh': 0}],
        'meshes': [{'primitives': [{'attributes': {'POSITION': 0}, 'indices': 1}]}],
        'buffers': [{'byteLength': len(binary)}],
        'bufferViews': [
            {'buffer': 0, 'byteOffset': 0, 'byteLength': pos_len, 'target': 34962},
            {'buffer': 0, 'byteOffset': pos_len, 'byteLength': len(idx_bytes), 'target': 34963},
        ],
        'accessors': [
            {'bufferView': 0, 'componentType': 5126, 'count': len(positions), 'type': 'VEC3',
             'min': lo, 'max': hi},
            {'bufferView': 1, 'componentType': 5125, 'count': len(indices), 'type': 'SCALAR'},
        ],
    }
    json_bytes = _pad(json.dumps(gltf, separators=(',', ':')).encode('utf-8'), b' ')
    total = 12 + 8 + len(json_bytes) + 8 + len(binary)
    with open(path, 'wb') as fh:
        fh.write(struct.pack('<4sII', b'glTF', 2, total))
        fh.write(struct.pack('<I4s', len(json_bytes), b'JSON'))
        fh.write(json_bytes)
        fh.write(struct.pack('<I4s', len(binary), b'BIN\x00'))
        fh.write(binary)
    return path


def read_glb(path) -> TriMesh:
    data = Path(path).read_bytes()
    magic, version, total = struct.unpack_from('<4sII', data, 0)
    if magic != b'glTF' or version != 2 or total != len(data):
        raise ValueError(f'{path} is not a valid GLB file')
    json_len, _ = struct.unpack_from('<I4s', data, 12)
    gltf = json.loads(data[20:20 + json_len])
    bin_start = 20 + json_len + 8
    views, accessors = gltf['bufferViews'], gltf['accessors']
    pos_view, idx_view = views[accessors[0]['bufferView']], views[accessors[1]['bufferView']]
    pos = np.frombuffer(data, '<f4', accessors[0]['count'] * 3, bin_start + pos_view['byteOffset'])
    idx = np.frombuffer(data, '<u4', accessors[1]['count'], bin_start + idx_view['byteOffset'])
    return TriMesh(pos.reshape(-1, 3), idx.reshape(-1, 3))