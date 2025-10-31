const showCalendar = doc => {
	doc.checked = false;

	if (doc.getField('changeView') === 'l' || doc.getField('upList') !== 0) {
		doc.loadView('mainList', true);
	}
	else {
		let url = ['form=v_schedule',
					`cmd=getSelected&plan=${doc.getField('plan')}`,
					`view=${doc.getField('changeView')}`,
					`selected=${doc.getField('leftList')}`,
					`status=${doc.getField('status')}`,
					`upList=${doc.getField('upList')}`,
					`event=${doc.getField('event')}`,
				].join('&')
		doc.util.getJson(doc, url)
			.then( js => {
				doc.setField('showCourse', js);
				doc.forceUpdate();
			})
			.catch( e => doc.msg.error(e.message) );
	}
};

window.sovaActions = window.sovaActions || {};
window.sovaActions.v_schedule = {
	init2: doc => {
		doc.util.getJson(doc, `form=${doc.form}&cmd=changeUp&uplist=0`)
			.then( newList => {
				doc.changeDropList('leftList', newList, 0);
				showCalendar(doc);
			})
			.catch( e => doc.msg.error(e.message) );
	},
	hide: {
		viewbar: doc => !doc.checked, // cPlus
		viewbar1: doc => doc.getField('upList'),
		viewbar2: doc => doc.getField('upList') !== 1,
		mainList: doc => doc.getField('changeView') !== 'l' && doc.getField('upList') === 0,
		showCalendar: doc => doc.getField('changeView') === 'l' || doc.getField('upList'),
		plan: doc => doc.getField('upList') || ['k1', 'k2'].includes(doc.getField('changeView')),
		cPlus: doc => doc.getField('upList') !== 2,
		event: doc => doc.getField('upList') || !['k1', 'k2'].includes(doc.getField('changeView')),
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
		
		
		
		
		cmdMminus: doc => doc.util.mainList(doc, '', -1),
		cmdMplus: doc => doc.util.mainList(doc, '', 1),

		cmdOpenSess:(doc, par, ctrlKey, shift) => doc.previewNew(par, ctrlKey, shift),

		addSessionGr: (doc, p, ctrlKey) => doc.mainDoc.sova.cmd.addSessionGr(doc, p, ctrlKey),
		deleteSessionGr: (doc, p) => doc.mainDoc.sova.cmd.deleteSessionGr(doc, p),
		editSessionGr: (doc, p, ctrl) => doc.mainDoc.sova.cmd.editSessionGr(doc, p, ctrl),
		dayX: (doc, url, ctrlKey) => doc.previewNew(`newForm=v_lk_curator2&${url}`, ctrlKey),
		selectGr: doc => doc.msg.ok('Выберите группу'),
		
		cmdEdit:(doc, pk, ctrlKey, shiftKey) => {
			let view = doc.getControl('mainList');
			view.rowClick(pk);
			let page = doc.util.urlKeys(view.props.previewUrl);
			let title;
			if (doc.getField('upList') === 2) {
				page.form = 'SessionSt';
				page.dbAlias = 'nv_SessionSt';
				title = 'Редактирование события студента';
			}
			else {
				title = doc.part(doc.getField('leftList') || '')[0];
				page.title = 'Редактирование ' + title;
				page.addUrl = `&grTitle=${title}`;
			}
			page.rsMode = `edit`;
			page.unid = pk;
			doc.previewNew(page, ctrlKey, shiftKey);
		},
		// *** *** ***

		// *** *** ***
	},
	recalc: {
		CHANGEVIEW: doc => showCalendar(doc),
		PLAN: doc => showCalendar(doc),
		EVENT: doc => showCalendar(doc),
		LEFTLIST: doc => {
			let mainList = doc.getControl('mainList');
			mainList.mainDocs = [];
			for (let k in doc.register) {
				if (k.startsWith('SELONE_'))
					delete doc.register[k];
			} 
			showCalendar(doc);
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
		STATUS: (doc, value) => {
			if (doc.getField('upList') === 2) {
				doc.util.getJson(doc, `form=${doc.form}&cmd=changeLLCP&group=${doc.getField('cPlus').partition('|')[1]}&status=${value}`)
					.then( leftList => doc.changeDropList('leftList', leftList, 0))
					.catch( e => doc.msg.error(e.message) );
			}
			else
				showCalendar(doc);
		},
		FILTER: (doc, value) => {
			doc.util.getJson(doc, `form=${doc.form}&cmd=changeLL&filter=${value}`)
				.then( newList => doc.changeDropList('leftList', newList, 0))
				.catch( e => doc.msg.error(e.message) );
		},

		UPLIST: (doc, value) => {
			let ll = doc.getControl('leftList');
			ll.cn = value ? 'list3str' : 'list1str';
			ll.cnItem = `${ll.cn}Item`; // className
			doc.util.getJson(doc, `form=${doc.form}&cmd=changeUp&uplist=${value}&filter=${doc.getField('filter')}`)
				.then( newList => {
					if (value !== 2)
						doc.changeDropList('leftList', newList, 0);
					else if (newList.length) {
						let igr = doc.getControl('cPlus').sel; // getField return string: item[sel]
						doc.changeDropList('cPlus', newList, igr);
					}
				})
				.catch( e => doc.msg.error(e.message) );
		},
		CPLUS: (doc, value) => {
			doc.util.getJson(doc, `form=${doc.form}&cmd=changeLLCP&group=${value}&status=${doc.getField('status')}`)
				.then( leftList => doc.changeDropList('leftList', leftList, 0))
				.catch( e => doc.msg.error(e.message) );
		},
	}
};
