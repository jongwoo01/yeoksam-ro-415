import * as T from 'three';
import {createStreetRouter} from './street-route.js';
import {GLTFLoader} from './lib/GLTFLoader.js';

const jogSpeed=6, sprintSpeed=10;
const movementKeys=new Set(['KeyW','KeyA','KeyS','KeyD','ArrowUp','ArrowDown','ArrowLeft','ArrowRight','ShiftLeft','ShiftRight','Space']);


export async function createWalker(scene,camera,boxes,canvas,walkways){
  function floorAt(x,z){
    const y=-z;
    for(const [start,end,left,right,nextLeft,nextRight] of walkways){
      if(y<start||y>end)continue;
      const t=(y-start)/(end-start);
      if(x>=left+(nextLeft-left)*t && x<=right+(nextRight-right)*t)return .146;
    }
    return 0;
  }
  const player=new T.Group();scene.add(player);
  const loader=new GLTFLoader();
  const motion=await fetch('./knit-motion.json?v=3').then(response=>response.json());
  const clips=motion.map(({name,duration,times,tracks})=>new T.AnimationClip(name,duration,
    Object.entries(tracks).map(([path,values])=>path.endsWith('.quaternion')
      ?new T.QuaternionKeyframeTrack(path,times,values):new T.VectorKeyframeTrack(path,times,values))));
  const variants=await Promise.all(['man','woman'].map(async id=>{
    const {scene:model}=await loader.loadAsync('./knit-'+id+'.glb?v=4');
    model.visible=false;player.add(model);
    model.traverse(obj=>{if(obj.isMesh)obj.receiveShadow=true;});
    const mixer=new T.AnimationMixer(model);
    const actions=Object.fromEntries(clips.map(clip=>[clip.name,mixer.clipAction(clip)]));
    return {id,model,mixer,actions};
  }));
  const selector=document.querySelector('#avatar');
  try{if(localStorage.getItem('hanq-avatar')==='woman')selector.value='woman';}catch{}
  let active,playing;
  function selectAvatar(){
    const selected=variants.find(choice=>choice.id===selector.value);
    for(const choice of variants)choice.model.visible=choice===selected;
    if(active===selected)return;
    const time=playing?active.actions[playing].time:0;
    active=selected;active.mixer.stopAllAction();
    if(playing){const action=active.actions[playing];action.reset().play();action.time=time;active.mixer.update(0);}
  }
  selectAvatar();
  selector.addEventListener('change',()=>{
    selectAvatar();
    try{localStorage.setItem('hanq-avatar',selector.value);}catch{}
  });
  function animate(dt,moving,sprint,grounded,forward){
    const name=!grounded?'Jump_Loop':!moving?'Idle_Loop':sprint?'Sprint_Loop':'Jog_Fwd_Loop';
    const action=active.actions[name];
    if(name!==playing){
      const previous=active.actions[playing];
      action.reset().play();
      if(previous){
        if(moving&&grounded&&(playing==='Jog_Fwd_Loop'||playing==='Sprint_Loop')){
          action.time=(previous.time/previous.getClip().duration)*action.getClip().duration;
        }
        action.crossFadeFrom(previous,.16,false);
      }
      playing=name;
    }
    action.timeScale=grounded&&moving&&forward<0?-.95:1;
    active.mixer.update(dt);
  }
  // The city uses a static shadow map. A small moving contact shadow follows the feet.
  const patch=document.createElement('canvas');patch.width=patch.height=64;
  const ctx=patch.getContext('2d'),fade=ctx.createRadialGradient(32,32,1,32,32,31);
  fade.addColorStop(0,'rgba(0,0,0,.80)');fade.addColorStop(.42,'rgba(0,0,0,.42)');fade.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=fade;ctx.fillRect(0,0,64,64);
  const shadow=new T.Mesh(new T.PlaneGeometry(1.1,.75),new T.MeshBasicMaterial({map:new T.CanvasTexture(patch),transparent:true,depthWrite:false}));
  shadow.rotation.x=-Math.PI/2;scene.add(shadow);
  const keys=new Set(),pos=player.position, target=new T.Vector3(), offset=new T.Vector3();
  const defaultElevation=.52, defaultDistance=7.2;
  let yaw=0,elevation=defaultElevation,distance=defaultDistance,arm=defaultDistance,vertical=0,grounded=true;
  let desiredYaw=yaw,desiredElevation=elevation,pivotY=0;
  let looking=true;
  const overlaps=(x,z,margin,[l,r,b,t])=>x>l-margin&&x<r+margin&&z>b-margin&&z<t+margin;
  const isObstacle=(x,z,margin,height)=>boxes.some(box=>height<(box[4]??Infinity)&&overlaps(x,z,margin,box));
  function supportAt(x,z,height){
    let floor=floorAt(x,z);
    for(const box of boxes){
      if(box[4]!==undefined&&box[4]<=height+.0001&&overlaps(x,z,.25,box))floor=Math.max(floor,box[4]);
    }
    return floor;
  }
  // Only nearby footprints can shorten the camera arm. Filter once per frame.
  let nearby=[];
  const free=(x,z)=>Math.hypot(x,z+17.5)<=40&&!isObstacle(x,z,.25,pos.y);
  function follow(dt,snap=false){
    const desiredY=pos.y+1.28;
    pivotY=snap?desiredY:T.MathUtils.damp(pivotY,desiredY,14,dt);
    target.set(pos.x,pivotY,pos.z);
    offset.set(Math.sin(yaw)*Math.cos(elevation),Math.sin(elevation),Math.cos(yaw)*Math.cos(elevation));
    nearby=boxes.filter(([l,r,b,t])=>target.x+distance+.12>=l&&target.x-distance-.12<=r&&target.z+distance+.12>=b&&target.z-distance-.12<=t);
    let available=distance;
    for(let d=.12;d<=distance;d+=.10){
      const z=target.z+offset.z*d;
      if(nearby.some(box=>target.y+offset.y*d-.12<(box[4]??Infinity)&&overlaps(target.x+offset.x*d,z,.12,box))||target.y+offset.y*d<floorAt(target.x+offset.x*d,z)+.18){
        available=Math.max(.09,d-.12);break;
      }
    }
    // Never ease through a wall. Ease user zoom and recovery in both directions.
    arm=snap?available:Math.min(available<distance-.001?available:Infinity,T.MathUtils.damp(arm,available,10,dt));
    camera.position.copy(target).addScaledVector(offset,arm);
    // Keep the high chase position but frame the next few metres of pavement as well.
    target.x-=Math.sin(yaw)*2.3;
    target.z-=Math.cos(yaw)*2.3;
    target.y+=.65;
    // Keep the pitch when the camera arm retracts at a wall or curb.
    target.addScaledVector(offset,arm-distance);
    camera.lookAt(target);
  }
  function place(x,z,angle){
    keys.clear();vertical=0;grounded=true;yaw=angle;elevation=defaultElevation;distance=defaultDistance;
    desiredYaw=yaw;desiredElevation=elevation;
    pos.set(x,floorAt(x,z),z);player.rotation.y=yaw+Math.PI;
    animate(0,false,false,true,0,0);follow(0,true);
  }
  const routeTo=createStreetRouter(boxes);
  let trip=null;
  function travel(x,z,angle){
    const path=routeTo({x:pos.x,y:pos.y,z:pos.z},{x,z});
    if(!path.length)return false;
    keys.clear();trip={path,angle,speed:trip?.speed??0};return true;
  }
  function endTrip(){
    if(trip)canvas.dispatchEvent(new Event('tripend'));
    trip=null;
  }
  const reset=()=>travel(-1,8.1,-.07);
  const detail=()=>travel(-4.7,-5.9,-Math.atan2(5.4,5.9));
  const parking=()=>travel(10.1,-28.7,1.72);
  if(location.hash==='#corner')place(11.46,-2.8,-.12);
  else place(-1,8.1,-.07);
  canvas.addEventListener('wheel',e=>{
    if(document.body.dataset.view!=='walking')return;
    e.preventDefault();
    const pixels=e.deltaY*(e.deltaMode===1?16:e.deltaMode===2?canvas.clientHeight:1);
    distance=T.MathUtils.clamp(distance*Math.exp(T.MathUtils.clamp(pixels*.0012,-.35,.35)),3,10);
  },{passive:false});
  function setLook(enabled){
    looking=enabled;
    if(!enabled){desiredYaw=yaw;desiredElevation=elevation;}
    canvas.dispatchEvent(new CustomEvent('lookchange',{detail:enabled}));
  }
  setLook(true);
  function captureMouse(){
    if(!document.pointerLockElement)canvas.requestPointerLock?.()?.catch?.(()=>{});
  }
  canvas.addEventListener('click',()=>{
    if(document.body.dataset.view!=='walking')return;
    setLook(true);captureMouse();
  });
  document.addEventListener('pointerlockchange',()=>setLook(document.pointerLockElement===canvas));
  addEventListener('keydown',e=>{
    if(e.code==='Escape'){
      if(document.pointerLockElement===canvas)document.exitPointerLock();
      setLook(false);
    }
  });
  addEventListener('blur',()=>setLook(false));
  let turned=false;
  document.addEventListener('mousemove',e=>{
    if(document.body.dataset.view!=='walking'||!looking||(e.target!==canvas&&document.pointerLockElement!==canvas))return;
    if(!turned&&(e.movementX||e.movementY)){turned=true;canvas.dispatchEvent(new Event("firstlook"));}
    desiredYaw-=e.movementX*.0025;
    desiredElevation=T.MathUtils.clamp(desiredElevation+e.movementY*.0020,-.15,1.04);
  });
  addEventListener('keydown',e=>{
    if(e.target===selector||(e.target.closest?.('button')&&e.code==='Space')||document.body.dataset.view!=='walking'||!movementKeys.has(e.code)||e.metaKey||e.ctrlKey||e.altKey)return;
    e.preventDefault();
    endTrip();
    if(looking&&!e.repeat&&e.isTrusted)captureMouse();
    keys.add(e.code);
    if(e.code==='Space'&&!e.repeat&&grounded){vertical=8.1;grounded=false;}
  });
  addEventListener('keyup',e=>keys.delete(e.code));
  addEventListener('blur',()=>keys.clear());
  document.addEventListener('pointerlockchange',()=>{if(!document.pointerLockElement)keys.clear();});
  const down=(a,b)=>Number(keys.has(a)||keys.has(b));
  let hasWalked=false;
  function step(dt){
    let routeSpeed=0,routeX=0,routeZ=0;
    if(trip){
      const next=trip.path[0],gap=next?Math.hypot(next.x-pos.x,next.z-pos.z):0;
      if(next&&gap>.001){
        trip.speed=Math.min(trip.speed+dt*12,7.3);
        const after=trip.path[1];
        let cornerSpeed=0;
        if(after){
          const ax=after.x-next.x,az=after.z-next.z;
          const cosine=((next.x-pos.x)*ax+(next.z-pos.z)*az)/(gap*Math.hypot(ax,az));
          cornerSpeed=2+5*Math.max(0,cosine);
        }
        routeSpeed=Math.min(trip.speed,Math.sqrt(cornerSpeed**2+14*gap),gap/dt);
        trip.speed=routeSpeed;
        routeX=(next.x-pos.x)/gap;routeZ=(next.z-pos.z)/gap;
        const heading=Math.atan2(-routeX,-routeZ);
        const toward=(trip.path.length===1?Math.min(1,gap/4):1);
        const delta=(a,b)=>Math.atan2(Math.sin(a-b),Math.cos(a-b));
        desiredYaw=yaw+delta(trip.angle+delta(heading,trip.angle)*toward,yaw);
      }else if(next){trip.path.shift();}
      else{
        desiredYaw=yaw+Math.atan2(Math.sin(trip.angle-yaw),Math.cos(trip.angle-yaw));
        if(Math.abs(desiredYaw-yaw)<.006)endTrip();
      }
      desiredElevation=defaultElevation;
    }
    yaw=T.MathUtils.damp(yaw,desiredYaw,trip?3.8:36,dt);
    elevation=T.MathUtils.damp(elevation,desiredElevation,32,dt);
    const f=down('KeyW','ArrowUp')-down('KeyS','ArrowDown'),r=down('KeyD','ArrowRight')-down('KeyA','ArrowLeft');
    const sprint=keys.has('ShiftLeft')||keys.has('ShiftRight');
    const stride=(sprint?sprintSpeed:jogSpeed)*dt/Math.max(1,Math.hypot(f,r));
    const dx=trip?routeX*routeSpeed*dt:(r*Math.cos(yaw)-f*Math.sin(yaw))*stride,dz=trip?routeZ*routeSpeed*dt:(-r*Math.sin(yaw)-f*Math.cos(yaw))*stride;
    const prevX=pos.x,prevZ=pos.z;
    if(trip){
      // The router checked this segment as a line, including corner clearance.
      pos.x+=dx;pos.z+=dz;
    }else{
      if(free(pos.x+dx,pos.z))pos.x+=dx;
      if(free(pos.x,pos.z+dz))pos.z+=dz;
    }
    const moving=Math.hypot(pos.x-prevX,pos.z-prevZ)>.0001;
    if(moving&&!trip&&!hasWalked){hasWalked=true;canvas.dispatchEvent(new Event("firstwalk"));}
    const facing=trip&&moving?Math.atan2(dx,dz):yaw+Math.PI;
    const angle=facing-player.rotation.y;
    player.rotation.y+=Math.atan2(Math.sin(angle),Math.cos(angle))*(1-Math.exp(-20*dt));
    const floor=supportAt(pos.x,pos.z,pos.y);
    if(grounded&&pos.y>floor+.16)grounded=false;
    if(!grounded){vertical-=18*dt;pos.y+=vertical*dt;grounded=pos.y<=floor&&vertical<=0;}
    if(grounded){pos.y=floor;vertical=0;}
    animate(dt,moving,sprint||routeSpeed>6,grounded,f);
  }
  return {reset,detail,parking,update(elapsed){
    let remaining=Math.min(elapsed,.15);
    while(remaining>.00001){const dt=Math.min(remaining,1/60);step(dt);remaining-=dt;}
    const floor=supportAt(pos.x,pos.z,pos.y),height=Math.max(0,pos.y-floor);
    shadow.position.set(pos.x+.06,floor+.024,pos.z+.025);
    shadow.scale.setScalar(1+height*.3);shadow.material.opacity=.83/(1+height*2);
    follow(elapsed);
  }};
}
