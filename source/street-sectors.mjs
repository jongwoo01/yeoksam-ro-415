// Reorder opaque triangle indices into consecutive street sectors. Vertices,
// materials and triangles remain identical to the Blender export.
export function indexStreetSectors(model) {
  const jsonSize = model.readUInt32LE(12);
  const gltf = JSON.parse(model.toString('utf8', 20, 20 + jsonSize));
  const binary = model.subarray(28 + jsonSize);
  function array(accessor, Type) {
    const view = gltf.bufferViews[accessor.bufferView];
    return new Type(binary.buffer, binary.byteOffset + (view.byteOffset || 0) +
      (accessor.byteOffset || 0), accessor.count * (accessor.type === 'VEC3' ? 3 : 1));
  }
  for (const mesh of gltf.meshes) {
    if (mesh.primitives.length !== 1) continue;
    const primitive = mesh.primitives[0], material = gltf.materials[primitive.material];
    const indices = gltf.accessors[primitive.indices], pos = gltf.accessors[primitive.attributes.POSITION];
    if ((primitive.mode ?? 4) !== 4 || indices.count < 30000 || pos.componentType !== 5126 ||
        gltf.bufferViews[pos.bufferView].byteStride || ![5123,5125].includes(indices.componentType) ||
        (material.alphaMode === 'BLEND' && material.name !== 'canopy')) continue;
    const xyz = array(pos, Float32Array);
    const index = array(indices, indices.componentType === 5125 ? Uint32Array : Uint16Array);
    const cells = new Map();
    const cellWidth = 12; // Assign the triangle by its centroid; retain its complete bounds.
    for (let i = 0; i < index.length; i += 3) {
      const a = 3*index[i], b = 3*index[i+1], c = 3*index[i+2];
      const x = Math.floor((xyz[a]+xyz[b]+xyz[c])/(3*cellWidth));
      const z = Math.floor((xyz[a+2]+xyz[b+2]+xyz[c+2])/(3*cellWidth));
      const key = x + ',' + z;
      let cell = cells.get(key);
      if (!cell) {
        cell = {x,z,indices:[],min:[Infinity,Infinity,Infinity],max:[-Infinity,-Infinity,-Infinity]};
        cells.set(key,cell);
      }
      cell.indices.push(index[i],index[i+1],index[i+2]);
      for (let axis = 0; axis < 3; axis++) {
        cell.min[axis] = Math.min(cell.min[axis],xyz[a+axis],xyz[b+axis],xyz[c+axis]);
        cell.max[axis] = Math.max(cell.max[axis],xyz[a+axis],xyz[b+axis],xyz[c+axis]);
      }
    }
    if (cells.size < 2) continue;
    const sectors = [];
    let start = 0;
    for (const cell of [...cells.values()].sort((a,b)=>a.z-b.z || a.x-b.x)) {
      index.set(cell.indices,start);
      start += cell.indices.length;
      sectors.push([start,...cell.min,...cell.max]);
    }
    mesh.extras = {...mesh.extras, streetSectors:sectors};
  }
  const json = Buffer.from(JSON.stringify(gltf)), padded = Math.ceil(json.length/4)*4;
  const out = Buffer.alloc(28+padded+binary.length,0x20);
  model.copy(out,0,0,20);
  out.writeUInt32LE(out.length,8);
  out.writeUInt32LE(padded,12);
  json.copy(out,20);
  model.copy(out,20+padded,20+jsonSize,28+jsonSize);
  binary.copy(out,28+padded);
  return out;
}
