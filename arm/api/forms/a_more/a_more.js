window.sovaActions = window.sovaActions || {};
window.sovaActions.a_more = {
	cmd: {},
	recalc: {},
	hide: {
		href: doc => !doc.getField('href') && doc.readOnly,
		mtx: doc => !doc.getField('mtx') && doc.readOnly,
		mtxLabel: doc => doc.readOnly,
	},
};