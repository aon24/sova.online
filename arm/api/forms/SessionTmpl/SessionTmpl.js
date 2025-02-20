let refreshVideoList = (doc, save) => {
	doc.videoList = [];
	for (let i=0; i < 20; i++) {
		if (`VL${i}_URL` in doc.register) { 
			if (save && doc.getField(`vl${i}_forDel`)) // mark for del
				continue;
				
			item = {platform: doc.platforms[`VL${i}`] || ''};
			for (let it of ['url', 'hrefs', 'image', 'notes', 'name', 'slip', 'video_id']) {
				let value = doc.getField(`vl${i}_${it}`);
				if (value)
					item[it] = value;
			}
			doc.videoList.push(item);
		}
	}
};
// *** *** ***

window.sovaActions = window.sovaActions || {};
window.sovaActions.SessionTmpl = {
	init: doc => {
		doc.videoList = JSON.parse(doc.fieldValues.VIDEOLIST || '[]');
		doc.videoList.sort((a, b) => (a.name || '') > (b.name || '') ? 1 : -1);
	},
	
	cmd: {
		createYD: doc => {
			let url=`/api/getData?form=${doc.form}&cmd=createYD&id=${doc.fieldValues['ID']}`;
			fetch(url, {method: 'get', credentials: 'include'})
				.then( response => !response.ok ? 
					response.text().then( tx => doc.msg.error(tx, 'getFormDir-error:'))
					:
					response.text().then( tx => {
						doc.setField('YDcreated', 1);
						doc.forceUpdate();
						console.log(tx);
					})
				)
				.catch( err => doc.msg.error(err.message, 'getFormDir-error:'));			
		},
		vkAut: (doc, url) => doc.util.xopen(url),
		openImg: (doc, i) => {
			if (i !== 0)
				i = i || '';
			let img = {
				dbAlias: 'dba',
				unid: 'new',
				pageName: 'Pictures',
				title: 'Pictures',
				rsMode: 'preview',
				newForm: 'img',
				modal: 1,
				addUrl: `&vl=${i}&formDir=Программа`,
			}
			doc.util.addChildPage(doc, img);
		},

		addEmpty: doc => {
			doc.videoList.push({url:'', 
				image: doc.getField('sticker') || '/image/owl in fly.png',
				name: doc.getField('title')
			});
			doc.getControl('videoGrid').forceUpdate();
		},
		saved: doc => {
			if (doc.mainDoc !== doc) {
				if (doc.page.owner.form === 'v_content') {
					let owner = doc.page.owner;
					doc.util.jsonByUrl(doc, `/api/getData?form=v_content&cmd=getLectors&nve=${owner.getField('upList')}`)
						.then( sgr => {
							owner.changeDropList('leftList', sgr, 0);
					
							if (owner.getField('view') === 1)
								owner.loadView('mainList', true);
							else
								owner.util.jsonByUrl(owner, `/api/getData?form=v_content&cmd=showC&lector=${owner.getField('leftList')}&nve=${owner.getField('upList')}&status=${owner.getField('status')}`)
									.then( js => owner.setField('showCourse', js) )
									.catch( e => owner.msg.error(e) );
						})
						.catch(()=>{});
				}
				else {
					doc.util.mainListGr(doc, '');
					doc.util.mainListGr(doc, '2');
				}
            }  
		},

		openYD: doc => doc.util.xopen(doc.getField('openYDurl')),
		openVK: (doc, url) => doc.util.xopen(url),
		
		makeVideoY: doc => {
			let id = doc.fieldValues['ID'];
			if (!id)
				return doc.msg.ok('Сохраните документ перед обновлением.','Обновление видео|Документ не сохранен.');
    		
    		doc.util.jsonByUrl(doc, `/api/getData?form=SessionTmpl&cmd=makeVideoY&id=${id}`)
    			.then( js => {
					for (let it of js || []) {
						let e = false;
						for (let it2 of doc.videoList) { // ищем с таким же урл
							if (it.url === it2.url) {
								e = true;
								break;
							}
						}
						if (!e) // не нашли, - вставляем
    						doc.videoList.push(it);
    				}
    				doc.forceUpdate();
    			})
    			.catch( e => doc.msg.error(e) );			
		},
		makeVideoVK: doc => {
			let id = doc.fieldValues['ID'];
			if (!id)
				return doc.msg.ok('Сохраните документ перед обновлением.','Обновление видео|Документ не сохранен.');
    		
    		doc.util.jsonByUrl(doc, `/api/getData?form=SessionTmpl&cmd=makeVideoVK&id=${id}`)
    			.then( js => {
					for (let it of js || []) {
						let e = false;
						for (let it2 of doc.videoList) { // ищем с таким же урл
							if (it.url === it2.url) {
								e = true;
								break;
							}
						}
						if (!e) // не нашли, - вставляем
    						doc.videoList.push(it);
    				}
    				doc.forceUpdate();
    			})
    			.catch( e => doc.msg.error(e) );			
		},
		
		test: (doc, url) => {
    		fetch(url, {method: 'get', credentials: 'include'})
				.then( response => response.text() )
				.then( t => console.log(t) )
    			.catch( e => console.log(e.message));
		},
		
		refreshVideo: doc => refreshVideoList(doc) || doc.getControl('videoGrid').forceUpdate(),
	},
	// *** *** ***
	
	recalc: {
	},	
	hide: {
/*
        tm2: doc => !doc.getField('mtx1'),
        tm3: doc => !doc.getField('mtx2'),
        tm4: doc => !doc.getField('mtx3'),
        tm5: doc => !doc.getField('mtx4'),		
        tm6: doc => !doc.getField('mtx5'),		
        tm7: doc => !doc.getField('mtx6'),
*/
        videoMaterial: doc => !doc.getField('y'),
		notSaved: doc => doc.getField('id'),
        createYD: doc => !doc.getField('openYDurl') || doc.getField('YDcreated') || !doc.getField('id'),
        openYD: doc => !doc.getField('openYDurl') || !doc.getField('YDcreated') || !doc.getField('id'),
	},
	validate: {
		title: doc => doc.getField('title') ? '' : 'Заголовок',
		NVEVENT: doc => doc.getField('NVEVENT') ? '' : 'Категория мероприятия',
	},
	querySave: doc => {
		doc.setField('title', doc.getField('title').trim());
		refreshVideoList(doc, true);
		doc.hideNewValues['VIDEOLIST'] = JSON.stringify(doc.videoList);
	},
};

for (let i=0; i < 20; i++) { 
	window.sovaActions.SessionTmpl.recalc[`VL${i}_FORDEL`] = doc => doc.getControl('videoGrid').forceUpdate();
	window.sovaActions.SessionTmpl.cmd[`clrUrl${i}`] = doc => doc.setField(`VL${i}_URL`, '');
	
	window.sovaActions.SessionTmpl.cmd[`insUrl${i}`] = doc => {
		navigator.clipboard.readText()
			.then( clipText => doc.setField(`VL${i}_URL`, clipText) || refreshVideoList(doc) )
			.catch( err => console.error(err));
	};
}	
	
	