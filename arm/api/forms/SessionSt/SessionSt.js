window.sovaActions = window.sovaActions || {};
window.sovaActions.SessionSt = {
	init: doc => {
		doc.videoList = JSON.parse(doc.getField('VIDEOLIST_FD') || '[]');
		doc.videoList.sort((a, b) => `${a.name||''}-${a.url||''}` > `${b.name||''}-${b.url||''}` ? 1 : -1);
		for (let i=0; i < 10; i++) {
// не исп.	doc.sova.hide[`UM_Table_FD_${i}`] = doc => i !== doc.getField('UM_Table_FD');
//			doc.sova.hide[`sst_Table_FD_${i}`] = doc => i !== doc.getField('sst_Table_FD');
			doc.sova.hide[`job1${i+1}`] = doc => !doc.getField(`job1${i+1}`);
		}
	}
	,
	init2: doc => {
		// учебные материалы будут удалены, если doc.mtx == '' and doc.videoList_FD == ''
		let ii = 0;
		if (!doc.getField('student_FD')) // форму открыл курато, у него "И" сначала
			ii = 1;
			
		let mainTabs = doc.getControl('sst_Table_FD');
		let items = [...mainTabs.items];
		if (!doc.getField('mtx') && !doc.getField('videoList_FD'))
			items[ii] = null; // учебные материалы
			
		// задания будут удалены, если все doc.job{i} == '' (i: 1-10)
		let ever;
		for (let i=1; i <= 10; i++)
			ever = ever || doc.getField(`job${i}`);
		if (!ever)
			items[ii+1] = null; // задания

		if (doc.getField('hideAss_FD'))
			items[ii+2] = null; // обратная связь

		mainTabs.items = [];
		
		let newInd = 0;
		for (let i=0; i < items.length; i++) {
			if (items[i]) {
				mainTabs.items.push(items[i]);
				// name -остались старые, скрывать надо по новому
				let k = newInd;
				doc.sova.hide[`sst_Table_FD_${i}`] = doc => k !== doc.getField('sst_Table_FD');
				newInd++;
			}
			else
				doc.sova.hide[`sst_Table_FD_${i}`] = doc => true;
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
                let view = parentDoc.getControl('mainList3') || parentDoc.getControl('mainList');
                view && view.loadView(true, doc.unid);
                view = parentDoc.getControl('mainListCL');
                view && view.loadView(true, doc.unid);
	    		// for Cube:
	    		parentDoc.getControl('cube') && getEdges(parentDoc, '', 'e');
	    		parentDoc.sovaPagesByName['arm_filter'] && getEdgesCL(parentDoc);
			}
		},


		changeGroup: doc => {
			doc.util.getJson(doc, 'cmd=well&clues=allGroups')
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
		HIDES: doc => doc.forceUpdate(),
		SST_TABLE_FD: doc => doc.forceUpdate(),
	},
	readOnly: {
		student: doc => doc.getField('STUDENT_FD'),
	},
	hide: {
		mtx: doc => !doc.getField('mtx'),
		rtf: doc => doc.getField('hides') !== 'rtf',
		text: doc => !doc.getField('text'),
		video: doc => !doc.getField('videoList_FD'),
		href: doc => !doc.getField('href'),
		
		ass: doc => doc.getField('noAss_fd'),
		delGr: doc => !doc.getField('other_group_FD') || doc.getField('STUDENT_FD'),
		chGr: doc =>   doc.getField('other_group_FD') || doc.getField('STUDENT_FD'),
		chGrTx: doc =>  !doc.getField('STUDENT_FD'),
		adminOnly: doc =>  doc.getField('STUDENT_FD'),
		other: doc => !doc.getField('owner'),
		owner: doc => doc.getField('owner'),
		semester: doc => !doc.getControl('semester') || (!doc.getField('semester') && doc.getControl('semester').props.readOnly),

	},
};

