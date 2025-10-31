let Util;

// *** *** ***

let getEdges = doc => {};
let getEdgesCL = (doc, shiftMonth) => {
    let view = doc.getField('changeViewCL'); // k1/эскизы/список
    let dateZ = document.getElementById('dateZ_CL');
    dateZ = dateZ && dateZ.innerHTML;
    dateZ = dateZ ? `&dateZ=${dateZ}` : '';
    shiftMonth = shiftMonth ? `&shiftMonth=${shiftMonth}` : '';

    let filter = doc.sovaPagesByName['arm_filter'].doc;
    let choosing  = filter.getField('scheduleChoosing');
    doc.setField('choosing', choosing); // for mainListCL
    
    let url = `form=arm&cmd=showCL&${shiftMonth}${dateZ}&view=${view}&choosing=${choosing}`;


    for (let k in filter.register) {
        if (k.startsWith('FILTER') && k.endsWith('CL')) {
            doc.setField(k, filter.getField(k)); // копируем фильтры в гл.док, чтобы mainListCL отработал
            if (filter.getField(k))
                url += `&${k}=${filter.getField(k)}`;
        }
    }

    let par;
    // scheduleChoosing: 'Полное|All','Куратор|C', 'Преподаватель|L', 'Сотрудник|S'
    switch(choosing) { // val: 'Полное|All','Куратор|C', 'Преподаватель|L', 'Сотрудник|S'
       case 'C':
           url += `&groupC=${doc.getField('groupC')}`;
           doc.setField('group', doc.getField('groupC'));
           break;
       case 'L':
           url += `&groupL=${doc.getField('groupL')}`;
           doc.setField('group', doc.getField('groupL'));
           break;
       case 'S':
           url += `&groupS=${doc.getField('groupS')}`;
           doc.setField('group', doc.getField('groupS'));
           break;
       default: // scheduleChoosing === 'All';
           url += `&groupC=${doc.getField('groupC')}`;
           url += `&groupL=${doc.getField('groupL')}`;
           url += `&groupS=${doc.getField('groupS')}`;
	}

    if (view === 'l') { // list
        return doc.loadView('mainListCL', true);
    }

    Util.getJson(doc, url) // calendar or icons
        .then( js => {
            doc.setField('showCourseCL', js); // в поле showCourse хранятся эскизы
            doc.forceUpdate();
        })
        .catch( e => doc.msg.error(e) );
};

// *** *** ***

const scale_etc = [0.75, 0.9, 1, 1.1, 1.25];


window.sovaActions = window.sovaActions || {};
window.sovaActions.arm = {
    init: doc => {
		Util = doc.util;
		let m = parseFloat(localStorage.getItem('nvScale') || 1);
	        doc.m = scale_etc.includes(m) ? m : 1;

		for (let it of ['eMovePl_etc', 'eSavePl_etc', 'noIcons_etc']) {
			doc[it] = localStorage.getItem(it);
		}
		doc.tabNewHide('lks_Table_FD'); // Расписание-ЛК-Контакты (student)

		let filters = {
			hide: true, // при закрытии не удалять, а скрывать
			dbAlias: 'dba',
			unid: 'unid',
			pageName: 'arm_filter',
			rsMode: 'new',
			noCls: true,
			fix: true,
			newForm: `arm_filter`,
			title: 'Фильтры',
			frameStyle: {width: 180, top: 0, right:0, display: 'none'}
		};
		Util.addChildPage(doc, filters);
    },
    init2: doc => {
		doc.setField('scale_etc', scale_etc.indexOf(doc.m));

		// curator *** *** ***
        let jsn = JSON.parse(doc.getField('curatorGroups') || '[[],[]]');
        doc.changeDropList('groupC', jsn[0], 0); // Все + список групп (для расписания)
        doc.changeDropList('groupCforOpen', jsn[1], 0); // список групп (для открытия окна группы)

		// lector *** *** ***
        let lectorGroups = JSON.parse(doc.getField('lectorGroups') || '[]');
		doc.changeDropList('groupL', lectorGroups);

		// student or worker *** *** ***
        let workerGroups = JSON.parse(doc.getField('workerGroups') || '[]');
        doc.changeDropList('groupS', workerGroups);
    },

	// *** *** ***

	hide: {
        filterGrBtn: doc => !doc.getField('showFilterGr'),
        groupBtnL: doc => !['All', 'L'].includes(doc.getField('choosing')),
        groupBtnC: doc => !['All', 'C'].includes(doc.getField('choosing')),
        groupBtnS: doc => !['All', 'S'].includes(doc.getField('choosing')),

		paymentsList: doc => !doc.getField('payments'),

		mainList3: doc => doc.getField('changeView3') !== 'l',
		showCL3: doc => doc.getField('changeView3') === 'l',

        mainListCL: doc => doc.getField('changeViewCL') !== 'l',
        showCL: doc => doc.getField('changeViewCL') === 'l',
	},

    recalc: {
        SHOWFILTERGR: doc => doc.forceUpdate(),
        PAYMENTS: (doc, val) => {
			let showLK_id = doc.getField('showLK_id');
			if(val) {
	            Util.getJson(doc, `form=arm&cmd=getTable&table=payments&showLK_id=${showLK_id}`)
	                .then( js => {
	                    doc.setField('paymentsList', js);
	                    doc.forceUpdate();
	                })
	                .catch( e => doc.msg.error(e) );
			}
			else
				doc.forceUpdate();
        },

		SCALE_ETC: (doc, val) => {
			doc.m = scale_etc[val];
			doc.forceUpdate();
		},

		CHANGEVIEWCL: doc => getEdgesCL(doc),
        CHANGEVIEW3: doc => getEdges(doc),


		GROUPCFOROPEN: (doc, par, ctrlKey) => { // gr of lector
			// открывает окно "список сессий"
			let [grn, grId] = par.partition();
            let page = Util.urlKeys(par);
            page.newForm = 'v_lk_curator';
            page.title = grn;
            page.unid = grId;
            page.addUrl = `&group=${grn}`;
			doc.previewNew(page, ctrlKey);
		},

        GROUPC: doc => getEdgesCL(doc) || doc.forceUpdate(),
        GROUPL: doc => getEdgesCL(doc) || doc.forceUpdate(),
        GROUPS: doc => getEdgesCL(doc) || doc.forceUpdate(),
	},

	// *** *** ***

    cmd: {
		reportGr: (doc, ctrl) => {
            let page = {
				newForm: 'arm_review',
				addUrl: `&nvGroup=${doc.getField('groupC')}`,
				title: `Сводки по группе ${doc.getField('groupC', true)}`,
				rsMode: 'edit',
			}
            doc.previewNew(page, ctrl);
		},
        reportSt: (doc, ctrl) => {
            let page = {
                newForm: 'arm_review',
                addUrl: `&nvGroup=${doc.getField('groupC')}&studentMode=1`,
                title: `Сводки по группе ${doc.getField('groupC', true)}`,
                rsMode: 'edit',
            }
            doc.previewNew(page, ctrl);
        },
		showFilter: doc => {
			let page = doc.mainDoc.sovaPagesByName['arm_filter'];
			page.frameStyle.display = 'block';
			page.forceUpdate();
		},
		hideFilter: doc => {
			if (doc.getField('lks_Table_FD')) {
				let page = doc.mainDoc.sovaPagesByName['arm_filter'];
				page.frameStyle.display = 'none';
				page.forceUpdate();
			}
		},

        addFeedback: doc => {
			doc.inputBox('Отзывы модерируюся', '', 'Отзыв', '', ['Отправить|FV'])
				.then(buf => {
					let body = JSON.stringify(['form=a_more&cmd=addFeedback', buf]);
					buf && doc.util.getJson(doc, body, true)
						.then( res => {
							doc.msg.ok('Он будет опуликован в течении 24 часов.', 'Отзыв отправлен|Спасибо за отзыв.')
						})
		            	.catch(() => doc.msg.error('Отзывы могут отправлять только зарегистрированные пользователи'));
				})
				.catch({});
		},

        deleteSessionGr: (doc, par) => { // call from calendar or ecsquse
            let [pk, tx] = par.partition('|'); // id|text'
            let view = doc.getControl('mainListCL');
            if (view) {
				view.selectedDoc = pk;
				view.forceUpdate();
			}
			
			doc.msg.box(`${tx}`, 'Удаление|Удалить выбранный документ?', ['Да+|Y', 'Нет'])
				.then( () => {
					Util.getJson(doc, `cmd=deleteFromDB&unid=${pk}&dbAlias=nv_SessionGr`, true)
						.then( res => {
							if (res === 'OK')
								getEdgesCL(doc);
							else
								doc.msg.error(res);
						})
						.catch(() => {}); // у промиса getJson свой errBox
				})
				.catch(() => {});
		},
		
		// ***
		
        editSessionGr: (doc, par, ctrl) => {
            let [unid, title] = par.partition('|');
            let page = {unid, title, rsMode: 'edit', dbAlias: 'nv_SessionGr'};
            doc.previewNew(page, ctrl);
        },
		dayX: (doc, url, ctrlKey) => doc.previewNew(`newForm=v_lk_curator2&${url}`, ctrlKey),

        selectGr: doc => doc.msg.ok('Выберите группу'),
        manyEvent: doc => doc.msg.ok('Несколько событий в день.\nДоступ к событиям из эскизов или списка.'),

		cmdMminusCL: doc => getEdgesCL(doc, -1),
		cmdMplusCL: doc => getEdgesCL(doc, 1),

        addSessionGr: (doc, p, ctrlKey) => {
            let [nvgroup, date_begin, nve] = p.split('|'); // nve: sess-lection-trening-practic-cl
			let url = `form=arm&cmd=getSessTemplList&nve=${nve}`;
			Util.getJson(doc, url)
				.then( jsn => {
					let items = jsn || [];
					doc.msg.list(items, 'Выберите нужное')
						.then(it => {
							if (it) {
								let tmplId = it.partition()[1];
								let page = {
									rsMode: 'new',
									newForm: 'SessionGr',
									addUrl: `&tmplId=${tmplId}&nvgroup=${nvgroup}&date_begin=${date_begin}`,
									dbAlias: 'nv_SessionGr',
									title: 'Добавить в расписание группы',
								};
								doc.previewNew(page, ctrlKey);
							}
						})
						.catch( () => null );
				})
				.catch( () => {});
		},

		// ***

		openSSt:(doc, par, ctrlKey) => {
			let page = Util.urlKeys(par);
			page.rsMode = 'edit';
			doc.previewNew(page, ctrlKey);
		},
		// *** *** ***
        openProfile: (doc, noProf, ctrlKey, shift) => {
			// self-profile
            if (noProf)
                return doc.msg.ok('Профайл не создан');

			let page = {title: 'Профайл', rsMode: 'edit', form: 'Profile', dbAlias: 'nv_Profile'};
			doc.previewNew(page, ctrlKey, shift);
		},
		// *** *** ***

		cmdEdit:(doc, pageParam, ctrlKey, shift) => {
			let page = Util.urlKeys(pageParam);
            let view = doc.getControl('mainListCL');
            if (view) {
				view.selectedDoc = page.unid;
				view.forceUpdate();
			}
			page.rsMode = 'edit';
			doc.previewNew(page, ctrlKey, shift);
		},
		cmdEdit3:(doc, pageParam, ctrlKey, shift) => {
			let page = Util.urlKeys(pageParam);
            let view = doc.getControl('mainListCL');
            if (view) {
				view.selectedDoc = page.unid;
				view.forceUpdate();
			}
			page.rsMode = 'edit';
			doc.previewNew(page, ctrlKey, shift);
		},
        cmdRead:(doc, pageParam, ctrlKey, shift) => { // для лектора в лк
			let page = Util.urlKeys(pageParam);
            let view = doc.getControl('mainListCL');
            if (view) {
				view.selectedDoc = page.unid;
				view.forceUpdate();
			}
			page.rsMode = 'read';
			doc.previewNew(page, ctrlKey, shift);
		},

		// *** *** ***
		cmdOpenSess:(doc, par, ctrlKey, shift) => doc.previewNew(par, ctrlKey, shift),
		// *** *** ***

	},
};
