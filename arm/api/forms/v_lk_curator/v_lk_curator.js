//
//
//
window.sovaActions = window.sovaActions || {};
window.sovaActions.v_lk_curator = {
	init2: doc => {
		if (doc.fieldValues.GRID)
			doc.util.jsonByUrl(doc, `/api/well?clues=sessionsGr_GrId_band|${doc.fieldValues.GRID}`)
				.then( sgr => { 
					doc.changeDropList('leftList', sgr, 0);
					setTimeout(() => doc.forceUpdate(), 100);
				})
				.catch( () => {});
	},
	// *** *** ***

	hide: {
		viewbar: doc => !doc.checked,
	},
	// *** *** ***

	cmd: {
		selOne: doc => {
			doc.checked = false;
			for (let k in doc.register) {
				if (k.startsWith('SELONE_') && doc.getField(k)) {
					doc.checked = true;
					break;
				}
			}
			doc.forceUpdate();
		},
		
		cmdSet: (doc, fi) => {
			let text;
			let value = '1';
			if (fi === 'allow_s')
				text = 'Установить "допуск"';
			else if (fi === 'allow_r') {
				text = 'Сбросить "допуск"';
				fi = 'allow_s';
				value = '';
			}
			else if (fi === 'video_s')
				text = 'Разрешить "видео"';
			else if (fi === 'video_r') {
				text = 'Заблокировать "видео"';
				fi = 'video_s';
				value = '';
			}
			else
				text = 'Установить "зачет"';

			doc.msg.box('выбранным студентам ?', `Установка полей|${text}\n`)
				.then( () => {
					let buf = '';
					let id;
					for (let k in doc.register) {
						if (k.startsWith('SELONE_') && doc.getField(k)) {
							id = doc.util.partition(k, '_')[1];
							if (buf)
								buf += '¤';
							buf += `${id}=${value}`;
						}
					}
					if (buf)
                        doc.util.serverAction(doc, `putData?form=v_lk_curator&cmd=setField&field=${fi}`, buf)
							.then( res => {
								if (res !== 'OK')
									console.error(`http-status: ${res}`)
								doc.loadView('mainList', true);
							})
							.catch( err => console.error(err) );
				}) // end msg.box
				.catch(() => {});
		},
		cmdPref:(doc, pk, ctrlKey, shiftKey) => {
			let [pkPref, pkSst] = pk.partition('|');
			let view = doc.getControl('mainList');
			view.rowClick(pkSst);
			let page = {form: 'Profile', dbAlias: 'nv_Profile', rsMode: 'edit', unid: pkPref};
			page.title = 'Редактирование профайла студента';
			doc.previewNew(page, ctrlKey, shiftKey);
		},

		cmdEdit:(doc, pk, ctrlKey, shiftKey) => {
			let view = doc.getControl('mainList');
			view.rowClick(pk);
			let page = doc.util.urlKeys(view.props.previewUrl);
			page.title = 'Редактирование сессии студента';
			page.unid = pk;
			page.rsMode = 'edit';
			doc.previewNew(page, ctrlKey, shiftKey);
		},
		
		openSession: (doc, value, ctrlKey, shiftKey) => {
			let ls = (value + '|').split('|');
			let page = {
				frameStyle: {'width': 1000},
				title: doc.getField('group') || 'Сессия группы',
				unid: ls[1],
				dbAlias: 'nv_SessionGr',
				rsMode: 'edit',
			};
			doc.previewNew(page, ctrlKey, shiftKey);
		},

		// *** *** ***

	},
	recalc: {
		SELECTALL: (doc, val) => {
			let checked = false;
			for (let k in doc.register) {
				if (k.startsWith('SELONE_')) {
					doc.setField(k, val);
					checked = val;
				}
			}
			doc.checked = checked;
			doc.forceUpdate();
		},

		STATUS: doc => {
			if (document.getElementById('chb_vm'))
				document.getElementById('chb_vm').checked = doc.checked = false;
			doc.loadView('mainList', true);
		},


		LEFTLIST: (doc, selectedLeft) => {
			if (document.getElementById('chb_vm'))
				document.getElementById('chb_vm').checked = doc.checked = false;
			doc.loadView('mainList', true);
		},

		UPLIST: (doc, selectedLeft) => {
			if (document.getElementById('chb_vm'))
				document.getElementById('chb_vm').checked = doc.checked = false;
			
			let grId = doc.getField('upList').partition('|')[1];
			doc.util.jsonByUrl(doc, `/api/well?clues=sessionsGr_GrId_band|${grId}`)
				.then( sgr => doc.changeDropList('leftList', sgr, 0))
				.catch( () => {});				
		},
	}
};

window.sovaActions.v_lk_curator2 = window.sovaActions.v_lk_curator;


