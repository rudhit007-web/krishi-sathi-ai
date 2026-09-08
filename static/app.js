const $=s=>document.querySelector(s);
let currentWeather={}, currentLang="English", currentPlan={};

document.querySelectorAll("[data-scroll]").forEach(b=>b.addEventListener("click",()=>document.getElementById(b.dataset.scroll).scrollIntoView({behavior:"smooth"})));

const translations={
 English:{hero:"Know what to grow, how to grow it, when to act — and how to reach the right buyers.",start:"Start my farm plan",farm:"Tell KrishiSaathi about your field.",roadmap:"From seed to harvest, one clear path.",market:"Don't wait until harvest to find a buyer.",assistant:"Ask in the language you understand.",ask:"Ask your farming question…"},
 Hindi:{hero:"क्या उगाना है, कैसे उगाना है, कब क्या करना है — और सही खरीदार तक कैसे पहुँचना है, एक ही जगह।",start:"मेरी खेती योजना शुरू करें",farm:"अपने खेत की जानकारी दें।",roadmap:"बीज से कटाई तक एक आसान योजना।",market:"फसल तैयार होने तक खरीदार का इंतज़ार न करें।",assistant:"जिस भाषा में समझें, उसी में पूछें।",ask:"खेती से जुड़ा सवाल पूछें…"},
 Marathi:{hero:"काय पिकवायचे, कसे पिकवायचे, कधी काय करायचे — आणि योग्य ग्राहकांपर्यंत कसे पोहोचायचे, एकाच ठिकाणी.",start:"माझी शेती योजना सुरू करा",farm:"तुमच्या शेताची माहिती द्या.",roadmap:"बियाण्यापासून काढणीपर्यंत स्पष्ट मार्ग.",market:"कापणीच्या आधीच ग्राहक शोधा.",assistant:"तुम्हाला समजणाऱ्या भाषेत विचारा.",ask:"शेतीबद्दल प्रश्न विचारा…"}
};
$("#language").onchange=e=>{currentLang=e.target.value;const t=translations[currentLang];$("#heroText").textContent=t.hero;$("#start").innerHTML=t.start+" <b>→</b>";$("#farm h2").textContent=t.farm;$("#roadmap h2").textContent=t.roadmap;$("#market h2").textContent=t.market;$("#assistant h2").textContent=t.assistant;$("#chatInput").placeholder=t.ask;$("#aiStatus").textContent="Ready • "+currentLang};

function readData(){
 return {language:currentLang,crop:$("#crop").value,location:$("#location").value,quantity:$("#quantity").value,harvest_date:$("#harvest").value,selling_route:$("#route").value,
 soil:{ph:$("#ph").value,n:$("#n").value,p:$("#p").value,k:$("#k").value,moisture:$("#moisture").value,organic:$("#organic").value},
 weather:{temperature:$("#temperature").value,humidity:$("#humidity").value,rain:$("#rain").value,wind:$("#wind").value},live_weather:currentWeather};
}

$("#weatherBtn").onclick=()=>{
 if(!navigator.geolocation){alert("Location is not available in this browser.");return}
 $("#weatherBtn").textContent="Getting live weather…";
 navigator.geolocation.getCurrentPosition(async pos=>{
  try{
   const r=await fetch(`/api/weather?lat=${pos.coords.latitude}&lon=${pos.coords.longitude}`);const d=await r.json();currentWeather=d;
   const c=d.current||{};$("#temperature").value=Math.round(c.temperature_2m??"");$("#humidity").value=Math.round(c.relative_humidity_2m??"");$("#rain").value=c.precipitation??"";$("#wind").value=Math.round(c.wind_speed_10m??"");
   $("#weatherBtn").textContent="✓ Live weather connected";$("#liveState").textContent="LIVE WEATHER";$("#tempStat").textContent=Math.round(c.temperature_2m??0);
  }catch(e){alert("Weather service could not be reached. You can enter weather manually.");$("#weatherBtn").textContent="◎ Use my location for live weather"}
 },()=>{alert("Please allow location access.");$("#weatherBtn").textContent="◎ Use my location for live weather"});
};

$("#analyze").onclick=async()=>{
 const data=readData();
 if(!data.soil.ph){alert("Please enter soil pH first.");return}
 $("#analyze").disabled=true;$("#analyze").textContent="Building your farm plan…";
 try{
  const r=await fetch("/api/plan",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(data)});currentPlan=await r.json();renderPlan(currentPlan,data);
  document.getElementById("results").scrollIntoView({behavior:"smooth"});
 }catch(e){alert("Could not connect to the planner. Make sure the Flask server is running.")}finally{$("#analyze").disabled=false;$("#analyze").innerHTML="Build my complete farm plan <b>→</b>"}
};

function renderPlan(p,data){
 $("#score").textContent=p.score??"--";$("#bigScore").textContent=p.score??"--";$("#cropStat").textContent=p.crop||"TOP";$("#phStat").textContent=data.soil.ph||"—";$("#tempStat").textContent=data.weather.temperature||"—";
 $("#planTitle").textContent=p.crop?`${p.crop}: your field-to-market plan`:"Top crop options for your field";
 $("#planSummary").textContent=p.summary||"Plan ready.";
 $("#soilNote").textContent=p.soil_note||"—";$("#weatherNote").textContent=p.weather_note||"—";
 const sug=$("#cropSuggestions");sug.innerHTML="";
 if(p.crop && p.crop!==""){sug.innerHTML=`<div class="suggestion"><b>Selected crop</b><span>${p.crop}</span></div>`}
 else{
  // fallback local suggestions based on the same crop model
  const ph=parseFloat(data.soil.ph||6.5), t=parseFloat(data.weather.temperature||25);
  const options=[["Wheat",6.0,7.5,10,25],["Rice",5.5,7,20,35],["Maize",5.8,7,18,30],["Soybean",6,7.5,20,30],["Chickpea",6,8,15,25]].map(x=>({name:x[0],s:(ph>=x[1]&&ph<=x[2]?25:5)+(t>=x[3]&&t<=x[4]?20:5)})).sort((a,b)=>b.s-a.s).slice(0,3);
  options.forEach((o,i)=>sug.innerHTML+=`<div class="suggestion"><b>${i+1}. ${o.name}</b><span>soil + weather fit</span></div>`);
 }
 $("#timeline").innerHTML=(p.roadmap||[]).map((x,i)=>`<div class="step"><div class="num">${String(i+1).padStart(2,"0")}</div><b>${x}</b><p>Use crop stage, soil moisture and local weather as your decision signals.</p></div>`).join("");
 $("#tips").innerHTML=(p.tips||[]).map(x=>`<li>${x}</li>`).join("");
 $("#buyers").innerHTML=(p.buyer_plan||[]).map(x=>`<div class="buyer"><b>${x.title}</b><p>${x.text}</p></div>`).join("");
 $("#liveState").textContent=p.mode==="gemini"?"AI PLAN":"LOCAL PLAN";
}

document.querySelectorAll(".chips button").forEach(b=>b.onclick=()=>{$("#chatInput").value=b.textContent;sendChat()});
$("#send").onclick=sendChat;$("#chatInput").onkeydown=e=>{if(e.key==="Enter")sendChat()};

async function sendChat(){
 const msg=$("#chatInput").value.trim();if(!msg)return;addBubble(msg,"user");$("#chatInput").value="";$("#aiStatus").textContent="Thinking…";
 try{const r=await fetch("/api/chat",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({message:msg,language:currentLang,context:readData(),plan:currentPlan})});const d=await r.json();addBubble(d.answer,"ai");$("#aiStatus").textContent=(d.mode==="gemini"?"Gemini AI":"Demo assistant")+" • "+currentLang}catch(e){addBubble("The assistant could not connect right now. Please try again.","ai");$("#aiStatus").textContent="Connection issue"}
}
function addBubble(t,c){const el=document.createElement("div");el.className="bubble "+c;el.textContent=t;$("#messages").appendChild(el);$("#messages").scrollTop=$("#messages").scrollHeight}
