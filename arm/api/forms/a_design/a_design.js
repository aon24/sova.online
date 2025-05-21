//
//
//
var tumba = [
	'f_fixed', 'f_insideOnly', 'f_lineOff', 'f_hide', 'f_rotate3Y|0',
	'f_left|0', 'f_top|0', 'f_bottom|0',
];

var screenFeature = ['phoneContur|0', 'pagePlusPreview', 'pagePlusDim'];

var arrowFeatures = ['x1', 'x2', 'y1', 'y2', 'len', 'io', 'linked'];

var mmmCommon = ['lineOff', 'insideOff']; // 4 кнопки внизу (fixed, turnOn - отдельно)

var gridFeatures = [
 'grid', 'gridX|0', 'gridY|0', 'gridWidth|1', 'gridColor|#d1d1d1'// 32 сетка
];

var mmmRoomsCommon = [ // общая для 3д, стен, мебели
 'bb3d|0', // главная 3d лента
 'rotate3X|0', 'rotate3Z|0',
 'wedWall|wed1', // Показать Все стены | Только одну
 'hide33|0', // 33 scale3d
 'cm|cm',
];

var mmmRoomsFull = [
 'is3dX|0', 'is3dY|0', 'is3dZ|0',
 'coverOn','angleHide','sidesOn',
 'sweep', // развертка стен
 'w3', // Толщина стен ]
 'shadowColor3', 'shadowR3|0', 'shadowW3|0', 'hide31|0' // 31 - тень для Rooms
];

var mmmWalls = [
 'w_shift|0', 'w_shiftTop|0', 'w_shiftGr|0',
 'w_rotate|0', 'w_rotateTop1|0','w_rotateTop2|0', 'w_rotateGr|0', 
];

var bricksM3t = [ // наклон блока, поворот, лев/прав, туда/сюда
	'm3t_rotate3X|0', 'm3t_rotate3Y|0', 'm3t_rotate3Z|0',
	'm3t_translateX|0', 'm3t_translateY|0', 'm3t_translateZ|0',
	'm3t_metric|0', 'm3t_fixed', 'm3t_fixedSize'
];
var bricks = [ // наклон блока, поворот, лев/прав, туда/сюда 
	'brick_fixed', 'brick_hide35|0', 'brick_insideOnly', 'brick2_insideOnly',
	'brick_rotate3X|0', 'brick_rotate3Y|0', 'brick_rotate3Z|0',
	'brick_translateZ|0',
	'brick_turnOn', 
];

var mmmM3T = [ // общее для блоков, кирпичей и таблиц
	'm3table_rotate3X|0','m3table_rotate3Y|0', 'm3table_rotate3Z|0',
	'm3table_wed|0', 'm3table_cm', 'm3table_hide33',
	'm3table_fixed', 'm3table_insideOnly',
];
var colorFeatures = ['bgStyle', 'gradient', // recalc With Redraw
	'backgroundColor', 'gradientColor', 'gradientDeg|0',
	'backgroundImage', 'bgiSizeX|100', 'bgiSizeY|100', 'repeatX', 'repeatY', 'bgiSizeXMetric', 'bgiSizeYMetric'
];

// box-features
var textFeatures = [
 'color|#000000ff', 'textAlign', 'fontFamily|Verdana', 'fontWeight', 'fontStyle', 'letterSpacing|0',
 'lineHeight|1.0', 'fontSize|40',
 'paddingLR|10', 'paddingTD|1', 'fontSizeMetric', 'letterSpacingMetric', 'paddingLRMetric', 'paddingTDMetric',
 'textIndent|10', 'textIndentMetric', 'overflow',
 'cmd', 'par', 'maxWidth', 'fontUnderline', 'margin',
];

var recalcWithRedraw = [
 'buttonAction|-', 'boxContent|0', 'fieldType', 'fieldStyle|0', 'anchor',
 'border', 'shadow', 'borderSide', 'trans', //trans: ['сдвиг', 'поворот', 'наклон']
 'bb|0',
];

var recalcOnly = [
	'dropList', 'xName', 'buttonUrl', 'buttonCmd', 'buttonLabel',
	'shadowX', 'shadowY', 'shadowR', 'shadowW', 'shadowColor',
	'insideOnly', 'fixed',
	'skewX', 'skewY',
	'rotateX', 'rotateY', 'rotateZ',
	'translateX', 'translateY', 'translateZ',
	'noIcons', 'flex', 'clipboard',
];
var m3empty = [
	'border', 'shadow', 'borderSide',
	'shadowX', 'shadowY', 'shadowR', 'shadowW', 'shadowColor',
	'insideOnly', 'fixed',
];
// *** *** ***
let docSP;
let tuMMM;

const _setFields = (fields, tuning, noPart) => {
	for (let it of fields) {
		let [fi, v] = docSP.util.partition(it, '|');
		
		if (fi === 'rotate3X') { // наклон rooms 75 -> 15
			docSP.setField(fi, 90 - tuning[fi]);
			continue;
		}
		
		let tun = noPart || !fi.includes('_') ?
			fi
			:
			docSP.util.partition(fi, '_')[1]; // fi = m3t_rotate3X, tun = rotate3X
		
		if (tun === 'rotate3Y' && tuMMM && tuMMM.mmm === 'rooms' && !tuning.furniture && tuning.mmm !== 'brick' && tuning.m3key !== 'm3t') {
			tun = 'rotate3Z';
		}

		if (tuning[tun] === undefined)
			tuning[tun] = v === '' || isNaN(v) ? v : Number(v);

		if (docSP.getField(fi) !== tuning[tun]) {
			docSP.setField(fi, tuning[tun]);
			tuning[tun] = docSP.getField(fi);
		}
	}
};

// *** *** ***

const showSetColors = (doc, box) => {
	let colorPage = doc.sovaPagesByName['settingColors'];
	docSP = colorPage.doc;
	colorPage.title = `Colors ${box.boxIndex}`;

	docSP.box = box;

	colorPage.frameStyle.display = 'block';

	_setFields(colorFeatures, box.tuning);
	_setFields(gridFeatures, box.tuning);
	colorPage.forceUpdate();
};

window.sovaActions = window.sovaActions || {};
window.sovaActions.a_design = {
	init: doc => {
		let settingColors = {
			hide: true, // при закрытии не удалять, а скрывать
			dbAlias: 'dba',
			unid: 'unid',
			pageName: 'settingColors',
			rsMode: 'new',
			min: true,
			pont: true,
			fix: true,
			smallCls: 'leftTop',
			newForm: `a_colors`,
			frameStyle: {top: 0, left: 0, width: 300}
		};
		let setting = {
			hide: true, // при закрытии не удалять, а скрывать
			dbAlias: 'dba',
			addUrl: `&key=${doc.getField('key')}`,
			unid: 'unid',
			pageName: 'setting',
			rsMode: 'new',
			min: true,
			pont: true,
			fix: true,
			smallCls: 'rightTop',
			newForm: `a_setting${ ['rooms','cases'].includes(doc.fieldValues['KEY']) ? '&key=d3' : ''}`,
			frameStyle: {width: 300, top: 0, right:15}
		};
/*
		let pagePlus = {
			hide: true, // при закрытии не удалять, а скрывать
			dbAlias: doc.dbAlias,
			unid: doc.unid,
			pageName: 'plus',
			rsMode: 'read',
			fieldValues: {_page_: '1', form: 'plus'},
			min: true,
			pont: true,
			smallCls: 'leftTop',
			frameStyle: {top: 0, left: 0, width: 295, height: 1, minHeight: 375, display: doc.getField('preview') ? 'block':'none'},
			children: [
				{ _teg: 'div', attributes: {className: 'pagePlus'}, children: [{_teg: 'div'}] },
				{field: [ 'pgDown', 'band', ['','','','','','','',''] ], attributes: {className: 'pageDown'} }
			],
		};
		doc.util.addChildPage(doc, pagePlus);
*/
		doc.util.addChildPage(doc, setting);
		doc.util.addChildPage(doc, settingColors);
	},
    //*** *** ***
  
    recalc: {},
    // *** *** ***
	
	querySave: doc => { // заполнить нужные поля перед сохранением
		let setPageDoc = doc.sovaPagesByName['setting'].doc;
		for (let it of ['project', 'pageName', 'pageUrl', 'title', 'pageCat', 'notes', 'key',
						'closed', 'preview', 'table', 'tableSize', 'saveScript'])
			doc.setField(it, setPageDoc.getField(it));
		
		if (setPageDoc.getField('saveScript')) {
			let s = JSON.stringify(doc.rootBox.clip.histArr);
			doc.setField('theScript', s);
		}
	},
	// *** *** ***
	
	// validatePM: {},


	
    cmd: {
		tbHist: doc => {
			url = `/api/getData?form=a_design&dbAlias=${doc.dbAlias}&unid=${doc.unid}`;
			doc.util.jsonByUrl(doc, url)
				.then( jsn => {
					items = jsn || [];
					if (items.length) {
						items.sort( (a, b) => a > b ? -1 : 1 )
						items.unshift(`__ (последняя сохраненная версия: ${doc.getField('notes')})`);
						doc.msg.list(items, 'История изменений')
							.then(it => { // it: '045__2022-09-21 13:58:00.702492 (Николай Сергеевич/SV, size:24169->2568)'
								let mdf = doc.util.partition(it, ' (')[0];
								mdf = doc.util.partition(mdf, '__')[1];
								let loadDocUrl = `api.get/loadDoc?dbAlias=${doc.dbAlias}&unid=${doc.unid}&mode=${doc.rsMode}&form=a_design&xmdf=${mdf}`;
								doc.util.jsonByUrl(doc, loadDocUrl)
									.then( jsn => {
										doc.hideNewValues = mdf ? {'FROMHIST': 1} : {}; // док из истории всегда даст конфликт
										doc.setDocProps(jsn);
									
										for (let xName in doc.fieldValues) { // повторная инициализация после пересчитывания данных с сервера
											if ( xName in doc.register && doc.register[xName].setValue )
												doc.register[xName].setValue(doc.fieldValues[xName]);
										}

										doc.forceUpdate();
										setTimeout( () => doc.forceUpdate(), 1);
									})
									.catch(e => console.log(e));
							})
							.catch(e => console.log(e));
					}
					else
						doc.msg.ok('История пуста');
				})
				.catch( e => console.log(e) );
		},

        undo: doc => doc.rootBox.clip.cmdUndo(),
        redo: doc => doc.rootBox.clip.cmdRedo(),
        
		showTuning: (doc, param, ctrl) => {
			let wrap = doc.rootBox.findWrap(doc.rootBox);
			wrap.moveResize = false;
			
			if (ctrl && wrap)
				wrap = wrap.parentBox;
			
			if (wrap) {
				let s = `l,t,w,h: ${wrap.rect.left}, ${wrap.rect.top}, ${wrap.rect.width}, ${wrap.rect.height}\n`;
				
				if(wrap.floating)
					s += 'floating: ' + wrap.floating + '\n';
				if(wrap.type)
					s += 'type: ' + wrap.type + '\n';
				if(wrap.row)
					s += 'row: ' + wrap.row + '\n';
				if(wrap.column)
					s += 'column: ' + wrap.column + '\n';


				s += `boxes: '${wrap.boxes.length}' floatBoxes: '${wrap.floatBoxes.length}'\n`;
				s += `cells: '${wrap.cells.length}' cellsBoxes: '${wrap.cellsBoxes.length}'\n`;
				s += `className: '${wrap.props.className || wrap.className}'\n`;
				s += `parentBox: ${wrap.parentBox && wrap.parentBox.boxIndex}\n`;
				s += `getFloat: ${wrap.getFloat.boxIndex}\n`;


				if (wrap.parent3d)
					s += 'parent3d: ' + wrap.parent3d.boxIndex + '\n';
				if (wrap.parent3T)
					s += 'parent3T: ' + wrap.parent3T.boxIndex + '\n';
				if (wrap.parent3M)
					s += 'parent3M: ' + wrap.parent3M.boxIndex + '\n';

				for (let k of Object.keys(wrap.tuning).sort())
					if (wrap.tuning[k])
						s += `\n${k}=${wrap.tuning[k]} (${typeof wrap.tuning[k]})`;
				doc.msg.ok(s, `Box ${wrap.boxIndex}`);
			}
		},
		
        setting: doc => {

			showSetColors(doc, doc.rootBox);

			doc.settingIsOpen = true;
			doc.settingBox = null; // чтобы при выборе блока он перерисовался
			let setPage = doc.sovaPagesByName['setting'];
			docSP = setPage.doc;
			setPage.title = 'Параметры страницы';
			
			docSP.style.background = 'linear-gradient(180deg, #ddd, #fff)';
			
			docSP.box = doc.rootBox;
			docSP.rootBox = doc.rootBox;
			docSP.pageBox = doc.pageBox;

			setPage.frameStyle.display = 'block';

			docSP.showSetting = 'setPage';
			
			_setFields(screenFeature, docSP.rootBox.tuning);
			_setFields(colorFeatures, docSP.rootBox.tuning);
			_setFields('playScript', doc.pageBox.tuning);
			

			doc.rootBox.tuning.interval = doc.rootBox.tuning.interval || 10;
			let arr = [10, 500, 1000, 2000, 5000, 10000];
			let interval = arr.indexOf(doc.rootBox.tuning.interval);
			docSP.setField('scriptDelay', interval < 0 ? 0 : interval);

			
			docSP.setField('screen', ((doc.pageBox.tuning.screen || 100)/100) - 1);
			setPage.forceUpdate();
		},
		
		pageBlur: (doc, pageName, e) => {},
		pageHide: (doc, pageName) => {
			if (pageName === 'setting')
				doc.settingBox = doc.settingIsOpen = null;
		},
		// ***

    	showSetBox: (doc, box) => {
			if (window.owlDebug)
				console.log('======================== showSetBox', box.boxIndex, 'm3key:', box.tuning.m3key, 'mmm:', box.tuning.mmm);
			if (box === doc.rootBox)
				return;

			let setPage = doc.sovaPagesByName['setting'];
			
			if (setPage.doc.getField('playScript') === 'play')
				return doc.sovaPagesByName['settingColors'].closePage();
			
			showSetColors(doc, box);

			let el;
			docSP = setPage.doc;
			doc.settingBox = box;
			docSP.box = box; // в командах и рекальках a_setting.js встречается "let box = doc.box;"
			let tuning = box.tuning;

			docSP.showSetting = 'setBox';
			setPage.frameStyle.display = 'block';

			//box.noForceUpdate = true;
			doc.settingIsOpen = true;

			const noFU = () => setPage.forceUpdate();
			
// arrow
if (tuning.line) {
	_setFields(['arrowType'], tuning); // отдельный обработчик
	_setFields(arrowFeatures, tuning);
	setPage.title = `Свойства стрелки ${box.boxIndex}`;
	docSP.style.background = '#ffffff';
	return noFU(box);
}

// colorFeatures
_setFields(colorFeatures, tuning);

if (box.floating && tuning.m3key === 'm3empty')
	;	
// свойства 3d
else if (box.parent3d) {
	tuMMM = box.parent3d.tuning; // 3d main

	// свойства brick
	if (tuning.mmm === 'brick' || (tuning.mmm === 'm3table' && !tuning.wall && box !== box.parent3d)) {
		if (box.parent3d === box) {
			_setFields(['brick_scale3d|1'], tuning);
			_setFields(['brick_cm|cm'], tuning);
		}
		if (tuning.mmm === 'brick')
			_setFields(['brick_wed|0'], tuning);
		else
			_setFields(['m3tab_wed|0'], tuning);
		
		_setFields(bricks, tuning);
		
		docSP.setField('brick_left', box.rect.left);
		docSP.setField('brick_top', box.rect.top);
		docSP.setField('brick_is3dX', box.rect.width);
		docSP.setField('brick_is3dY', box.rect.height);

		_setFields(['brick_is3dZ|0'], tuning);
		_setFields(['turnOn|0'], tuning);
		docSP.style.background = 'linear-gradient(180deg, #ffa, #ffffc9)';
		setPage.title = `3d блок ${box.boxIndex}`;
		
		if (tuning.mmm !=='brick')
			return noFU(box);
	}
	
	else if (tuning.mmm === 'm3table') { // таблица или тумба
		setPage.title = `3d таблица ${box.boxIndex}`;
		
		if (box.parent3d === box) { // одинокая таблица или одинокая тумба
			_setFields(mmmM3T, tuMMM);
			_setFields(['m3table_scale3d|1'], tuMMM);
			docSP.setField('m3table_is3dX', box.parent3d.rect.width);
			docSP.setField('m3table_is3dY', box.parent3d.rect.height);
			_setFields(['m3table_is3dZ|0'], tuMMM);
			return noFU(box);
		}

		_setFields(bricksM3t, tuning);
		return noFU(box);
	}
	
	if (tuMMM.mmm === 'rooms') {
		_setFields(mmmCommon, tuMMM);
		_setFields(['turnOn|0'], tuMMM);

		_setFields(['mmm_fixed'], box.parent3d.parentBox.tuning);
		_setFields(['scale3d|1'], tuMMM);
	}

	
	// свойства 3d-rooms
	if (tuning.mmm === 'rooms') {
		_setFields(mmmRoomsCommon, tuning);
		_setFields(mmmRoomsFull, tuning);

		_setFields(['persOn', 'perspective|1000', 'perspectiveOriginX|50', 'perspectiveOriginY|50'], box.parentBox.tuning);

		docSP.style.background = 'linear-gradient(180deg, #ffd8d8, #fff8f8)';
		setPage.title = `3d помещение ${box.boxIndex}`;
		return noFU(box);
	}
	
	// свойства стены
	if (tuning.wall) {
		_setFields(mmmRoomsCommon, tuMMM);
		_setFields(mmmWalls, tuning, true);
		_setFields(['w_left|0', 'w_top|0'], tuning, true);

		tuMMM.lastWall = box.parent3d.floatBoxes.indexOf(box.parentBox);

		docSP.setField('w_skewY', tuning.skewY);
		docSP.setField('w_is3dX', box.rect.width);
		docSP.setField('w_is3dY', box.rect.height);
		_setFields(['w_is3dZ|0'], tuning);
		
		docSP.style.background = 'linear-gradient(180deg, #d8ffd8, #f8fff8)';
		let wallsName ={'top': 'потолок','ground': 'пол','far': 'дальняя','right': 'справа','left': 'слева','door': 'дверь'};
		setPage.title = `3d стена (${wallsName[tuning.wall]}) ${box.boxIndex}`;
		//return noFU(box);
	}

	// *** *** ***
	
	if (tuning.furniture && tuMMM.bb3d === 2) {
		setPage.title = `3d мебель. ${tuning.named || ''} (${box.boxIndex})`;
		_setFields(tumba, tuning);
		docSP.setField('tumba_is3dX', box.rect.width);
		docSP.setField('tumba_is3dY', box.rect.height);
		_setFields(['tumba_is3dZ|0'], tuning);
		return noFU(box);
	}
		
	if (tuning.m3key === 'm3t') { // кирпич в стене(фасад). свойства m3t
		if (box.column)
			tuning.whp = 100 * box.rect.width / box.parentBox.rect.width;
		else if (box.row)
			tuning.whp = 100 * box.rect.height / box.parentBox.rect.height;
		
		if (tuning.metric) {
			if (box.row)
				docSP.setField('m3t_is3dY', tuning.whp);
			else
				docSP.setField('m3t_is3dX', tuning.whp);
		}
		else {
			docSP.setField('m3t_is3dX', box.rect.width);
			docSP.setField('m3t_is3dY', box.rect.height);
		}
		_setFields(['m3t_is3dZ|0'], tuning);

		_setFields(bricksM3t, tuning);

		if (tuMMM.mmm === 'rooms') {
			_setFields(mmmRoomsCommon, tuMMM);
			if (box.parent3T)
				_setFields(['wall_wed|0'], box.parent3T.tuning);
		}
		else {
			_setFields(mmmM3T, box.parent3T.tuning);
			_setFields(['m3table_scale3d|1'], box.parent3T.tuning);
		}

		
		docSP.style.background = 'linear-gradient(180deg, #ffa, #ffffc9)';
		setPage.title = `Фасад 3d-блока ${box.boxIndex}`;
		//return noFU(box);
	}
	
	// ***
	
	if (tuning.m3key === 'edge') { // грань
		if (box.parentBox.tuning.m3key === 'm3brick') // кирпч
			_setFields(['brickEdge_wed|0'], box.parentBox.tuning);
		
		else if (tuMMM.mmm === 'rooms') {
			_setFields(mmmRoomsCommon, tuMMM);
			if (box.parent3T === box.parentBox.getFloat && box.parent3T.tuning.wall) // кирпч in wall
				_setFields(['wall_wed|0'], box.parent3T.tuning);
		}
		
		else if (box.parent3T) { // одинокая таблица
			_setFields(mmmM3T, box.parent3T.tuning);
			_setFields(['m3table_scale3d|1'], box.parent3T.tuning);
		}
		
		setPage.title = `Грань 3d-блока ${box.boxIndex}`;
		docSP.style.background = '#f7d98b';
		//return noFU(box);
	}

	// ***
	
	if (tuning.m3key === 'm3empty') { // дырка в таблице или плав блок в стене или в кирпиче, или в грани
		if (tuMMM.mmm === 'rooms') {
			_setFields(mmmRoomsCommon, tuMMM);
			if (box.parent3T)
				_setFields(['wall_wed|0'], box.parent3T.tuning);
		}
		else if (box.parent3T) { // одинокая таблица
			_setFields(mmmM3T, box.parent3T.tuning);
			_setFields(['m3table_scale3d|1'], box.parent3T.tuning);
		}
		else { // одинокий кирпч
			_setFields(mmmM3T, box.parent3d.tuning);
			_setFields(['m3table_scale3d|1'], box.parent3d.tuning);
		}
	}

} // end of parent3d



// 2d
	if (!box.parent3d && box.getFloat.parentBox && box.getFloat.parentBox.boxIndex === 1000 && !tuning.line) {
		box.getFloat.tuning.scale2d = box.getFloat.tuning.scale2d || 1;
		box.getFloat.tuning.cm2d = box.getFloat.tuning.cm2d || 'cm';
		docSP.setField('cm2d', box.getFloat.tuning.cm2d);
		docSP.setField('scale2d', box.getFloat.tuning.scale2d);
	}
	if (!box.parent3d && !box.parent3T) {
		docSP.style.background = 'linear-gradient(180deg, #ddd, #fff)';
		setPage.title = `Свойства 2d-бокса ${box.boxIndex}`;
	}
	else
		setPage.title = `Свойства бокса ${box.boxIndex}`;
		
	// common
	for (let side of ['', 'Top', 'Right', 'Bottom', 'Left'])
		for (let it of [`border${side}Radius|0`, `border${side}RadiusMetric`, `border${side}Width|0`, `border${side}Style`, `border${side}Color`])
			_setFields([it], tuning);

	_setFields(['bb'], tuning);
	docSP.setField('boxSizeX', box.rect.width);
	docSP.setField('boxSizeY', box.rect.height);
	docSP.setField('rectLeft', box.rect.left);
	docSP.setField('rectTop', box.rect.top);
	if (box.parentBox) {
		docSP.setField('boxSizeXp', ` ${(box.rect.width  / box.parentBox.rect.width * 100).toFixed(2)}%` ); // boxSizeX в %
		docSP.setField('boxSizeYp', ` ${(box.rect.height  / box.parentBox.rect.height * 100).toFixed(2)}%` ); // boxSizeY в %
		docSP.setField('showAnchor', `b_${box.boxIndex}`); // показать якорь
		box.floating && docSP.setField('boxLayer', box.parentBox.floatBoxes.indexOf(box).toString()); // z-index
	}
	

// *** *** ***

	for (let arr of [textFeatures, recalcWithRedraw, recalcOnly])
		_setFields(arr, tuning);

	return noFU(box);

	// end of 2d
		
		}, // end of showSetBox
    }, // end of cmd
	
    //*** *** ***

	hide: { // doc.boxEditMode - бокс(не документ) в editMode
		undo: doc => doc.showUndo && !doc.boxEditMode, // true - показать, false - замутить
		redo: doc => doc.showRedo && !doc.boxEditMode, // true - показать, false - замутить
	},
    
};

