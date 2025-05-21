window.sovaActions = window.sovaActions || {};
window.sovaActions.Profile = {
	init: doc => {
		for (let i=0; i < 10; i++)
			doc.sova.hide[`PR_Table_FD_${i}`] = doc => i !== doc.getField('PR_Table_FD');
	},
	init2: doc => {
		let ls;
		ls = doc.getField('tls_fd').split('\n');
		doc.changeDropList('training', ls);
		ls = doc.getField('fls_fd').split('\n');
		doc.changeDropList('fest', ls);
		ls = doc.getField('ils_fd').split('\n');
		doc.changeDropList('invite', ls);
	},
	cmd: {
		saved: doc => {
			if (doc.mainDoc !== doc) {
				let view = doc.page.owner.getControl('mainList') || doc.mainDoc.getControl('mainList');
				view && view.loadView(true, doc.unid);
			}
		},
		forceUpdate: doc => doc.forceUpdate(),

		payList: (doc, p, ctrl, shiftKey) => {
			if (!ctrl) {
				let page = {
					newForm: 'v_payments',
					unid: '1',
					dbAlias: 'nv_Payment',
					title: 'Платежи',
					addUrl: `&profile=${doc.getField('id')}`
				};
				doc.previewNew(page, ctrl, shiftKey);
			}
			else
				doc.util.xopen(`/api/new?form=v_payments&dbAlias=nv_Payment&mode=read&profile=${doc.getField('profile')}`);
		},
		
	},
	// *** *** ***
	
	recalc: {
		PR_TABLE_FD: doc => doc.forceUpdate(),
	},	
	hide: {
		createUser: doc => doc.getField('username'),
		changeUser: doc => !doc.getField('username'),
		cur_gr: doc => !doc.getField('role').includes('куратор'),
		// lec_gr: doc => !doc.getField('role').includes('преподаватель'),
	},
	validate: {
	        full_name: doc => doc.getField('full_name') ? '' : 'ФИО',
	        role: doc => doc.getField('role') ? '' : 'Роль',
	},
};


	
	
	