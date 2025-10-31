const _d3d = (doc, tu) => tu ? doc.box && doc.box.parent3d && doc.box.parent3d.tuning[tu] : doc.box && doc.box.parent3d;

window.sovaActions = window.sovaActions || {};
window.sovaActions.a_colors = {
	init2: doc => doc.setField('_page_', '1'),
	
    hide: {
		// сетка
		grid: doc => !doc.box || doc.box.tuning.grid !== 'set',
		
		setColorWP: doc => !doc.box || _d3d(doc) || doc.box.parentBox,
		phoneB: doc => !doc.box || _d3d(doc) || !doc.box.parentBox,

		gradient: doc => !doc.box || !doc.box.tuning.gradient,
		filter: doc => !doc.box || !doc.box.tuning.filter,
		bgColor: doc => !doc.box || doc.box.tuning.bgStyle !== 'color',
		bgImage: doc => !doc.box || doc.box.tuning.bgStyle !== 'image',

		wallsColor: doc => _d3d(doc, 'bb3d') !== 1 || !doc.box.tuning.wall,
		wallsPaperColor: doc => _d3d(doc, 'bb3d') !== 0 || doc.box.tuning.mmm !== 'rooms',
		
		// Цвет всех граней
		m3tableColor: doc => !_d3d(doc) || doc.box.tuning.m3key === 'm3empty' || !(doc.box.tuning.mmm === 'm3table' || (doc.box.tuning.wall && !doc.box.parent3d.tuning.bb3d)),
		fasadeColor: doc => !_d3d(doc) || !['m3t', 'm3brick'].includes(doc.box.tuning.m3key), // Цвет фасада
		edgeColor: doc => !_d3d(doc) || !['edge', 'm3empty'].includes(doc.box.tuning.m3key), // Цвет фасада


	},
 
	//*** *** ***

	recalc: {}, // end of recalc
	
	// ***
	
	cmd: {
		clrUrl: doc => {
			//if (doc.box.parent3d)
				//doc.box.clip.toHist(doc.box.parent3d, 'bgImage_root');
			//else
				doc.box.clip.toHist(doc.box, 'tuning', 'backgroundImage');
				doc.box.tuning.backgroundImage = '';
			doc.setField('backgroundImage', '');
			doc.box.forceUpdate();
		},
		imgFromBuf: doc => {
			navigator.clipboard.readText()
  				.then( clipText => {
					//if (doc.box.parent3d)
						//doc.box.clip.toHist(doc.box.parent3d, 'bgImage_root');
					//else
						doc.box.clip.toHist(doc.box, 'tuning', 'backgroundImage');
						doc.box.tuning.backgroundImage = clipText;
					doc.setField('backgroundImage', clipText);
					doc.box.forceUpdate();
				})
				.catch( err => console.error(err));
		},
		openImg: doc => {
			let mainDoc = doc.page.props.owner;
			let pageName = 'Pictures';
			let page = mainDoc.sovaPagesByName[pageName];
			page && page.closePage();
			let rect = doc.util.getRect(mainDoc, 80, 80);
			rect.width = Math.min(rect.width, 1200);
			let img = {
				dbAlias: 'dba',
				unid: 'unid',
				pageName,
				title: pageName,
				rsMode: 'preview',
				newForm: 'img',
				frameStyle: rect,
				modal: 1,
			}
			doc.util.addChildPage(mainDoc, img);
		},
	} // end of cmd
};
// *** *** ***

let recalcColors = window.sovaActions.a_colors.recalc;

// *** *** ***

let setColorFeature = (doc, feature, val, noHist, toHist, sl) => {
	if (doc.box && !(doc.box.tuning[feature] === val && toHist !== true)) {
		writeHist(doc.box, feature, val, noHist, sl);
		doc.box.forceUpdate();
	}
};

for (let it of colorFeatures) {
	let fi = it.split('|')[0];
	let redraw = ['bgStyle', 'gradient', 'filter'].includes(fi); // recalc  с перериcовкой settingPage (для chb/chb3)
	recalcColors[fi.toUpperCase()] = (doc, val, noHist, toHist, sl) => setColorFeature(doc, fi, val, noHist, toHist, sl) || (redraw && doc.forceUpdate());
}
for (let it of gridFeatures) {
	let fi = it.split('|')[0];
	let redraw = ['grid'].includes(fi); // recalc  с перериcовкой settingPage (для chb/chb3)
	recalcColors[fi.toUpperCase()] = (doc, val, noHist, toHist, sl) => setColorFeature(doc, fi, val, noHist, toHist, sl) || (redraw && doc.forceUpdate());
}

