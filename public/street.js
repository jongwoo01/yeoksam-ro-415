import * as T from 'three';
import {GLTFLoader} from './lib/GLTFLoader.js';

import {createContactPass} from './contact-light.js';
import {createWalker} from './walker.js?v=walk4';

const status=document.querySelector('#status');
async function loadStreet(progress){
  const file='./street.glb?v=cars-6';
  const bytes=await new T.FileLoader().setResponseType('arraybuffer').loadAsync(file,event=>{
    if(event.total)progress.value=Math.min(75,75*event.loaded/event.total);
  });
  const header=new Uint8Array(bytes,0,2);
  const data=header[0]===31&&header[1]===139
    ?await new Response(new Blob([bytes]).stream().pipeThrough(new DecompressionStream('gzip'))).arrayBuffer()
    :bytes;
  return new GLTFLoader().parseAsync(data,'./');
}
export async function main(){
  const progress=document.querySelector("progress");
  const label=document.querySelector("#loadLabel");
  const renderer=new T.WebGLRenderer({antialias:true,powerPreference:'high-performance'});
  renderer.setPixelRatio(Math.min(devicePixelRatio,1.25));
  renderer.setSize(innerWidth,innerHeight);
  renderer.shadowMap.enabled=true;
  renderer.shadowMap.type=T.PCFSoftShadowMap;
  renderer.toneMapping=T.ACESFilmicToneMapping;
  renderer.toneMappingExposure=1.03;
  document.body.prepend(renderer.domElement);
  const scene=new T.Scene(), camera=new T.PerspectiveCamera(62,innerWidth/innerHeight,.08,230);
  scene.fog=new T.FogExp2(0xc8d5db,.009);
  const clock=new T.Clock();
  const light=new T.DirectionalLight(0xfff0d9,2.15);
  light.position.set(-24,42,24);light.castShadow=true;
  Object.assign(light.shadow.camera,{left:-47,right:47,top:38,bottom:-40,near:.1,far:125});
  light.shadow.mapSize.set(2048,2048);light.shadow.normalBias=.018;
  scene.add(light,new T.HemisphereLight(0xe1ecf4,0xa89a83,1.66));
  const sky=new T.Mesh(new T.SphereGeometry(190,32,16), new T.ShaderMaterial({
    side:T.BackSide,depthWrite:false,
    vertexShader:'varying vec3 v; void main(){v=position;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}',
    fragmentShader:`varying vec3 v;void main(){vec3 d=normalize(v); float h=max(d.y,0.); vec3 c=mix(vec3(.94,1.,1.04),vec3(.24,.49,.80),pow(h,.48)); float a=max(dot(d,normalize(vec3(-24.,42.,24.))),0.);c+=vec3(1.,.83,.54)*pow(a,60.)*.45;gl_FragColor=vec4(c,1.);
    #include <tonemapping_fragment>
    #include <colorspace_fragment>
    }`
  }));scene.add(sky);
  const [model,boxes,walkways]=await Promise.all([loadStreet(progress),fetch('./obstacles.json?v=cars-4').then(r=>r.json()),fetch('./walkways.json').then(r=>r.json())]);
  progress.value=78;label.textContent="잠시 후 시작할 수 있어요";
  scene.add(model.scene);
  const breeze={value:0};
  model.scene.traverse(o=>{
    if(!o.isMesh)return;
    o.castShadow=true;o.receiveShadow=true;
    const mat=o.material;
    if(mat.map)mat.map.anisotropy=Math.min(4,renderer.capabilities.getMaxAnisotropy());
    if(mat.name==='asphalt')mat.color.setScalar(.66);
    if(mat.name==='paint'||mat.name==='ochre'){
      mat.onBeforeCompile=shader=>{
        shader.vertexShader='varying vec3 markPosition;\n'+shader.vertexShader.replace('#include <begin_vertex>','#include <begin_vertex>\n markPosition=(modelMatrix*vec4(position,1.)).xyz;');
        shader.fragmentShader='varying vec3 markPosition;\n'+shader.fragmentShader.replace('#include <color_fragment>',`#include <color_fragment>
          vec2 grid=floor(markPosition.xz*130.);
          float chips=fract(sin(dot(grid,vec2(12.9898,78.233)))*43758.5);
          float strength=1.-smoothstep(.3,1.8,max(fwidth(markPosition.x),fwidth(markPosition.z))*130.);
          diffuseColor.rgb*=mix(.82,mix(.26,1.,smoothstep(.025,.17,chips)),strength);`);
      };
    }
    if(mat.name==='canopy'){
      mat.transparent=false;mat.alphaTest=.42;mat.side=T.DoubleSide;mat.depthWrite=true;
      mat.shadowSide=T.DoubleSide;
      mat.onBeforeCompile=shader=>{
        shader.uniforms.breeze=breeze;
        shader.vertexShader='uniform float breeze;\n'+shader.vertexShader.replace('#include <begin_vertex>',`
          #include <begin_vertex>
          vec3 worldLeaf=(modelMatrix*vec4(position,1.)).xyz;
          float heightWeight=smoothstep(2.,6.,worldLeaf.y);
          float gust=sin(breeze*1.15+worldLeaf.x*.84+worldLeaf.z*.56);
          transformed.x+=heightWeight*(gust*.047+.014*sin(breeze*2.4+worldLeaf.y*4.));
          transformed.z+=heightWeight*.019*cos(breeze+worldLeaf.z);
        `);
      };
    }
    if(mat.name.endsWith('interior daylight')){mat.color.setScalar(.25);mat.emissiveIntensity=.12;}
    if(mat.name==='windscreen'){mat.depthWrite=false;o.castShadow=false;}
    if(mat.name==='Cafe glazing'){o.castShadow=false;mat.depthWrite=false;mat.opacity=.085;mat.metalness=.18;}
    if(mat.name.startsWith('leaf'))mat.side=T.DoubleSide;
  });
  scene.background=new T.Color(0xc6dbea);
  const gltf=new GLTFLoader();
  async function prop(name,x,z,height,rotation,baseY,solid=true){
    const {scene:object}=await gltf.loadAsync('./props/'+name+'/'+name+'.gltf');
    const bound=new T.Box3().setFromObject(object),size=bound.getSize(new T.Vector3());
    object.scale.multiplyScalar(height/size.y);object.rotation.y=rotation;
    bound.setFromObject(object);const center=bound.getCenter(new T.Vector3());
    object.position.add(new T.Vector3(x-center.x,baseY-bound.min.y,z-center.z));
    object.traverse(o=>{if(o.isMesh){o.castShadow=true;o.receiveShadow=true;}});
    scene.add(object);
    bound.setFromObject(object);if(solid)boxes.push([bound.min.x,bound.max.x,bound.min.z,bound.max.z]);
  }
  await prop('water_manhole_cover',0,3,.035,0,.001,false);
  // A local reflection probe includes the opposite frontage and real canopy silhouettes.
  // All six sides see the same fixed sun and static city.
  renderer.shadowMap.autoUpdate=false;
  renderer.shadowMap.needsUpdate=true;
  const target=new T.WebGLCubeRenderTarget(512,{type:T.HalfFloatType,generateMipmaps:true,minFilter:T.LinearMipmapLinearFilter});
  const probe=new T.CubeCamera(.3,190,target);probe.position.set(0,3.5,-9.7);probe.update(renderer,scene);
  const pmrem=new T.PMREMGenerator(renderer), environment=pmrem.fromCubemap(target.texture);
  scene.environment=environment.texture;
  // Project static street reflections onto the opposite frontage. One capture serves every frame.
  model.scene.traverse(o=>{
    if(!o.isMesh||!['glass','smoke','tint'].includes(o.material.name))return;
    const mat=o.material;
    mat.envMap=environment.texture;mat.metalness=.57;mat.roughness=.13;
    mat.onBeforeCompile=shader=>{
      shader.uniforms.streetReflection={value:target.texture};
      shader.uniforms.probeCenter={value:probe.position};
      shader.vertexShader='varying vec3 panePosition;\n'+shader.vertexShader.replace('#include <worldpos_vertex>',
        '#include <worldpos_vertex>\n panePosition=(modelMatrix*vec4(transformed,1.)).xyz;');
      shader.fragmentShader='varying vec3 panePosition; uniform samplerCube streetReflection; uniform vec3 probeCenter;\n'+shader.fragmentShader.replace('#include <opaque_fragment>',`
        vec3 N=normalize(inverseTransformDirection(normal,viewMatrix));
        vec3 V=normalize(cameraPosition-panePosition);
        vec3 R=reflect(-V,N);
        float opposite=R.z>0.?12.:-32.;
        float t=clamp((opposite-panePosition.z)/(abs(R.z)<.001?.001:R.z),0.,90.);
        vec3 ray=normalize(panePosition+t*R-probeCenter);
        vec3 reflected=textureCube(streetReflection,ray).rgb;
        float fresnel=pow(1.-clamp(abs(dot(N,V)),0.,1.),3.);
        outgoingLight=mix(outgoingLight,reflected*vec3(.86,1.04,1.00),.36+.38*fresnel);
        #include <opaque_fragment>`);
    };
  });
  pmrem.dispose();
  const canvas=renderer.domElement;
  let walked=false, turned=false, destination='', lockHint=false;
  const panelButtons=[...document.querySelectorAll('footer [aria-controls]')];
  function setPanel(open){
    for(const button of panelButtons){
      const visible=button===open;
      document.getElementById(button.getAttribute('aria-controls')).hidden=!visible;
      button.setAttribute('aria-expanded',String(visible));
    }
  }
  for(const button of panelButtons)button.onclick=()=>setPanel(button.getAttribute('aria-expanded')==='true'?null:button);
  function updateStatus(){
    status.textContent=destination?destination+' 이동 중 · WASD로 직접 걷기':
      lockHint?'Esc를 누르면 커서를 쓸 수 있어요':
      walked&&turned?'':'마우스로 둘러보고 WASD로 걸어보세요';
  }
  canvas.addEventListener('firstwalk',()=>{walked=true;updateStatus();});
  canvas.addEventListener('firstlook',()=>{turned=true;updateStatus();});
  canvas.addEventListener('tripend',()=>{destination='';updateStatus();});
  let shownLock=false;
  document.addEventListener('pointerlockchange',()=>{
    if(document.pointerLockElement===canvas&&!shownLock){
      shownLock=lockHint=true;setPanel(null);updateStatus();
      setTimeout(()=>{lockHint=false;updateStatus();},2800);
    }else if(!document.pointerLockElement){lockHint=false;updateStatus();}
  });
  addEventListener('keydown',e=>{
    if(document.body.dataset.view!=='walking')return;
    if(e.key==='?'){
      if(document.pointerLockElement)document.exitPointerLock();
      panelButtons[1].click();
    }else if(e.key==='Escape')setPanel(null);
  });
  canvas.addEventListener('click',()=>setPanel(null));
  progress.value=92;
  const walker=await createWalker(scene,camera,boxes,canvas,walkways);
  const body=document.body,arrival=document.querySelector('#arrival'),enter=document.querySelector('#enter');
  const reducedMotion=matchMedia('(prefers-reduced-motion: reduce)');
  let flightStart=0;
  const aerial=new T.Vector3(-19,30,4);
  const landing=camera.position.clone();
  const curve=new T.CubicBezierCurve3(aerial,new T.Vector3(-15,26,3),new T.Vector3(-3,10,9),landing);
  const landingTarget=new T.Vector3();
  camera.getWorldDirection(landingTarget).multiplyScalar(9).add(landing);
  const aerialTarget=new T.Vector3(5,1,-8),focus=new T.Vector3();
  function finishFlight(){
    body.dataset.view='walking';
    camera.position.copy(landing);camera.lookAt(landingTarget);
    document.querySelector('footer').hidden=false;
    canvas.tabIndex=-1;canvas.focus({preventScroll:true});updateStatus();
  }
  enter.onclick=()=>{
    if(body.dataset.view!=='aerial')return;
    arrival.hidden=true;
    flightStart=performance.now();
    body.dataset.view='descending';
    if(reducedMotion.matches)finishFlight();
  };
  for(const action of ['reset','detail','parking']){
    const button=document.getElementById(action);
    button.onclick=()=>{
      setPanel(null);canvas.focus({preventScroll:true});
      if(walker[action]()){destination=button.textContent;updateStatus();}
      else status.textContent='여기서는 경로를 찾을 수 없어요. 조금 이동한 뒤 다시 선택해 주세요.';
    };
  }
  addEventListener('resize',()=>{camera.aspect=innerWidth/innerHeight;camera.updateProjectionMatrix();renderer.setSize(innerWidth,innerHeight);});
  renderer.shadowMap.autoUpdate=false;
  renderer.shadowMap.needsUpdate=true;
  let draw=createContactPass(renderer,camera);
  let sampleSeconds=0, sampleFrames=0;
  renderer.setAnimationLoop(()=>{
    const dt=clock.getDelta();
    breeze.value+=Math.min(dt,.12);
    const view=body.dataset.view;
    if(view==='walking')walker.update(dt);
    else if(view==='loading'||view==='aerial'){
      camera.position.copy(aerial);camera.lookAt(aerialTarget);
    }else if(view==='descending'){
      const now=performance.now();
      const progress=Math.min(1,(now-flightStart)/3600);
      const blend=progress*progress*(3-2*progress);
      curve.getPoint(blend,camera.position);
      camera.lookAt(focus.lerpVectors(aerialTarget,landingTarget,blend));
      if(progress===1)finishFlight();
    }
    draw(scene);
    if(view==='loading'){
      progress.value=100;
      body.dataset.view='aerial';
      document.querySelector('#loading').hidden=true;enter.hidden=false;
    }
    if(document.hidden||dt>.25){sampleSeconds=0;sampleFrames=0;return;}
    sampleSeconds+=dt;sampleFrames++;
    if(sampleSeconds>=1.5){
      if(sampleFrames/sampleSeconds<32){
        draw=scene=>renderer.render(scene,camera);
      }
      if(sampleFrames/sampleSeconds<40&&renderer.getPixelRatio()>.8){
        renderer.setPixelRatio(Math.max(.8,renderer.getPixelRatio()-.2));
      }
      sampleSeconds=0;sampleFrames=0;
    }
  });
}
