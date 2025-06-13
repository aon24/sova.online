window.sovaActions = window.sovaActions || {};
window.sovaActions.Payment = {
	init2: doc => doc.changeDropList('purpose', `/api/well?clues=sessionTmpl_nve_band|${doc.getField('nvEvent')}`),
	cmd: {
		saved: doc => {
			if (doc.mainDoc !== doc) {
				let owner = doc.page.owner;
				if (owner.form === 'SessionSt'){
					if (doc.getField('summa'))
						owner.setField('pay_s', 1);
				}
				else {
					let view = owner.getControl('mainList') || doc.mainDoc.getControl('mainList');
					view && view.loadView(true, doc.unid);
				}
			}
		},
	},
};
