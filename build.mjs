// Prepare only the assets used by the web client.
import {cp, mkdir, readFile, writeFile} from 'node:fs/promises';
import {gzipSync} from 'node:zlib';
import {indexStreetSectors} from './source/street-sectors.mjs';
const output='dist';
await mkdir(output,{recursive:true});
const files=['_routes.json','share','index.html','street.js','walker.js','touch-controls.js','street-boundary.js','street-sectors.js','street-route.js','contact-light.js','aerial.webp',
  'street-light.bin.gz','knit-motion.json','knit-man.glb','knit-woman.glb','walkways.json','obstacles.json','camera-volume.bin',
  'lib','utils','making','archive','props/water_manhole_cover'];
for(const file of files)await cp('public/'+file,output+'/'+file,{recursive:true});
const model=await readFile('public/street.glb');
await writeFile(output+'/street.glb.gz',gzipSync(indexStreetSectors(model),{level:9}));
const entry=await readFile(output+'/street.js','utf8');
await writeFile(output+'/street.js',entry.replace('./street.glb?v=cars-6', './street.glb.gz'));
