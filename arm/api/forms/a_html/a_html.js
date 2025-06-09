window._rsOpen = (pageName, title) => {
	let page = {
		dbAlias: 'draft',
		title: title || 'О системе',
		addUrl: `&page=${pageName}`,
		rsMode: 'read',
		pageName: `a_html-${pageName}`,
	};

	window._rsDoc.previewNew(page);
};

window.sovaActions = window.sovaActions || {};
window.sovaActions.a_html = {
    init2: doc => window._rsDoc = doc.mainDoc,
    
	recalc: {},
	hide: {
		href: doc => !doc.getField('href') && doc.readOnly,
		mtx: doc => !doc.getField('mtx') && doc.readOnly,
		mtxLabel: doc => doc.readOnly,
	},
};