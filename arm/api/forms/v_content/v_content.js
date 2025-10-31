const showCourse = doc => {
	doc.util.getJson(doc, `form=v_content&cmd=getLectors&nve=${doc.getField('upList')}`)
		.then( sgr => { 
			doc.changeDropList('leftList', sgr, 0);

			if (doc.getField('view') !== 1)
				doc.loadView('mainList', true);
			else
				doc.util.getJson(doc, `form=v_content&cmd=showC&lector=${doc.getField('leftList')}&nve=${doc.getField('upList')}&status=${doc.getField('status')}`)
					.then( js => doc.setField('showCourse', js) )
					.catch( e => doc.msg.error(e) );
		})
		.catch( () => {});
};
			
window.sovaActions = window.sovaActions || {};
window.sovaActions.v_content = {
	init2: doc => {
			doc.util.getJson(doc, `cmd=well&clues=events`)
				.then( sgr => { 
					doc.changeDropList('upList', sgr, 0);
					showCourse(doc);
					//setTimeout(() => doc.forceUpdate(), 100);
				})
				.catch( () => {});
	},
	
	cmd: {
		cmdEdit:(doc, pk, ctrlKey, shiftKey) => {
			let view = doc.getControl('mainList');
			view.rowClick(pk);
			let page = doc.util.urlKeys(view.props.previewUrl);
			page.title = 'Редактирование шаблона';
			page.unid = pk;
			page.rsMode = 'edit';
			doc.previewNew(page, ctrlKey, shiftKey);
		},
		cmdNewCopy: (doc, sourceDoc, ctrlKey) => {
			let page = {
				rsMode: 'new',
				newForm: `SessionTmpl&sourceDoc=${sourceDoc}`,
				dbAlias: 'nv_SessionTmpl',
				title: 'Создание шаблона',
			};
			doc.previewNew(page, ctrlKey);
		},
		cmdNew: (doc, nve, ctrlKey) => {
			let page = {
				rsMode: 'new',
				newForm: `SessionTmpl&nvEvent=${nve.partition('|')[1]}`,
				dbAlias: 'nv_SessionTmpl',
				title: 'Создание шаблона',
			};
			doc.previewNew(page, ctrlKey);			
		},
	},
	// *** *** ***
	hide: {
		mainList: doc =>   doc.getField('view'),
		showCourse: doc => !doc.getField('view'),
	},
	// *** *** ***
	recalc: {
		LEFTLIST: doc => {
			if (doc.getField('view') !== 1)
				doc.loadView('mainList', true);
			else
				doc.util.getJson(doc, `form=v_content&cmd=showC&lector=${doc.getField('leftList')}&nve=${doc.getField('upList')}&status=${doc.getField('status')}`)
					.then( js => doc.setField('showCourse', js) )
					.catch( e => doc.msg.error(e) );
			
		},
		UPLIST: doc => showCourse(doc),
		VIEW: doc => {
			if (doc.getField('view') !== 1)
				doc.loadView('mainList', true);
			else
				doc.util.getJson(doc, `form=v_content&cmd=showC&lector=${doc.getField('leftList')}&nve=${doc.getField('upList')}&status=${doc.getField('status')}`)
					.then( js => doc.setField('showCourse', js) )
					.catch( e => doc.msg.error(e) );
			
		},

		STATUS: doc => showCourse(doc),

	}
};

