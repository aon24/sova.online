
# Описание проекта Sova

## Общая архитектура

**Технологический стек:**
- **Бэкенд:** Django (Python)
- **Фронтенд:** ReactJS

## Механизм взаимодействия клиент-сервер

### Генерация UI на сервере
Разметка тега BODY формируется на Python в виде XML-подобной структуры и отправляется клиенту в формате JSON.

### Структура элементов

#### HTML-тег:
```json
{
  "_teg": "div",
  "attributes": {...},
  "text": "Hello world",
  "children": [{...}]
}
```

#### React-компонент:
```json
{
  "field": [fieldName, fieldType, param],
  "fieldProps": {...},
  "attributes": {...}
}
```

### Обработка на клиенте
React-скрипт рекурсивно распаковывает структуру:

```javascript
// Для HTML-тегов
return React.createElement(element._teg, {key: i, ...element.attributes}, children);

// Для кастомных компонентов  
switch (fieldType) {
  case 'btn':    return <Btn key={i} {...prop}/>;
  case 'chb':    return <Checkbox key={i} {...prop}/>;
  case 'number': return <SmartNumber key={i} {...prop}/>;
  case 'list':   return <List key={i} {...prop}/>;
  case 'band':   return <Band key={i} {...prop}/>;
  case 'fd':     return <Field key={i} {...prop}/>;
  // ... другие типы полей
}
```

# Ключевые компоненты системы

### Бэкенд (Django)
инструменты:
```python

class DC(object)
    ''' аналог dict, сделан для упрощения работы и для красоты кода
    особенности:
    - регистронезависимый
    - не генерирует "key error", а возвращает пустую строку
    - возвращает значения словаря через атрибут
    dc = DC(q=1, QQ=2)
    print(dc['q'], dc.qq, dc.keys(), dc.values(), dc.items())
    '''
...

well(*keys) # доступ к глобальному словарю. Возвращает то, что туда положили
toWell(d, *keys) # положить в словарь объект d с ключом (с ключами) keys

```

**Базовый класс страницы:**
```python
class Page(object):
    '''
    self.urlForm - url для формы: f'/api/getс/loadForm?form={self.form}::{crc32}'
    При открытии докумета клиенту передаются значения полей и url формы.
    JS по url загружает и распаковывает форму и передает на прорисовку React.

    Сами формы хранятся в глобальном словаре в виде json-строк.
    Получить форму: js = well('form-json', КЛЮЧ), где КЛЮЧ - 'ИМЯ_ФОРМЫ::CRC_СУММА'
    Т.о. форма кэшируется с обеих сторон.
    В редких случаях, когла форма зависит от данных, в форме задается self.noCaching = True.
    Url без кэширования: f'/api/get/loadForm?form={self.form}::{crc32}'
    Клиент каждый раз будет лезть на сервер, а сервер будет каждый раз парсить
    '''

    def __init__(self, request):
        '''
        request.dcUK - DC объект со значениями ключей
        ''' 
        ...

    # *** *** ***

    def page(self, request=None):
        '''
        Главный метод класса. То, что увидит пользователь.
        Возвращает словрь dict(_teg='div', className='PageStyle', children=[...])
        '''
        pass

    def getJsDoc(self, request, coocieBtn=None):
        '''
        fормирует словарь для отправки клиенту
        request.dcUK.doc - DC объект со значениями полей
        '''
        ...
        return json.dumps(ds, ensure_ascii=False)

    # *** *** ***

    def getOldValue(self, request, fv, do):
        '''
		    do - old(fields from DB), fv - after queryOpen
		'''
        return {k: do.get(k, '') for k in fv if do.get(k, '') != fv[k]}
    def queryOpen(self, request): pass
    def querySave(self, dcUK): return True
    def afterSave(self, dcUK, pk=None): return True
    def getData(self, dcUK): return  # вызывется из xhr api/post/getJson 
    def _getUrl(self, request):
        '''
        возвращает url для загрузки формы
        сама форма хранится в глоб. словаре 'form-json', в url ключ для этого словаря
        '''
        ...
	def _parseCell(self, cell):
		'''
		проверяет форму и убирает лишние элемнты
		'''
        ...
```

### Фронтенд (ReactJS)

```Javascript
// Главный элемент в прорисовке - объект сласса Document
// Soca - многооконный сайт, на стрнице м.б. несколько окон,
// у каждого свой экземпляр класса Document.
// при рендеринге вызывается функция boxing
// которая врзвращает рекурсивно распакованную структуру того, что прислал сервер
    children = boxing(page.children, this, this.readOnly);

// Для HTML-тегов
...
    return React.createElement(element._teg, {key: i, ...element.attributes}, children);

// Для кастомных компонентов
...
    switch (fieldType) {
    case 'btn':    return <Btn key={i} {...prop}/>;
    case 'chb':    return <Checkbox key={i} {...prop}/>;
    case 'number': return <SmartNumber key={i} {...prop}/>;
    case 'json':	return <JsonArea key={i} {...prop}/>;
    case 'list':	return <List key={i} {...prop}/>;
    case 'view':	return <View key={i} {...prop}/>;
    case 'band':	return <Band key={i} {...prop}/>;
    // ... другие типы полей
}
```

### Подгружаемы скрипты (Vanilla JavaScript)
Каждая форма может иметь свои подгружаемые скрипты
для обработки команд, скрытия элементов, проверки значений и пр.
Скрипты желательно размещать в той же директории, где форма
```python
class MyPage(Page):
    def __init__(self, request):
        self.form = getattr(self, '__module__', '').rpartition('.')[2]
        self.jsCssUrl = [ f'/api/jsv?forms/{self.form}/{self.form}.js'] # общий
        self.jsCssUrlEdit = [ f'/api/jsv?forms/{self.form}/{self.form}_edit.js'] # mode in ['edit', 'new']
        self.jsCssUrlRead = [ f'/api/jsv?forms/{self.form}/{self.form}_read.js'] # mode in ['read', 'preview']
```

Привязки скрипта к документу с данной формой делается с помощью глобальной переменной

```javascript
// file: /api/jsv/forms/MyPage/MyPage.js
window.sovaActions = window.sovaActions || {};
window.sovaActions.MyPage = {
	init: doc => { // инициализация до прорисовки. Поля загружены в doc.vieldValues, но dom не создан
    },
	init2: doc => {
        // инициализация после первого вызова componentDidUpdate
    },
    hide: { // скрытие элементов и полей. Регистрозависим. 

        // скрыть элементы, у которых name='viewbar', если поле 'upList' не равно 0 и не пустое
		viewbar: doc => doc.getField('upList'), // hide if true
        ...
    },

    cmd: {
        // control Button при нашатии вызывает команду с параметрами

        Pref:(doc, pk, ctrlKey, shiftKey) => { // cmd='Pref', param=id_Profile|id_SessiomSt
            // открыть в дочернем окне профайл студента
			let [pkPref, pkSst] = pk.partition('|');
			let view = doc.getControl('mainList');
			view.rowClick(pkSst); // подсветить стоку в которой кнопка "Открыть профайл"
			let page = {form: 'Profile', dbAlias: 'nv_Profile', rsMode: 'edit', unid: pkPref};
			page.title = 'Редактирование профайла студента';
			doc.previewNew(page, ctrlKey, shiftKey);
            // doc.previewNew открывает форму в дочернем окне
            // или в новой вкладке (ctrlKey=true)
            // или в новой вкладке в режиме info: просмотр полей (ctrlKey=shiftKey=true)
		},
        ...
    },
	validate: { // проверка значений
		title: doc => doc.getField('title') ? '' : 'Заголовок',
        // если пусто при сохранении выведет диалогбокс "Поле 'Заголовок' не заполнено!"
	},
	querySave: doc => { // необходимые действия перед сохранением
		doc.setField('title', doc.getField('title').trim()); // убрать пробелы в поле 'title'
	},

}
```
**

