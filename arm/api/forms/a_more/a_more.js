let refreshVideoList = (doc, save) => {
	doc.videoList = [];
	for (let i=0; i < 20; i++) {
		if (`VL${i}_URL` in doc.register) { 
			if (save && doc.getField(`vl${i}_forDel`)) // mark for del
				continue;
				
			let item = {platform: doc.platforms[`VL${i}`] || ''};
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
window.sovaActions.a_more = {
	init: doc => {
		doc.videoList = JSON.parse(doc.getField('VIDEOLIST') || '[]');
		doc.videoList.sort((a, b) => (a.name || '') > (b.name || '') ? 1 : -1);

		for (let i=0; i < 20; i++) {
			doc.sova.recalc[`VL${i}_FORDEL`] = doc => doc.getControl('videoGrid').forceUpdate();
			doc.sova.cmd[`clrUrl${i}`] = doc => doc.setField(`VL${i}_URL`, '');
			doc.sova.cmd[`insUrl${i}`] = doc => {
				navigator.clipboard.readText()
					.then( clipText => doc.setField(`VL${i}_URL`, clipText) || refreshVideoList(doc) )
					.catch( err => console.error(err));
			};
		}			
	},

    init2: doc => {
		let m = parseFloat(localStorage.getItem('nvScale') || 1);
		let sca = [0.5, 0.75, 0.9, 1, 1.1, 1.25, 1.5];
		if (sca.includes(m))
			doc.setField('scale_etc', sca.indexOf(m));
		else {
			doc.setField('scale_etc', 3);
			doc.mainDoc.m = 1;
			localStorage.setItem('nvScale', 1);
			doc.mainDoc.forceUpdate();
		}
	},
	
	cmd: {
		addFeedback: doc => window.sovaActions.arm.cmd.addFeedback(doc),

		save_etc: doc => {
			localStorage.setItem('nvScale', doc.mainDoc.m);
			doc.mainDoc.msg.ok('Сохранено в локальной памяти браузера');
		},
	},

	recalc: {
		HIDES: doc => doc.forceUpdate(),
		SCALE_ETC: (doc, val) => {
			doc.mainDoc.m = [0.5, 0.75, 0.9, 1, 1.1, 1.25, 1.5][val];
			doc.mainDoc.forceUpdate();
		},		
	},
	
	hide: {
		scale: doc => doc.getField('pageName') !== 'about',
		rtf: doc => doc.getField('hides') !== 'rtf',
		text: doc => doc.getField('hides') !== 'text' || (!doc.getField('text') && doc.readOnly),
		

		href: doc => !doc.getField('href') && doc.readOnly,
		mtx: doc => !doc.getField('mtx') && doc.readOnly,
		mtxLabel: doc => doc.readOnly,
		
	},
};