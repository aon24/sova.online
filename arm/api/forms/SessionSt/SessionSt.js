window.sovaActions = window.sovaActions || {};
window.sovaActions.SessionSt = {
	init: doc => {
		doc.videoList = JSON.parse(doc.getField('VIDEOLIST_FD') || '[]');
		doc.videoList.sort((a, b) => (a.name || '') > (b.name || '') ? 1 : -1);
		for (let i=0; i < 10; i++) {
			doc.sova.hide[`UM_Table_FD_${i}`] = doc => i !== doc.getField('UM_Table_FD');
			doc.sova.hide[`sst_Table_FD_${i}`] = doc => i !== doc.getField('sst_Table_FD');
		}
	},
	
	cmd: {
		newPay: (doc, par, ctrl, shiftKey) => {
			let page = {
				addUrl: [
					`&sgrId=${doc.getField('SESSIONGR_ID')}`,
					`profile=${doc.getField('PREF')}`,
				].join('&'),
				rsMode: 'new',
				newForm: 'Payment',
				dbAlias: 'nv_Payment',
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
				doc.util.xopen(`/api/new?form=v_payments&dbAlias=nv_Payment&mode=read&profile=${doc.getField('pref')}`);
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
		SST_TABLE_FD: doc => doc.forceUpdate(),
	},
	readOnly: {
		student: doc => doc.getField('STUDENT_FD'),
	},
	hide: {
		job1: doc => !doc.getField('job1'),
		job2: doc => !doc.getField('job2'),
		job3: doc => !doc.getField('job3'),
		job4: doc => !doc.getField('job4'),
		job5: doc => !doc.getField('job5'),
		video: doc => !doc.getField('videoList_FD'),
		ass: doc => doc.getField('noAss_fd'),
		delGr: doc => !doc.getField('other_group_FD') || doc.getField('STUDENT_FD'),
		chGr: doc =>   doc.getField('other_group_FD') || doc.getField('STUDENT_FD'),
		chGrTx: doc =>  !doc.getField('STUDENT_FD'),
		adminOnly: doc =>  doc.getField('STUDENT_FD'),
		href: doc => !doc.getControl('href') || (!doc.getField('href') && doc.getControl('href').props.readOnly),
		mtx: doc => !doc.getControl('mtx') || (!doc.getField('mtx') && doc.getControl('mtx').props.readOnly),
		other: doc => !doc.getField('owner'),
		owner: doc => doc.getField('owner'),
		semester: doc => !doc.getControl('semester') || (!doc.getField('semester') && doc.getControl('semester').props.readOnly),

	},
};

