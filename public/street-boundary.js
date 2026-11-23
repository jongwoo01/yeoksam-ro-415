import * as T from 'three';

export const radius=40,centerZ=-17.5;
export const distanceFromCenter=(x,z)=>Math.hypot(x,z-centerZ);

// Two mirrored pentagons per cell. Neighbouring cells rotate one quarter turn.
function makePanelTexture(){
  const tile=document.createElement('canvas');tile.width=tile.height=512;
  const ctx=tile.getContext('2d');
  ctx.fillStyle='black';ctx.fillRect(0,0,512,512);
  ctx.scale(256,256);ctx.beginPath();ctx.lineJoin='round';
  const corners=[[0,1],[-1/6,.5],[0,0],[.5,1/6],[.5,5/6]];
  for(let row=-1;row<=2;row++)for(let col=-1;col<=2;col++){
    for(const mirror of [false,true]){
      for(let i=0;i<corners.length;i++){
        let [x,y]=corners[i];if(mirror)x=1-x;
        if((row+col)%2)[x,y]=[1-y,x];
        if(i===0)ctx.moveTo(col+x,row+y);else ctx.lineTo(col+x,row+y);
      }
      ctx.closePath();
    }
  }
  ctx.strokeStyle='#444';ctx.lineWidth=.040;ctx.stroke();
  ctx.strokeStyle='white';ctx.lineWidth=.014;ctx.stroke();
  const texture=new T.CanvasTexture(tile);
  texture.wrapS=texture.wrapT=T.RepeatWrapping;
  return texture;
}

export function createBoundary(scene,player,reducedMotion){
  const material=new T.ShaderMaterial({
    transparent:true,depthWrite:false,side:T.DoubleSide,forceSinglePass:true,
    uniforms:{panels:{value:makePanelTexture()},playerXZ:{value:new T.Vector2()},time:{value:0}},
    vertexShader:`varying vec3 world;varying vec2 panelUV;
      void main(){panelUV=uv*vec2(80.,20.);world=(modelMatrix*vec4(position,1.)).xyz;
      gl_Position=projectionMatrix*viewMatrix*vec4(world,1.);}`,
    fragmentShader:`varying vec3 world;varying vec2 panelUV;uniform vec2 playerXZ;uniform float time;uniform sampler2D panels;
      void main(){
        vec2 radial=normalize(world.xz-vec2(0.,${centerZ}));
        vec2 outward=normalize(playerXZ-vec2(0.,${centerZ}));
        float arc=${radius.toFixed(1)}*atan(radial.x*outward.y-radial.y*outward.x,dot(radial,outward));
        float edgeDistance=${radius.toFixed(1)}-length(playerXZ-vec2(0.,${centerZ}));
        float reveal=1.-smoothstep(1.,10.,edgeDistance);
        vec3 eye=normalize(cameraPosition-world);
        float grazing=pow(1.-abs(dot(radial,eye.xz)),1.7);
        float outline=texture2D(panels,panelUV).r;
        float seam=smoothstep(.16,.85,outline);
        float halo=smoothstep(.025,.35,outline);
        float local=1.-smoothstep(5.,23.,length(vec2(arc,world.y*.7)));
        float energy=pow(.5+.5*cos(length(vec2(arc,world.y-1.2))*1.08-time*1.8),6.);
        float charge=local*(.50+.50*energy);
        vec3 film=mix(vec3(.12,.23,.30),vec3(.41,.79,.86),halo);
        film=mix(film,vec3(.77,.96,1.),seam*charge);
        float alpha=reveal*(.055+.055*grazing+local*.065+
          charge*(.60*seam+.20*halo));
        gl_FragColor=vec4(film,alpha);
        #include <colorspace_fragment>
      }`
  });
  const wall=new T.Mesh(new T.CylinderGeometry(radius,radius,64,192,1,true),material);
  wall.position.set(0,32,centerZ);wall.visible=false;scene.add(wall);
  return time=>{
    wall.visible=radius-distanceFromCenter(player.x,player.z)<10;
    if(!wall.visible)return;
    material.uniforms.playerXZ.value.set(player.x,player.z);
    material.uniforms.time.value=reducedMotion.matches?0:time;
  };
}
