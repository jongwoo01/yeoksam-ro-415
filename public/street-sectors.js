import {Box3, Frustum, Matrix4, Vector3} from 'three';

// A single draw per material keeps the CPU cost low. Trim the invisible leading
// and trailing sectors, then restore the full index range for picking and shadows.
export function cullStreetSectors(city) {
  city.updateWorldMatrix(true,true);
  const frustum=new Frustum(), projection=new Matrix4();
  let previousFrame=-1, previousCamera=null;
  city.traverse(object=>{
    const sectors=object.userData.streetSectors;
    if(!object.isMesh || !sectors) return;
    const ranges=sectors.map(([end,x0,y0,z0,x1,y1,z1])=>({
      end, box:new Box3(new Vector3(x0,y0,z0),new Vector3(x1,y1,z1))
        .expandByScalar(.08).applyMatrix4(object.matrixWorld)
    }));
    object.onBeforeRender=(renderer,scene,camera,geometry)=>{
      const frame=renderer.info.render.frame;
      if(previousFrame!==frame || previousCamera!==camera){
        projection.multiplyMatrices(camera.projectionMatrix,camera.matrixWorldInverse);
        frustum.setFromProjectionMatrix(projection);
        previousFrame=frame; previousCamera=camera;
      }
      let first=0,last=ranges.length-1;
      while(first<=last && !frustum.intersectsBox(ranges[first].box))first++;
      while(last>=first && !frustum.intersectsBox(ranges[last].box))last--;
      const start=first ? ranges[first-1].end : 0;
      geometry.setDrawRange(start,last<first ? 0 : ranges[last].end-start);
    };
    object.onAfterRender=(_renderer,_scene,_camera,geometry)=>geometry.setDrawRange(0,Infinity);
  });
}
