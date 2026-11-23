"""Build the optional lightweight street from the standard web export."""
from pathlib import Path
import json
import struct
import tempfile

import bpy

public = Path(__file__).resolve().parents[1] / "public"
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(public / "street.glb"))
for obj in bpy.context.scene.objects:
    if obj.type != "MESH" or len(obj.data.polygons) < 600:
        continue
    modifier = obj.modifiers.new("Low detail", "DECIMATE")
    modifier.ratio = 0.34
# Resizing and packing in Blender can silently turn source JPEGs into large PNGs.
with (public / "street.glb").open("rb") as source:
    source.seek(12)
    json_size = struct.unpack("<I", source.read(4))[0]
    source.seek(20)
    metadata = json.loads(source.read(json_size))
jpeg_names = {item["name"] for item in metadata["images"] if item["mimeType"] == "image/jpeg"}
scratch = tempfile.TemporaryDirectory()
for image in list(bpy.data.images):
    width, height = image.size
    if max(width, height) > 512:
        scale = 512 / max(width, height)
        image.scale(max(1, round(width * scale)), max(1, round(height * scale)))
        if image.name in jpeg_names:
            image.filepath_raw = str(Path(scratch.name) / (image.name + ".jpg"))
            image.file_format = "JPEG"
            image.save()
            # Reload the resized JPEG as the export source, including its encoded bytes.
            replacement = bpy.data.images.load(image.filepath_raw, check_existing=False)
            replacement.colorspace_settings.name = image.colorspace_settings.name
            image.user_remap(replacement)
        else:
            image.pack()
bpy.ops.export_scene.gltf(filepath=str(public / "street-low.glb"), export_format="GLB",
                          export_apply=True, export_animations=False, export_cameras=False)
