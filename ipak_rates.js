// Ipak Yo'li bank: "Kassada" tabidagi AQSh dollar kursini o'qiydi.
// Ishlatish: node ipak_rates.js  ->  {"buy":11940,"sell":12030,"updated":"19.11.2026, 05:20","tab":"Kassada"}
const {chromium}=require('playwright');
(async()=>{
  const b=await chromium.launch(); const p=await b.newPage();
  await p.goto('https://ipakyulibank.uz/physical/valyuta-ayirboshlash',{waitUntil:'networkidle',timeout:60000});
  const tab=p.locator('button.view-tab',{hasText:'Kassada'}).first();
  await tab.click(); await p.waitForTimeout(2500);
  const active=await tab.getAttribute('aria-selected');
  const t=await p.evaluate(()=>document.body.innerText);
  const m=t.match(/AQSh dollar\s+([\d ]+?)\s+([\d ]+?)\s*\n/); const u=t.match(/yangilandi\s+([\d.]+,\s*[\d:]+)/);
  await b.close();
  if(!m||active!=='true') throw new Error('Kassada kursi topilmadi');
  console.log(JSON.stringify({buy:+m[1].replace(/\s/g,''),sell:+m[2].replace(/\s/g,''),updated:u&&u[1],tab:'Kassada'}));
})().catch(e=>{console.error(e.message);process.exit(1)});
