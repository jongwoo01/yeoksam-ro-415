import {radius,distanceFromCenter} from './street-boundary.js';
import {bindTouchControls} from './touch-controls.js';
import * as T from 'three';
import {createStreetRouter} from './street-route.js';
import {GLTFLoader} from './lib/GLTFLoader.js';

const jogSpeed=6, sprintSpeed=10;
const movementKeys=new Set(['KeyW','KeyA','KeyS','KeyD','ArrowUp','ArrowDown','ArrowLeft','ArrowRight','ShiftLeft','ShiftRight','Space']);


export async function createWalker(scene,camera,boxes,canvas,walkways,city){
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
  const volumePromise=fetch('./camera-volume.bin').then(async response=>{
    if(!response.ok)throw Error('Camera volume unavailable');
    return new Uint8Array(await response.arrayBuffer());
  });
  const motion=await fetch('./knit-motion.json?v=3').then(response=>response.json());
  const clips=motion.map(({name,duration,times,tracks})=>new T.AnimationClip(name,duration,
    Object.entries(tracks).map(([path,values])=>path.endsWith('.quaternion')
      ?new T.QuaternionKeyframeTrack(path,times,values):new T.VectorKeyframeTrack(path,times,values))));
  const selector=document.querySelector('#avatar'), avatarMessage=document.querySelector('#avatarMessage');
  const variants=new Map();
  try{if(localStorage.getItem('hanq-avatar')==='woman')selector.value='woman';}catch{}
  let active,playing;
  async function loadAvatar(id){
    const {scene:model}=await loader.loadAsync('./knit-'+id+'.glb?v=4');
    model.visible=false;player.add(model);
    model.traverse(obj=>{if(obj.isMesh)obj.receiveShadow=true;});
    const mixer=new T.AnimationMixer(model);
    const actions=Object.fromEntries(clips.map(clip=>[clip.name,mixer.clipAction(clip)]));
    return {id,model,mixer,actions};
  }
  async function selectAvatar(){
    const id=selector.value;
    if(!variants.has(id)){
      variants.set(id,loadAvatar(id).catch(error=>{variants.delete(id);throw error;}));
    }
    avatarMessage.textContent=active&&active.id!==id?'캐릭터 불러오는 중…':'';
    let selected;
    try{selected=await variants.get(id);}
    catch(error){
      if(!active)throw error;
      if(selector.value===id){
        selector.value=active.id;
        avatarMessage.textContent='캐릭터를 불러오지 못했어요. 다시 선택해 주세요.';
      }
      return;
    }
    if(selector.value!==id)return;
    avatarMessage.textContent='';
    if(active===selected)return;
    const time=playing?active.actions[playing].time:0;
    if(active)active.model.visible=false;
    active=selected;active.model.visible=true;active.mixer.stopAllAction();
    if(playing){const action=active.actions[playing];action.reset().play();action.time=time;active.mixer.update(0);}
    try{localStorage.setItem('hanq-avatar',id);}catch{}
  }
  await selectAvatar();
  selector.addEventListener('change',selectAvatar);
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
  const volume=await volumePromise;
  function cameraBlocked(x,y,z){
    const i=Math.floor((x+52)*2),j=Math.floor((34-z)*2),k=Math.floor(y*2);
    if(i<0||j<0||k<0||i>=208||j>=208||k>=32)return false;
    const bit=(j*208+i)*32+k;
    return !!(volume[bit>>3]&(1<<(bit&7)));
  }
  // Only nearby footprints can shorten the camera arm. Filter once per frame.
  const lastArmStart=new T.Vector3(),lastArmDirection=new T.Vector3();
  let lastArmLength=-1,available=0;
  const free=(x,z)=>distanceFromCenter(x,z)<=radius&&!isObstacle(x,z,.25,pos.y);
  function follow(dt,snap=false){
    const desiredY=pos.y+1.28;
    pivotY=snap?desiredY:T.MathUtils.damp(pivotY,desiredY,14,dt);
    target.set(pos.x,pivotY,pos.z);
    offset.set(Math.sin(yaw)*Math.cos(elevation),Math.sin(elevation),Math.cos(yaw)*Math.cos(elevation));
    // The obstruction volume and boxes are static. While the character idles
    // the same ray has the same hit distance; keep easing the camera each frame.
    if(lastArmLength!==distance||!target.equals(lastArmStart)||!offset.equals(lastArmDirection)){
      lastArmLength=distance;
      lastArmStart.copy(target);
      lastArmDirection.copy(offset);
      const nearby=boxes.filter(([l,r,b,t])=>target.x+distance+.12>=l&&target.x-distance-.12<=r&&target.z+distance+.12>=b&&target.z-distance-.12<=t);
      available=distance;
      for(let d=.12;d<=distance;d+=.10){
        const x=target.x+offset.x*d,y=target.y+offset.y*d,z=target.z+offset.z*d;
        // Pavement is at most .146 m high. Only sample its footprint near ground level.
        if(cameraBlocked(x,y,z)||nearby.some(box=>y-.12<(box[4]??Infinity)&&overlaps(x,z,.12,box))||(y<.146+.18&&y<floorAt(x,z)+.18)){
          available=Math.max(.09,d-.12);break;
        }
      }
    }
    // Never ease through a wall. Ease user zoom and recovery in both directions.
    arm=snap?available:Math.min(available<distance-.001?available:Infinity,T.MathUtils.damp(arm,available,10,dt));
    player.visible=arm>.62;
    camera.position.copy(target).addScaledVector(offset,arm);
    // Keep the high chase position but frame the next few metres of pavement as well.
    target.x-=Math.sin(yaw)*2.3;
    target.z-=Math.cos(yaw)*2.3;
    target.y+=.65;
    // Keep the pitch when the camera arm retracts at a wall or curb.
    target.addScaledVector(offset,arm-distance);
    camera.lookAt(target);
  }
  const entrance={x:-3.5,z:4.65,angle:-.19};
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
  const reset=()=>travel(entrance.x,entrance.z,entrance.angle);
  const detail=()=>travel(-4.7,-5.9,-Math.atan2(5.4,5.9));
  const parking=()=>travel(10.1,-28.7,1.72);
  if(location.hash==='#corner')place(11.46,-2.8,-.12);
  else place(entrance.x,entrance.z,entrance.angle);
  let zoomActiveUntil=0;
  canvas.addEventListener('wheel',e=>{
    if(document.body.dataset.view!=='walking')return;
    e.preventDefault();
    zoomActiveUntil=performance.now()+650;
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
  canvas.addEventListener('click',e=>{
    if((e.pointerType&&e.pointerType!=='mouse')||e.sourceCapabilities?.firesTouchEvents||(!e.pointerType&&matchMedia('(pointer:coarse)').matches))return;
    if(document.body.dataset.view!=='walking')return;
    setLook(true);captureMouse();
  });
  document.addEventListener('pointerlockchange',()=>setLook(document.pointerLockElement===canvas));
  const menu=document.querySelector('#menu');
  menu.addEventListener('pausewalk',()=>{keys.clear();setLook(false);});
  menu.addEventListener('close',()=>setLook(true));
  addEventListener('blur',()=>setLook(false));
  let turned=false;
  function turn(dx,dy){
    if(!turned&&(dx||dy)){turned=true;canvas.dispatchEvent(new Event('firstlook'));}
    desiredYaw-=dx*.0025;
    desiredElevation=T.MathUtils.clamp(desiredElevation+dy*.002,-.15,1.04);
  }
  function jump(){if(grounded){vertical=8.1;grounded=false;}}
  const picker=new T.Raycaster(),pointer=new T.Vector2();
  const feedback=document.querySelector('#tapMark');
  let feedbackTimer;
  function tap(x,y){
    const rect=canvas.getBoundingClientRect();
    pointer.set(2*(x-rect.left)/rect.width-1,1-2*(y-rect.top)/rect.height);
    picker.setFromCamera(pointer,camera);
    const hit=picker.intersectObject(city,true)[0];
    let accepted=false;
    if(hit){
      const p=hit.point;
      if(Math.abs(p.y-floorAt(p.x,p.z))<.22&&
        distanceFromCenter(p.x,p.z)<radius&&!isObstacle(p.x,p.z,.25,p.y)){
        accepted=travel(p.x,p.z,Math.atan2(pos.x-p.x,pos.z-p.z));
      }
    }
    feedback.style.left=x+'px';feedback.style.top=y+'px';
    feedback.textContent=accepted?'':'×';feedback.hidden=false;
    clearTimeout(feedbackTimer);feedbackTimer=setTimeout(()=>feedback.hidden=true,550);
    if(accepted)canvas.dispatchEvent(new Event('taptrip'));
  }
  const touch=bindTouchControls(canvas,menu,{turn:(x,y)=>turn(x*1.7,y*1.7),tap,jump,interrupt:endTrip});
  document.addEventListener('mousemove',e=>{
    if(e.sourceCapabilities?.firesTouchEvents||document.body.dataset.view!=='walking'||menu.open||!looking||(e.target!==canvas&&document.pointerLockElement!==canvas))return;
    turn(e.movementX,e.movementY);
  });
  addEventListener('keydown',e=>{
    if(menu.open||e.target===selector||(e.target.closest?.('button')&&e.code==='Space')||document.body.dataset.view!=='walking'||!movementKeys.has(e.code)||e.metaKey||e.ctrlKey||e.altKey)return;
    e.preventDefault();
    endTrip();
    if(looking&&!e.repeat&&e.isTrusted)captureMouse();
    keys.add(e.code);
    if(e.code==='Space'&&!e.repeat)jump();
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
    const f=touch.forward+down('KeyW','ArrowUp')-down('KeyS','ArrowDown'),r=touch.right+down('KeyD','ArrowRight')-down('KeyA','ArrowLeft');
    const sprint=Math.hypot(touch.forward,touch.right)>.94||keys.has('ShiftLeft')||keys.has('ShiftRight');
    const stride=(sprint?sprintSpeed:jogSpeed)*dt/Math.max(1,Math.hypot(f,r));
    const dx=trip?routeX*routeSpeed*dt:(r*Math.cos(yaw)-f*Math.sin(yaw))*stride,dz=trip?routeZ*routeSpeed*dt:(-r*Math.sin(yaw)-f*Math.cos(yaw))*stride;
    const prevX=pos.x,prevZ=pos.z;
    if(trip){
      // The router checked this segment as a line, including corner clearance.
      pos.x+=dx;pos.z+=dz;
    }else{
      if(dx&&free(pos.x+dx,pos.z))pos.x+=dx;
      if(dz&&free(pos.x,pos.z+dz))pos.z+=dz;
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
  function isActive(now){
    return !!(trip||!grounded||keys.size||touch.forward||touch.right||now<zoomActiveUntil||
      Math.abs(yaw-desiredYaw)>.0001||Math.abs(elevation-desiredElevation)>.0001);
  }
  return {position:pos,reset,detail,parking,isActive,update(elapsed){
    let remaining=Math.min(elapsed,.15);
    while(remaining>.00001){const dt=Math.min(remaining,1/60);step(dt);remaining-=dt;}
    const floor=supportAt(pos.x,pos.z,pos.y),height=Math.max(0,pos.y-floor);
    shadow.position.set(pos.x+.06,floor+.024,pos.z+.025);
    shadow.scale.setScalar(1+height*.3);shadow.material.opacity=.83/(1+height*2);
    follow(elapsed);
  }};
}
