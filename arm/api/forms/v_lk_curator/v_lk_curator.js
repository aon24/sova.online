//
//
//
window.sovaActions = window.sovaActions || {};
window.sovaActions.v_lk_curator = {
	init2: doc => {
		if (doc.fieldValues.GRID)
			doc.util.getJson(doc, `form=v_lk_curator&event=${doc.getField('event')}&cmd=getSgr&group=${doc.fieldValues.GRID}`)
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
		newPay: (doc, par, ctrl, shiftKey) => {
			let [sgrId, sstId, pref] = par.split('|');
			
			let view = doc.getControl('mainList');
			view.selectedDoc = sstId;
			view.forceUpdate();
						
			let page = {
				addUrl: `&sgrId=${sgrId}&sstId=${sstId}&profile=${pref}`,			
				rsMode: 'new',
				newForm: 'Payment',
				dbAlias: 'nv_Payment',
				title: 'Новый платеж',
			};
			doc.previewNew(page);
		},
		
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
		setField: (doc, prm) => {
			let text;
			let [fi, id, value] = prm.split('|');

			let view = doc.getControl('mainList');
			view.selectedDoc = id;
			view.forceUpdate();

			switch(fi) {
				case 'was_s':
					text = value ? 'Установить "Пропустил"' : 'Установить "Был на занятии"';
					break;
				case 'esse_s':
					text = value ? 'Сбросить "Эссе"' : 'Установить "Эссе"';
					break;
				case 'consultant_s':
					text = value ? 'Сбросить "Консультант"' : 'Установить "Консультант"';
					break;
				case 'allow_s':
					text = value ? 'Сбросить "Допуск"' : 'Установить "Допуск"';
					break;
			}
			doc.msg.box('выбранному студенту ?', `Установка полей|${text}\n`)
				.then( () => {
					let body = JSON.stringify([`form=v_lk_curator&cmd=setField&field=${fi}`, `${id}=${value ? '' : '1'}`]);
					doc.util.getJson(doc, body, true)
						.then( res => {
							if (res !== 'OK')
								console.error(`http-status: ${res}`)
							doc.loadView('mainList', true, id);
						})
						.catch( err => console.error(err) );
				}) // end msg.box
				.catch(() => {});
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
			else if (fi === 'was_s')
				text = 'Установить "Был на занятии"';
			else if (fi === 'was_r') {
				text = 'Установить "Пропустил"';
				fi = 'was_s';
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
					if (buf) {
						let body = JSON.stringify([`form=v_lk_curator&cmd=setField&field=${fi}`, buf]);
                        doc.util.getJson(doc, body, true)
							.then( res => {
								if (res !== 'OK')
									console.error(`http-status: ${res}`)
								doc.loadView('mainList', true);
							})
							.catch( err => console.error(err) );
					}
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
		EVENT: (doc, val) => {
			if (doc.fieldValues.GRID)
				doc.util.getJson(doc, `form=v_lk_curator&event=${val}&cmd=getSgr&group=${doc.fieldValues.GRID}`)
					.then( sgr => { 
						doc.changeDropList('leftList', sgr, 0);
						setTimeout(() => doc.forceUpdate(), 100);
					})
					.catch( () => {});
		},

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
			let mainList = doc.getControl('mainList');
			mainList.mainDocs = [];
			for (let k in doc.register) {
				if (k.startsWith('SELONE_'))
					delete doc.register[k];
			} 
			mainList.loadView(true); // true -> refresh
		},

		UPLIST: (doc, selectedLeft) => {
			if (document.getElementById('chb_vm'))
				document.getElementById('chb_vm').checked = doc.checked = false;
			
			let grId = doc.getField('upList').partition('|')[1];
			doc.util.getJson(doc, `cmd=well&clues=sessionsGr_GrId_band|${grId}`)
				.then( sgr => doc.changeDropList('leftList', sgr, 0))
				.catch( () => {});				
		},
	}
};

window.sovaActions.v_lk_curator2 = window.sovaActions.v_lk_curator;


