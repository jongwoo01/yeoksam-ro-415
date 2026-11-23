// The stick, camera, and jump button each own their pointer.
export function bindTouchControls(canvas, menu, {turn, jump, interrupt, tap}){
  const stick=document.querySelector('#stick'), knob=stick.firstElementChild;
  const movement={forward:0,right:0};
  let stickId=null,lookId=null,originX=0,originY=0,radius=1,lastX=0,lastY=0;
  let startX=0,startY=0,started=0,dragging=false;
  const enabled=()=>document.body.dataset.view==='walking'&&!menu.open;
  function updateStick(e){
    const x=(e.clientX-originX)/radius,y=(e.clientY-originY)/radius;
    const length=Math.hypot(x,y),scale=1/Math.max(1,length);
    movement.right=length>.12?x*scale:0;
    movement.forward=length>.12?-y*scale:0;
    knob.style.transform='translate('+x*scale*radius+'px,'+y*scale*radius+'px)';
    if(length>.12)interrupt();
  }
  function releaseStick(){
    stickId=null;movement.right=movement.forward=0;knob.style.transform='';
  }
  function reset(){releaseStick();lookId=null;}
  stick.onpointerdown=e=>{
    if(stickId!==null||!enabled())return;
    const box=stick.getBoundingClientRect();
    originX=box.x+box.width/2;originY=box.y+box.height/2;radius=box.width*.32;
    stickId=e.pointerId;stick.setPointerCapture(stickId);updateStick(e);
  };
  stick.onpointermove=e=>{if(e.pointerId===stickId)updateStick(e);};
  stick.onlostpointercapture=stick.onpointercancel=stick.onpointerup=e=>{if(e.pointerId===stickId)releaseStick();};
  canvas.addEventListener('pointerdown',e=>{
    if(e.pointerType==='mouse'||lookId!==null||!enabled())return;
    startX=lastX=e.clientX;startY=lastY=e.clientY;started=e.timeStamp;dragging=false;lookId=e.pointerId;canvas.setPointerCapture(lookId);
  });
  canvas.addEventListener('pointermove',e=>{
    if(e.pointerId!==lookId||!enabled())return;
    if(!dragging){
      if(Math.hypot(e.clientX-startX,e.clientY-startY)<9)return;
      dragging=true;interrupt();
    }
    turn(e.clientX-lastX,e.clientY-lastY);lastX=e.clientX;lastY=e.clientY;
  });
  canvas.addEventListener('pointerup',e=>{
    if(e.pointerId===lookId&&enabled()&&!dragging&&stickId===null&&e.timeStamp-started<390&&Math.hypot(e.clientX-startX,e.clientY-startY)<9)tap(e.clientX,e.clientY);
  });
  for(const event of ['pointerup','pointercancel','lostpointercapture'])
    canvas.addEventListener(event,e=>{if(e.pointerId===lookId)lookId=null;});
  const jumpButton=document.querySelector('#jump');
  jumpButton.onpointerdown=e=>{if(enabled()){e.preventDefault();interrupt();jump();}};
  jumpButton.onclick=e=>{if(e.detail===0&&enabled()){interrupt();jump();}};
  menu.addEventListener('pausewalk',reset);
  addEventListener('blur',reset);addEventListener('resize',reset);
  document.addEventListener('visibilitychange',reset);
  return movement;
}
