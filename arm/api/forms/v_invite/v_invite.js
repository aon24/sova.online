window.sovaActions = window.sovaActions || {};
window.sovaActions.v_invite = {
	init2: doc => {
		let more = doc.getField('upList').partition()[1]
		doc.util.jsonByUrl(doc, `/api/getData?form=${doc.form}&cmd=changeUp&uplist=${more}`)
			.then( newList => doc.changeDropList('leftList', newList, 0))
			.catch( e => {} );
		},

	// *** *** ***
	hide: {},
	// *** *** ***
	
	cmd: {
		cmdNewPay: (doc, pk) => {
			let view = doc.getControl('mainList');
			view.rowClick(pk);
			let page = {
				rsMode: `new`,
				newForm: `Payment&profile=${pk}`,
				dbAlias: 'nv_Payment',
				title: 'Новый платеж',
			};
			doc.previewNew(page);
		},
		cmdNew: doc => {
			let page = {
				rsMode: 'new',
				newForm: `Profile`,
				dbAlias: 'nv_Profile',
				title: 'Новый пользователь',
			};
			doc.previewNew(page);
		},
		cmdEdit:(doc, pk, ctrlKey, shiftKey) => {
			let view = doc.getControl('mainList');
			view.rowClick(pk);
			let page = doc.util.urlKeys(view.props.previewUrl);
			page.title = 'Редактирование ' + doc.getField('leftList');
			page.unid = pk;
			page.rsMode = 'edit';
			doc.previewNew(page, ctrlKey, shiftKey);
		},
		search: doc => doc.getControl('mainList').search(doc.getField('search')),
		reset: doc => {
			doc.setField('search', '');
			doc.getControl('mainList').search('');
		},
		// *** *** ***
	},
	recalc: {
		STATUS: doc => doc.loadView('mainList', true),
		LEFTLIST: doc => doc.loadView('mainList', true),

		UPLIST: (doc, more) => {
			more = more.partition()[1]
			doc.util.jsonByUrl(doc, `/api/getData?form=${doc.form}&cmd=changeUp&uplist=${more}`)
				.then( newList => doc.changeDropList('leftList', newList, 0))
				.catch( e => {} );
		},
	}
};
