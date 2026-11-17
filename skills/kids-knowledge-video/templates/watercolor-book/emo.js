// Emotion helpers: child bust silhouette, standing child, paper texture, watercolor, halftone.
// Bust path (front view). cx,cy = head centre; s = head width.
Q.bust=function(ctx,cx,cy,s,opt={}){const u=v=>v*s;ctx.beginPath();
  // head
  ctx.ellipse(cx,cy,u(.5),u(.56),0,0,7);
  // ears
  ctx.moveTo(cx-u(.47),cy+u(.02));ctx.ellipse(cx-u(.5),cy+u(.06),u(.09),u(.13),0,0,7);
  ctx.moveTo(cx+u(.59),cy+u(.06));ctx.ellipse(cx+u(.5),cy+u(.06),u(.09),u(.13),0,0,7);
  // neck + shoulders + torso
  const ny=cy+u(.45);
  ctx.moveTo(cx+u(.17),ny);ctx.lineTo(cx+u(.19),cy+u(.78));
  ctx.bezierCurveTo(cx+u(.45),cy+u(.86),cx+u(1.05),cy+u(.92),cx+u(1.2),cy+u(1.3));
  ctx.bezierCurveTo(cx+u(1.32),cy+u(1.6),cx+u(1.36),cy+u(2.0),cx+u(1.38),cy+u(2.6));
  ctx.lineTo(cx-u(1.38),cy+u(2.6));
  ctx.bezierCurveTo(cx-u(1.36),cy+u(2.0),cx-u(1.32),cy+u(1.6),cx-u(1.2),cy+u(1.3));
  ctx.bezierCurveTo(cx-u(1.05),cy+u(.92),cx-u(.45),cy+u(.86),cx-u(.19),cy+u(.78));
  ctx.lineTo(cx-u(.17),ny);ctx.closePath();
  // hair tuft (kid)
  if(opt.hair!==false){ctx.moveTo(cx-u(.52),cy-u(.05));
    ctx.bezierCurveTo(cx-u(.6),cy-u(.62),cx-u(.1),cy-u(.78),cx+u(.18),cy-u(.66));
    ctx.bezierCurveTo(cx+u(.3),cy-u(.78),cx+u(.42),cy-u(.7),cx+u(.4),cy-u(.6));
    ctx.bezierCurveTo(cx+u(.62),cy-u(.42),cx+u(.56),cy-u(.12),cx+u(.52),cy-u(.05));
    ctx.bezierCurveTo(cx+u(.3),cy-u(.42),cx-u(.3),cy-u(.42),cx-u(.52),cy-u(.05));ctx.closePath();}
};
// Paper texture canvas (warm, fibres) – deterministic
Q.paper=function(w,h,base=[244,236,222],seed=3,amt=1){const c=document.createElement('canvas');c.width=w;c.height=h;const x=c.getContext('2d');
  const N=Q.makeNoise(seed),id=x.createImageData(w,h),d=id.data,r=Q.rng(seed+1);
  for(let j=0;j<h;j++)for(let i=0;i<w;i++){const k=(j*w+i)*4;const n=N.fbm(i/180,j/180,4)-.5,f=N.n(i/3,j/40)-.5,g=(r()-.5);
    const v=(n*26+f*8+g*10)*amt;d[k]=base[0]+v;d[k+1]=base[1]+v;d[k+2]=base[2]+v*1.1;d[k+3]=255;}
  x.putImageData(id,0,0);return c;};
// Watercolor blob: Tyler Hobbs-style deformed polygon stacked at low alpha
Q.wcPoly=function(cx,cy,r,n,rng,irr=.25){const p=[];for(let i=0;i<n;i++){const a=i/n*6.283;const rr=r*(1+(rng()-.5)*irr);p.push([cx+Math.cos(a)*rr,cy+Math.sin(a)*rr*1]);}return p;};
Q.deform=function(pts,depth,var_,rng){if(depth<=0)return pts;const out=[];for(let i=0;i<pts.length;i++){const a=pts[i],b=pts[(i+1)%pts.length];out.push(a);
  const mx=(a[0]+b[0])/2,my=(a[1]+b[1])/2,l=Math.hypot(b[0]-a[0],b[1]-a[1]);const g=()=>{let s=0;for(let k=0;k<4;k++)s+=rng();return (s-2)/2;};
  out.push([mx+g()*l*var_,my+g()*l*var_]);}return Q.deform(out,depth-1,var_,rng);};
Q.wash=function(ctx,base,color,layers,rng,alpha=.035,var_=.5,edge=.5){// base: polygon; edge = edge-darkening strength
  const b=Q.deform(base,2,var_,rng);ctx.save();ctx.fillStyle=color;ctx.strokeStyle=color;ctx.lineWidth=1.6;
  for(let i=0;i<layers;i++){const p=Q.deform(b,3,var_*.8,rng);ctx.beginPath();p.forEach((q,k)=>k?ctx.lineTo(q[0],q[1]):ctx.moveTo(q[0],q[1]));ctx.closePath();ctx.globalAlpha=alpha;ctx.fill();if(edge){ctx.globalAlpha=alpha*edge;ctx.stroke();}}
  ctx.restore();};
