// Renders index.html to an MP4 frame by frame: node docs/pitch_video/render.js out.mp4 [fps] [from] [to]
const {chromium}=require('playwright');const {spawn}=require('child_process');const path=require('path');
const [out='pitch_silent.mp4',fps=30,from=0,to=240]=process.argv.slice(2);
(async()=>{
  const b=await chromium.launch();const p=await b.newPage({viewport:{width:1920,height:1080}});
  await p.goto('file://'+path.join(__dirname,'index.html'));
  await p.evaluate(async()=>{await document.fonts.ready;await Promise.all([...document.images].map(i=>i.decode().catch(()=>{})))});
  const ff=spawn('ffmpeg',['-y','-loglevel','error','-f','image2pipe','-framerate',String(fps),'-c:v','mjpeg','-i','-','-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p',out],{stdio:['pipe','inherit','inherit']});
  const n0=Math.round(from*fps),n1=Math.round(to*fps);
  for(let n=n0;n<n1;n++){
    await p.evaluate(t=>window.seek(t),n/fps);
    const buf=await p.screenshot({type:'jpeg',quality:92});
    if(!ff.stdin.write(buf))await new Promise(r=>ff.stdin.once('drain',r));
    if(n%300===0)console.log('t =',(n/fps).toFixed(1));
  }
  ff.stdin.end();await new Promise(r=>ff.on('close',r));await b.close();
})();
