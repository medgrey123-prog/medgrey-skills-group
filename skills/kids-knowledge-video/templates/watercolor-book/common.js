// Shared helpers: deterministic RNG, noise, easing, text, mock app UI overlay.
window.Q = (function(){
  const W=1080,H=1920;
  function rng(seed){let s=seed>>>0||1;return ()=>{s^=s<<13;s>>>=0;s^=s>>17;s^=s<<5;s>>>=0;return s/4294967296;};}
  // value noise 2D
  function makeNoise(seed){const r=rng(seed);const p=new Float32Array(512*512);for(let i=0;i<p.length;i++)p[i]=r();
    const g=(x,y)=>p[((y&511)<<9)|(x&511)];
    const sm=t=>t*t*(3-2*t);
    function n(x,y){const xi=Math.floor(x),yi=Math.floor(y),xf=x-xi,yf=y-yi;const a=g(xi,yi),b=g(xi+1,yi),c=g(xi,yi+1),d=g(xi+1,yi+1);const u=sm(xf),v=sm(yf);return a+(b-a)*u+(c-a)*v+(a-b-c+d)*u*v;}
    function fbm(x,y,o=5){let s=0,a=.5,f=1;for(let i=0;i<o;i++){s+=a*n(x*f,y*f);f*=2;a*=.5;}return s;}
    return {n,fbm};}
  const clamp=(x,a=0,b=1)=>Math.max(a,Math.min(b,x));
  const ease=t=>t<.5?4*t*t*t:1-Math.pow(-2*t+2,3)/2;
  const eo=t=>1-Math.pow(1-clamp(t),3);
  const seg=(t,a,b)=>clamp((t-a)/(b-a));
  // spectrum colour for wavelength nm (approx)
  function wl(n){let r=0,g=0,b=0;
    if(n<440){r=-(n-440)/60;b=1}else if(n<490){g=(n-440)/50;b=1}else if(n<510){g=1;b=-(n-510)/20}else if(n<580){r=(n-510)/70;g=1}else if(n<645){r=1;g=-(n-645)/65}else{r=1}
    return [r,g,b].map(v=>Math.round(255*Math.pow(clamp(v),.8)));}
  function grain(ctx,amt=14,seed=7,alpha=1){const id=ctx.getImageData(0,0,W,H),d=id.data;const r=rng(seed);
    for(let i=0;i<d.length;i+=4){const v=(r()-.5)*amt*alpha;d[i]+=v;d[i+1]+=v;d[i+2]+=v;}ctx.putImageData(id,0,0);}
  // mock app chrome so layout can be judged in context (tab bar 300px, right action column 140px)
  function ui(ctx,dark=true){ctx.save();
    const fg=dark?'rgba(255,255,255,':'rgba(20,24,30,';
    const g=ctx.createLinearGradient(0,H-360,0,H);g.addColorStop(0,'rgba(0,0,0,0)');g.addColorStop(1,dark?'rgba(0,0,0,.55)':'rgba(255,255,255,.7)');
    ctx.fillStyle=g;ctx.fillRect(0,H-360,W,360);
    ctx.fillStyle=dark?'rgba(14,16,22,.72)':'rgba(255,255,255,.82)';ctx.fillRect(0,H-170,W,170);
    ctx.fillStyle=fg+'.12)';ctx.fillRect(0,H-170,W,1.5);
    const tabs=['刷一刷','今日任务','复习本','我的'];
    ctx.font='500 30px "Noto Sans CJK SC"';ctx.textAlign='center';
    tabs.forEach((s,i)=>{const x=W/8+i*W/4;ctx.fillStyle=fg+(i==0?'.95)':'.45)');
      ctx.beginPath();ctx.arc(x,H-112,15,0,7);ctx.fill();ctx.fillText(s,x,H-60);});
    // right action column
    const icons=['♥','★','↗'];const lab=['2.1万','收藏','分享'];
    ctx.font='44px "Noto Sans CJK SC"';
    icons.forEach((s,i)=>{const y=H-760+i*150;ctx.fillStyle=dark?'rgba(255,255,255,.14)':'rgba(0,0,0,.06)';ctx.beginPath();ctx.arc(W-78,y,44,0,7);ctx.fill();
      ctx.fillStyle=fg+'.92)';ctx.fillText(s,W-78,y+15);ctx.font='500 24px "Noto Sans CJK SC"';ctx.fillText(lab[i],W-78,y+78);ctx.font='44px "Noto Sans CJK SC"';});
    ctx.restore();}
  return {W,H,rng,makeNoise,clamp,ease,eo,seg,wl,grain,ui};
})();
// leaf outline in local coords: base at (0,0), tip at (L,0)
Q.leaf=function(ctx,L,Wd){ctx.beginPath();ctx.moveTo(0,0);
  ctx.bezierCurveTo(L*.18,-Wd*1.05,L*.62,-Wd*1.0,L,0);
  ctx.bezierCurveTo(L*.62,Wd*1.0,L*.18,Wd*1.05,0,0);ctx.closePath();};
// half-width of leaf at fraction u along length (approx, matches bezier above)
Q.leafHalf=function(u,Wd){return Wd*0.77*Math.pow(Math.sin(Math.PI*Math.pow(u,0.85)),0.9)*(1-0.15*u);};
// veins: returns list of polylines in local coords
Q.leafVeins=function(L,Wd,n=9,seed=3){const r=Q.rng(seed),out=[];
  out.push({w:1,pts:[[0,0],[L*.5,-Wd*.03],[L*.98,0]]});
  for(let i=1;i<=n;i++){const u=i/(n+1)*0.92+0.03;for(const s of[-1,1]){
    const x0=L*u,h=Q.leafHalf(Math.min(.98,u+.12),Wd)*0.88;
    out.push({w:.55,pts:[[x0,0],[x0+L*.07,s*h*.55],[x0+L*.16+r()*8,s*h]]});
    // tertiary
    for(let k=0;k<3;k++){const v=.3+k*.22;const bx=x0+L*.07*v*1.6,by=s*h*.55*v*1.4;
      out.push({w:.25,pts:[[bx,by],[bx-L*.03,by+s*h*.12],[bx-L*.05+r()*10,by+s*h*.28]]});}
  }}return out;};
Q.strokeVeins=function(ctx,veins,base){for(const v of veins){ctx.lineWidth=base*v.w;ctx.beginPath();const p=v.pts;ctx.moveTo(p[0][0],p[0][1]);ctx.quadraticCurveTo(p[1][0],p[1][1],p[2][0],p[2][1]);ctx.stroke();}};
