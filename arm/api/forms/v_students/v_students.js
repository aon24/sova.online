window.sovaActions = window.sovaActions || {};
window.sovaActions.v_students = {
	// *** *** ***
	init2: doc => window.sovaActions.v_students.recalc.UPLIST(doc,0),	
	cmd: {
		cmdNew: doc => {
			let page = {
				rsMode: 'new',
				newForm: `Profile`,
				dbAlias: 'nv_Profile',
				title: 'Новый пользователь',
				addUrl: `&group=${doc.getField('leftList')}`,
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
		// *** *** ***

	},
	recalc: {
		UPLIST: (doc, i) => {
	        doc.util.jsonByUrl(doc, `/api/getData?form=v_students&cmd=getGroups&status=${i}`)
	            .then( js => {
					doc.changeDropList('LEFTLIST', js);
					doc.loadView('mainList', true);
	            })
	            .catch( e => doc.msg.error(e) );
		},
		LEFTLIST: doc => doc.loadView('mainList', true),

	}
};
