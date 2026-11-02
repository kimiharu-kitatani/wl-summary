// No credentials are stored on the phone. Requests are submitted using GitHub's signed-in form.
(() => {
  const owner = 'kimiharu-kitatani', repo = 'wl-summary';
  const api = `https://api.github.com/repos/${owner}/${repo}/issues`;
  const key = 'wl_mobile_delete_jobs_v1';
  let jobs; try { jobs = JSON.parse(localStorage.getItem(key) || '[]'); } catch { jobs = []; }
  if (!Array.isArray(jobs)) jobs = [];
  const box = document.createElement('section');
  box.style.cssText = 'margin:12px;padding:12px;border:1px solid #93c5fd;border-radius:12px;background:#eff6ff';
  box.setAttribute('aria-live', 'polite');
  document.querySelector('header').after(box);
  const save = () => localStorage.setItem(key, JSON.stringify(jobs));
  const labels = {draft:'依頼は未送信です。GitHub画面で「Create」を押してください',waiting:'PC／Chromeの接続待ちです。PCが閉じている場合は、起動してChromeを開くと順に処理します',running:'PCで削除中です。途中でPCを閉じると結果確認が必要になります',done:'削除完了',failed:'削除できませんでした。内容を確認してください',interrupted:'PCの処理が中断されました。削除結果を確認してから再依頼してください'};
  let error = '', checking = false;
  function render() {
    box.hidden = !jobs.length;
    box.replaceChildren();
    const h = document.createElement('strong'); h.textContent = 'スマホからの削除依頼'; box.append(h);
    for (const job of jobs.slice(-10).reverse()) {
      const row = document.createElement('p');
      row.textContent = `${job.ids.length}件：${labels[job.state] || '状態確認待ち'}${job.message ? '／' + job.message : ''}`;
      box.append(row);
      const link = document.createElement('a'); link.href = job.url; link.target = '_blank'; link.rel = 'noopener';
      link.textContent = job.number ? '依頼と結果を見る' : '依頼の送信画面を開く'; box.append(link);
      if (job.state === 'draft') { const cancel=document.createElement('button');cancel.textContent='この未送信表示を消す';cancel.onclick=()=>{jobs=jobs.filter(x=>x.id!==job.id);save();render()};box.append(cancel); }
    }
    if (error) { const p=document.createElement('p');p.textContent=error;box.append(p); }
    const btn = document.createElement('button');btn.textContent = checking ? '確認中…' : '状態を更新';btn.disabled=checking;btn.onclick=()=>poll();box.append(btn);
  }
  window.requestMobileDelete = ids => {
    ids = [...new Set(ids)].filter(id=>/^[\w-]{11}$/.test(id));
    if (!ids.length) return;
    if(ids.length>50){alert('スマホからは1回50件まで選択してください');return;}
    if(!confirm(`選んだ${ids.length}件をYouTubeの「後で見る」から削除する依頼を作ります。次のGitHub画面で送信を確定してください。PCが閉じている場合はPC／Chromeの起動後に処理します。`))return;
    const id = crypto.randomUUID();
    const body = `選択した動画をYouTubeの「後で見る」から削除してください。PC／Chromeの接続待ちです。\n\n<!-- WL_DELETE_REQUEST: ${JSON.stringify({version:1,id,ids})} -->`;
    const url = `https://github.com/${owner}/${repo}/issues/new?title=${encodeURIComponent('[WL削除依頼] '+id)}&body=${encodeURIComponent(body)}`;
    jobs.push({id,ids,state:'draft',url,createdAt:Date.now()});save();render();window.open(url,'_blank','noopener');
  };
  async function poll() {
    if(checking || !jobs.length || document.hidden)return;
    checking=true;error='';render();
    try {
      const r=await fetch(`${api}?creator=${owner}&state=all&sort=created&direction=desc&per_page=100`,{headers:{Accept:'application/vnd.github+json'},cache:'no-store'});
      if(!r.ok)throw new Error(`状態確認に失敗しました（${r.status}）。依頼が送信済みなら取り消されません。あとで更新してください`);
      const issues=await r.json();
      let listChanged=false;
      for(const job of jobs){
        const issue=issues.find(x=>x.title==='[WL削除依頼] '+job.id && x.user?.login?.toLowerCase()===owner);
        if(!issue)continue;
        const match=issue.body?.match(/<!-- WL_DELETE_STATUS: (.*?) -->/);
        let status=null;try{status=match?JSON.parse(match[1]):null}catch{}
        job.number=issue.number;job.url=issue.html_url;
        job.state=status?.state || (issue.state==='closed'?'failed':'waiting');
        job.message=status?.message || (issue.state==='closed'?'依頼は閉じられています。結果を確認してください':'');
        if(status?.state==='done' && Array.isArray(status.removed)) {
          const deleted=new Set(JSON.parse(localStorage.getItem('wl_deleted')||'[]'));
          status.removed.filter(id=>job.ids.includes(id)).forEach(id=>{deleted.add(id);SEL.delete(id);const row=D.find(x=>x.videoId===id);if(row&&!row.removed){Object.assign(row,{removed:true,removed_at:new Date().toISOString()});listChanged=true}});localStorage.setItem('wl_deleted',JSON.stringify([...deleted]));
        }
      }
      save();if(listChanged)window.render();
    }catch(e){error=e.message}finally{checking=false;render()}
  }
  document.addEventListener('visibilitychange',()=>{if(!document.hidden)poll()});
  setInterval(poll,120000); render();poll();
})();
