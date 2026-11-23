import {radius,distanceFromCenter} from './street-boundary.js';
// Find a walkable polyline with clearance for the character, then remove extra turns.
export function createStreetRouter(boxes){
  const margin=.25;
  const blocks=boxes.map(([l,r,b,t,height=Infinity])=>[l-margin,r+margin,b-margin,t+margin,height]);
  const inside=(x,z)=>distanceFromCenter(x,z)<radius;
  function clear(a,b){
    if(!inside(b.x,b.z))return false;
    const dx=b.x-a.x,dz=b.z-a.z;
    for(const [left,right,near,far,height] of blocks){
      if(a.y>=height&&a.x>=left&&a.x<=right&&a.z>=near&&a.z<=far)continue;
      if(Math.max(a.x,b.x)<left||Math.min(a.x,b.x)>right||Math.max(a.z,b.z)<near||Math.min(a.z,b.z)>far)continue;
      let enter=0,exit=1;
      if(dx){const l=(left-a.x)/dx,r=(right-a.x)/dx;enter=Math.max(enter,Math.min(l,r));exit=Math.min(exit,Math.max(l,r));}
      if(dz){const l=(near-a.z)/dz,r=(far-a.z)/dz;enter=Math.max(enter,Math.min(l,r));exit=Math.min(exit,Math.max(l,r));}
      if(enter<=exit)return false;
    }
    return true;
  }
  const vertices=[];
  for(const [l,r,b,t] of blocks){
    for(const x of [l-.035,r+.035])for(const z of [b-.035,t+.035]){
      const p={x,z};if(clear(p,p))vertices.push(p);
    }
  }
  const distance=(a,b)=>Math.hypot(a.x-b.x,a.z-b.z);
  return (start,end)=>{
    if(clear(start,end))return [end];
    const pending=[{point:start,length:0,score:distance(start,end),parent:null}];
    const best=new Map();
    while(pending.length){
      pending.sort((a,b)=>b.score-a.score);
      const current=pending.pop();
      if(current.length>(best.get(current.point)??Infinity))continue;
      if(clear(current.point,end)){
        const route=[end];let node=current;
        while(node.parent){route.unshift(node.point);node=node.parent;}
        return route;
      }
      for(const point of vertices){
        const length=current.length+distance(current.point,point);
        if(length>=(best.get(point)??Infinity)||!clear(current.point,point))continue;
        best.set(point,length);pending.push({point,length,score:length+distance(point,end),parent:current});
      }
    }
    return [];
  };
}
