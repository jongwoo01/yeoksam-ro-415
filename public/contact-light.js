import * as T from 'three';

// Compute short-range contact shadows in view space, so their physical radius
// stays constant as the player approaches mullions, tyres and window reveals.
export function createContactPass(renderer,camera){
  if(!renderer.capabilities.isWebGL2||!renderer.extensions.has('EXT_color_buffer_float')){
    return scene=>renderer.render(scene,camera);
  }
  const target=new T.WebGLRenderTarget(1,1,{type:T.HalfFloatType,samples:0});
  target.depthTexture=new T.DepthTexture(1,1,T.UnsignedIntType);
  const uniforms={
    colorBuffer:{value:target.texture},depthBuffer:{value:target.depthTexture},
    dimensions:{value:new T.Vector2()},inverseProjection:{value:camera.projectionMatrixInverse},
    focalScale:{value:1}
  };
  const material=new T.ShaderMaterial({
    depthTest:false,depthWrite:false, uniforms,
    vertexShader:'varying vec2 coord;void main(){coord=uv; gl_Position=vec4(position.xy,0.,1.);}',
    fragmentShader:`
      uniform sampler2D colorBuffer,depthBuffer;
      uniform vec2 dimensions;
      uniform mat4 inverseProjection;
      uniform float focalScale;
      varying vec2 coord;
      vec3 viewPoint(vec2 uv,float depth){
        vec4 p=inverseProjection*vec4(2.*uv-1.,depth*2.-1.,1.);
        return p.xyz/p.w;
      }
      void main(){
        vec3 light=texture2D(colorBuffer,coord).rgb;
        float d=texture2D(depthBuffer,coord).r;
        vec3 p=viewPoint(coord,d);
        vec3 n=normalize(cross(dFdx(p),dFdy(p)));
        float visibility=1.;
        if(d<.9998&&p.z<-.1){
          float ao=0.;
          for(int i=0;i<8;i++){
            float index=float(i)+.5;
            float angle=index*2.399963;
            float radius=.09+.46*index/8.;
            vec2 shift=vec2(cos(angle),sin(angle))*radius*focalScale/max(.4,-p.z)/dimensions;
            vec2 uv=clamp(coord+shift,vec2(.001),vec2(.999));
            vec3 delta=viewPoint(uv,texture2D(depthBuffer,uv).r)-p;
            float dist=length(delta);
            ao+=max(0.,dot(n,delta/max(.001,dist))-.085)*(1.-smoothstep(.12,.79,dist));
          }
          visibility=clamp(1.-ao*.21,.62,1.);
        }
        gl_FragColor=vec4(light*visibility,1.);
        #include <tonemapping_fragment>
        #include <colorspace_fragment>
      }`
  });
  const screen=new T.Scene(), quad=new T.Mesh(new T.PlaneGeometry(2,2),material);
  screen.add(quad);
  const screenCamera=new T.Camera(),size=new T.Vector2();
  const draw=scene=>{
    renderer.getDrawingBufferSize(size);
    if(target.width!==size.x||target.height!==size.y)target.setSize(size.x,size.y);
    uniforms.dimensions.value.copy(size);uniforms.focalScale.value=.5*size.y*camera.projectionMatrix.elements[5];
    renderer.setRenderTarget(target);renderer.render(scene,camera);
    renderer.setRenderTarget(null);renderer.render(screen,screenCamera);
  };
  draw.dispose=()=>{target.dispose();quad.geometry.dispose();material.dispose();};
  return draw;
}
