let _etc = ['eMovePl_etc', 'eSavePl_etc', 'noIcons_etc'];

window.sovaActions = window.sovaActions || {};
window.sovaActions.etc = {
    init2: doc => {
		let m = parseFloat(localStorage.getItem('nvScale') || 1);
		let sca = [0.5, 0.75, 0.9, 1, 1.1, 1.25, 1.5];
		if (sca.includes(m))
			doc.setField('scale_etc', sca.indexOf(m));
		else {
			doc.setField('scale_etc', 3);
			doc.mainDoc.m = 1;
			localStorage.setItem('nvScale', 1);
			doc.mainDoc.forceUpdate();
		}

		for (let it of _etc) {
			let value = localStorage.getItem(it);
			doc.setField(it, value === '0' ?  '' : value);
		}
	},
	
	recalc: {
		NOICONS_ETC: (doc, val) => doc.mainDoc.noIcons_etc = val,
		EMOVEPL_ETC: (doc, val) => doc.mainDoc.eMovePl_etc = val,
		ESAVEPL_ETC: (doc, val) => doc.mainDoc.eSavePl_etc = val,
		SCALE_ETC: (doc, val) => {
			doc.mainDoc.m = [0.5, 0.75, 0.9, 1, 1.1, 1.25, 1.5][val];
			doc.mainDoc.forceUpdate();
		},
    },
	cmd: {
		previewArm: (doc, url, ctrlKey, shift) => doc.previewNew(url, ctrlKey, shift),
		
		loadNV: doc => {
            doc.util.jsonByUrl(doc, '/api/runCmd?cmd=loadNV')
                .then( _ => doc.msg.ok('Загружено', 'Выполнение команды') )
                .catch( e => doc.msg.error(e) );
        },
        
        loadWell: doc => doc.util.jsonByUrl(doc, '/api/runCmd?cmd=loadWell')
            .then( () => doc.msg.ok('Справочники обновлены', 'Выполнение команды') )
            .catch( e => doc.msg.error(e) ),
        
        exportEmail: doc => doc.util.jsonByUrl(doc, '/api/runCmd?cmd=exportEmail')
	        .then( () => doc.msg.ok('Агент успешно запущен', 'Выполнение команды') )
	        .catch( e => doc.msg.error(e) ),


		save_etc: doc => {
			for (let it of _etc)
				localStorage.setItem(it, doc.getField(it) || '');
			localStorage.setItem('nvScale', doc.mainDoc.m);
			doc.mainDoc.msg.ok('Сохранено в локальной памяти браузера');
		},
		reset_etc: doc => {
			localStorage.clear();
			doc.mainDoc.m = 1;
			doc.setField('scale_ETC', 3);
			for (let it of _etc) {
				doc.setField(it, null);
				doc.mainDoc[it] = null;
			}
			doc.mainDoc.forceUpdate();
		},

	
	}
};

// *** *** ***












