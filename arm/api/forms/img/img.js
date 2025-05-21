// *** *** ***
//
// aon 2022
//
// *** *** ***

window.sovaActions = window.sovaActions || {};
window.sovaActions.img = {
	init2: doc => {
		if (!doc._first) {
			doc.page.dom.current.addEventListener('dragover', e => e.preventDefault());
			doc.page.dom.current.addEventListener('drop', e => window.sovaActions.img.cmd.addFiles(doc, null, e));
			doc._first = true;
			doc.page.forceUpdate();

			let url=`/api/getData?form=${doc.form}&cmd=getFormDir`;
			fetch(url, {method: 'get', credentials: 'include'})
				.then( response => response.text())
				.then( formDir => doc.formDir = formDir)
				.catch( err => doc.msg.error(err.message, 'getFormDir-error:'));
		}

	},
	cmd: {
		btnFiles: () => {
			let el = document.getElementById('inputBgFiles');
			if (el)
				el.click();
		},
		addFiles: (doc, p, e) => {
			e.preventDefault();
			let files = e.dataTransfer?.files || e.target.files;
			let items = e.dataTransfer?.items;
			if (!files && !(items && items[0] && items[0].kind === 'file'))
				return;

			let f = files[0];

	doc.msg.box(`Загрузить файл ${f.name} на сервер?\nsize ${f.size}(${f.type})`, 'Upload')
		.then(() => {
			//if (!f.size)
			//	return doc.msg.ok('Нельзя загрузить файл нулевой длины');

			let formData = new FormData();
			formData.append('bgFile', f);
			
			let par = {
	            method: 'post',
				credentials: 'include',
				body: formData,
			};

	        let csrftoken = doc.util.getCookie('csrftoken');
	        if (csrftoken)
	            par.headers = {'X-CSRFToken': csrftoken};

			let path = doc.formDir ?
				`${doc.formDir}/${doc._path || ''}`
				: 
				doc._path || '';


			let url = `/api/upload?path=${path}`;

			doc.waitLoad = true;
			setTimeout( () => doc.waitLoad && doc.setState({spinner: true}), 500 );

			if (e.target.tagName === 'INPUT')
				e.target.value = '';
		
			fetch(url, par)
				.then( response => response.text())
				.then( text => {
					doc.waitLoad = false;
					doc.setState({spinner: false});
					text !== 'OK' ?
						doc.msg.error(text)
						:
						window.sovaActions.img.cmd.chDir(doc);
				})
				.catch( err => {
					doc.waitLoad = false;
					doc.setState({spinner: false});
					doc.msg.error(err.message, 'Util.doPost-error:');
				});
			})
			.catch(()=>{})
		},

		// ***
		
		oneImg: (doc, img) => {
			let colorPage = doc.mainDoc.sovaPagesByName['settingColors'];
			if (colorPage) {
				let docSP = colorPage.doc;
				let box = docSP.box;
	
				docSP.setField('backgroundImage', img);
				//box.clip.toHist(box, 'tuning', 'backgroundImage');
			}
			else if (doc.fieldValues['VL']) {
				let i = parseInt(doc.fieldValues['VL'], 10);
				let owner = doc.page.owner;
				owner.videoList[i]['image'] = img;
				owner.setField(`vl${i}_image`, img);
				owner.getControl('videoGrid').forceUpdate();
			}
			else {
				let owner = doc.page.owner;
				owner.setField('sticker', img);
				let jsn = [{_teg: 'div', attributes: {style: {
					width:260, 
					height:160, 
					backgroundSize:'100% 100%', 
					backgroundImage:`url('${img}')`,
				}}}];
				owner.setField('stickerImg', jsn);
			}
			doc.page.closePage();
		},
		
		chDir: (doc, path) => {
			doc._path = path;
			
		    let url = `/api/newForm?form=img&list=${doc.getField('list')}&subDir=${path}&vl=${doc.getField('VL')}`;
		    doc.util.jsonByUrl(doc, url)
		        .then( jsn => {
		            doc.setDocProps(jsn);
		            return jsn && jsn.urlForm ? doc.util.jsonByUrl(doc, jsn.urlForm) : null;
		        })
		        .then( page => {
		            doc.register = {};
		            doc.init2 = false;
		            doc.loadForm(page);
		            doc.page.title = `${doc.page.pageName}: ${doc._path}`;
		         })
		        .catch( err => doc.msg.error(err) );
		},
	},
	recalc: {
		BTNLIST: (doc, val) => {
			let url = `/api/newForm?form=img&list=${val}&subDir=${doc._path}&vl=${doc.getField('VL')}`;
		    doc.util.jsonByUrl(doc, url)
		        .then( jsn => {
		            doc.setDocProps(jsn);
		            return jsn && jsn.urlForm ? doc.util.jsonByUrl(doc, jsn.urlForm) : null;
		        })
		        .then( page => {
		            doc.register = {};
		            doc.init2 = false;
		            doc.loadForm(page);
		            doc.page.title = `${doc.page.pageName}: ${doc._path || ''}`;
		         })
		        .catch( err => doc.msg.error(err) );
		},
	}
};