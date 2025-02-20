
window.sovaActions = window.sovaActions || {};
window.sovaActions.SessionSt = {
	init: doc => {
		doc.videoList = JSON.parse(doc.fieldValues.VIDEOLIST || '[]');
		doc.videoList.sort((a, b) => (a.name || '') > (b.name || '') ? 1 : -1);
		doc.fieldValues.VIDEOLIST = null;
	},
	
	cmd: {
		newPay: (doc, par, ctrl, shiftKey) => {
			let page = {
				addUrl: [
					`&sstId=${doc.fieldValues['ID']}`,
					`t1=${doc.getField('DATE_BEGIN')}`,
					`nvEvent=${doc.fieldValues['NVEVENT']}`,
					`purpose=${doc.getField('title')}`,
					`group=${doc.getField('nvgroup_fd')}`,
					`profile=${doc.getField('PREF')}`,
				].join('&'),
				rsMode: 'new',
				newForm: 'Payment',
				dbAlias: 'nv_Payment',
				unid: 'new',
				title: 'Новый платеж',
			};
			doc.previewNew(page, ctrl, shiftKey);
		},

		payList: (doc, p, ctrl, shiftKey) => {
			if (!ctrl) {
				let page = {
					newForm: 'v_payments',
					unid: '1',
					dbAlias: 'nv_Payment',
					title: 'Платежи',
					addUrl: `&profile=${doc.getField('pref')}`
				};
				doc.previewNew(page, ctrl, shiftKey);
			}
			else
				doc.util.xopen(`/api/new?form=v_payments&dbAlias=nv_Payment&unid=1&mode=read&profile=${doc.getField('pref')}`);
		},
		
		saved: doc => {
			if (doc.mainDoc !== doc) {
				let parentDoc = doc.page.owner;
				let view = parentDoc.getControl('mainList3') || parentDoc.getControl('mainList')
	    		view && view.loadView(true, doc.unid);
			}
		},


		changeGroup: doc => {
			let url = `/api/well?clues=allGroups`;
			doc.util.jsonByUrl(doc, url)
				.then( jsn => {
					let items = jsn || [];
					doc.msg.list(items, 'Выберите группу')
						.then(it => {
							if (it) {
								let [ofd, oid] = doc.util.partition(it, '|')
								doc.setField('other_group_FD', ofd);
								doc.setField('other_group', oid);
								setTimeout(() => doc.forceUpdate(), 1);
							}
						})
						.catch( () => {});
				})
				.catch( () => {})
		},
		
		delGroup: doc => {
			doc.setField('other_group_FD', '');
			doc.setField('other_group', '');
			setTimeout(() => doc.forceUpdate(), 1);
		},

		
		forceUpdate: doc => doc.forceUpdate(),
	},
	recalc: {
	},
	readOnly: {
		student: doc => doc.fieldValues['STUDENT_FD'],
	},
	hide: {
		ass: doc => doc.getField('noAss_fd'),
		delGr: doc => !doc.getField('other_group_FD') || doc.fieldValues['STUDENT_FD'],
		chGr: doc =>   doc.getField('other_group_FD') || doc.fieldValues['STUDENT_FD'],
		chGrTx: doc =>  !doc.fieldValues['STUDENT_FD'],
		adminOnly: doc =>  doc.fieldValues['STUDENT_FD'],
		href: doc => !doc.getControl('href') || (!doc.getField('href') && doc.getControl('href').props.readOnly),
		mtx: doc => !doc.getControl('mtx') || (!doc.getField('mtx') && doc.getControl('mtx').props.readOnly),
		other: doc => !doc.getField('owner'),
		owner: doc => doc.getField('owner'),
		semester: doc => !doc.getControl('semester') || (!doc.getField('semester') && doc.getControl('semester').props.readOnly),

	},
};

