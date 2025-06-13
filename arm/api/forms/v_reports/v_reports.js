// *** *** ***
let reportFields = ['module', 'title', 'firstList', 'addList', 'who', 'dt1', 'dt2', 'dt3', 'dt4', 'comment'];
var _currCat = 0;
let sheduleTimeList = doc => {
	let scheduled = doc.getField('scheduled');
	let dt = doc.getControl('schedDay');
	if (!scheduled)
		return;
	dt.setValue('');
	dt.changeDropList(`/api/well?clues=scheduled_${scheduled}_day`);
	dt = doc.getControl('schedTime');
	dt.setValue('');
	dt.changeDropList(`/api/well?clues=scheduled_${scheduled}_time`);
};


window.sovaActions = window.sovaActions || {};
window.sovaActions.v_reports = {
    init: doc => doc.setField( 'show', 'krd_0' ),
    init2: doc => sheduleTimeList(doc),

    //*** *** ***
  
    hide: {
		shedule: doc => doc.getField('show') === 'krd_0',
		dayTime: doc => !doc.getField('scheduled') || doc.getField('scheduled') === 'now',
		startReport: doc => !doc.getField('scheduled') || doc.getField('scheduled') !== 'now',
		rep: doc => doc.getField('db'),
		sched: doc => !doc.getField('db'),
		db0: doc => doc.getField('db') != 0,
		db1: doc => doc.getField('db') != 1,
		db2: doc => doc.getField('db') != 2,
		newLM: doc => doc.getField('db') != 2 || doc.getField('agentView') != 0,
	},
    //*** *** ***
  
    recalc: {
		EXPAND: (doc, val) => {
			let v = doc.getControl('mainList');
			v.expandChange = val ? '+' : '-';
			v.forceUpdate();
			setTimeout(() => {v.expandChange = null; v.forceUpdate()}, 1);
		},
		SCHEDULED: doc => sheduleTimeList(doc),
        TITLE: (doc, label, opt, i) => {
        	_currCat = i;
            doc.setField( 'show', `krd_${i}` );
            doc.loadView('mainList', true);
            doc.forceUpdate();
        },
        AGENTVIEW: doc => doc.loadView('mainList', true),
        STATUS: doc => doc.loadView('mainList', true),
        CATEGORY: doc => doc.loadView('mainList', true),
        DB: doc => {
			doc.loadView('mainList', true);
			doc.forceUpdate();
		},
		
    },
    
    currCat: 0,
  
    cmd: {
		cmdNew: doc => {
			let page = {
				rsMode: 'new',
				newForm: 'Module',
				dbAlias: 'nv_lm_Module',
				title: 'Новый модуль',
			};
			doc.previewNew(page);
		},


		refClick: (doc, unid, ctrlKey, shiftKey) => {
			let dba = doc.getField('db') == 2 ? 'nv_lm_Module' : 'nv_reports_Report';
			let page = {
				unid: unid,
				dbAlias: dba,
				title: 'Отчет',
				rsMode: 'read',
				form: 'html',
			};
			doc.previewNew(page, ctrlKey, shiftKey);
		},
		
        p2: (doc, i) => {
            let dt = doc.getField('dt1_' + i);
            if (dt) {
                let dti = +dt.slice(0,4) - 1;
                doc.setField('dt3_' + i, '' + dti + dt.slice(4));
            }
            dt = doc.getField('dt2_' + i);
            if (dt) {
                let dti = +dt.slice(0,4) - 1;
                doc.setField('dt4_' + i, '' + dti + dt.slice(4));
            }
        },
        
        startReport: doc => {
			let i = doc.util.partition(doc.getField('show'), '_')[1];
            let act = `title=${doc.getField('title')}`;

			for(let it of ['scheduled', 'schedTime', 'schedDay', 'domain'])
				act += `&${it}=${doc.getField(it)}`;

			for(let it of reportFields) {
				let fi = `${it}_${i}`;
				act += `&report_${it}=${doc.getField(fi)}`;
			}

			doc.util.serverAction(doc, `putData?form=v_reports&cmd=startReport`, act)
				.then( res => res === 'OK' ?
					doc.msg.box('Агент успешно запущен', 'Запуск сбора отчета')
					:
					doc.msg.error(res)
				)
				.catch(err => console.error(err));
        },

        
        scheduleReport: doc => {
			let i = doc.util.partition(doc.getField('show'), '_')[1];
            let act = `title=${doc.getField('title')}`;

			for(let it of ['scheduled', 'schedTime', 'schedDay', 'domain'])
				act += `&${it}=${doc.getField(it)}`;

			for(let it of reportFields) {
				let fi = `${it}_${i}`;
				act += `&report_${it}=${doc.getField(fi)}`;
			}

			doc.util.serverAction(doc, `putData?form=v_reports&cmd=scheduleReport`, act)
				.then( res => res === 'OK' ?
					doc.msg.box('Отчет добавлен в расписание', 'Сбор отчета по расписанию')
					:
					doc.msg.error(res)
				)
				.catch(err => console.error(err));
        },
        

     	setQuar: (doc, dt1_dt2) => {
     		let [dt1, dt2] = doc.util.partition(dt1_dt2, '|');
     		doc.setField('dt1_' + _currCat, dt1);
     		doc.setField('dt2_' + _currCat, dt2);
     	},
		cmdEdit:(doc, par, ctrlKey, shiftKey) => {
			let page = doc.util.urlKeys(par);
			let view = doc.getControl('mainList');
			view.rowClick(page.unid);
			page.title = 'Редактирование';
			page.rsMode = 'edit';
			doc.previewNew(page, ctrlKey, shiftKey);
		},

//		search: doc => doc.getControl('mainList').search(doc.getField('search')),
//		reset: doc => doc.setField('search', '') || doc.getControl('mainList').search(''),

    },
};

// *** *** ***

// т.о. формируется 20 условий скрытия { krd_0: doc => doc.getField('show') != 'krd_0', ...
for ( let i = 0; i < 20; i++ )
    window.sovaActions.v_reports.hide[`krd_${i}`] = doc => doc.getField('show') !== `krd_${i}`;













