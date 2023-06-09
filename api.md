## API tlgdb

### API работы с БД телеграмм

__GET /tlg/api/__ - получть список телеграмм в БД  
__GET /tlg/api/{id}__ - получть данные конкретной телеграммы    
__POST /tlg/api/__ - добавить данные телеграммы в БД  
__PUT (PATCH) /tlg/api/{id}__ - отредактировать данные телеграммы в БД  
__DELETE /tlg/api/{id}/__ - удалить телеграмму из БД  

Можно использовать фильтрацию по ключам:
- __un_name__ - полное совпадение с полем ___un_name___ (уникальный идентификатор тлг)
- __inp_num__ - полное совпадение с полем ___inp_num___ (номер тлг на входящем канале)
- __out_num__ - полное совпадение с полем ___out_num___ (номер тлг на исходящем канале)
- __inp_chan__ - регистронезависимое совпадение с началом поля ___inp_chan___ (входящий канал)  
- __out_chan__ - регистронезависимое совпадение с началом поля ___out_chan___ (исходящий канал)  
- __kn__ - регистронезависимое совпадение регулярного выражения с полем ___kn___ (кассовый номер)  
- __pp__ - регистронезависимое совпадение регулярного выражения с полем ___pp___ (пункт подачи телеграммы)  
- __address__ - регистронезависимое совпадение регулярного выражения с полем ___address___ (адрес получателя)  
- __subscribe__ - регистронезависимое совпадение регулярного выражения с полем ___subscribe___ (подпись)  
- __datei_after, datei_before__ - с какой по какую дату включительно поступила телеграмма в ЦКС 
(поле ___inp_gate_date___);  например:
    - __?datei_after=2022-08-01&datei_before=2022-08-02__ - выборка с 1 по 2 августа включительно 2022 г  
    - __?datei_before=2022-08-02__ - выборка по 2 августа включительно 2022 г  
    - __?datei_after=2022-08-01&datei_before=2022-08-01__ - выборка за 1 августа 2022 г  
 
Для упорядочивания вывода результатов в __GET__-запросе можно использовать query-параметр __?ordering=<имя_поля_в_модели>__

***

### API работы с телеграфным калькулятором

__GET /tlgtarif/tcalc/api/__ - получить стоимость телеграммы по компонентам и в целом.  

Ключи в url-вызове:
- __date__ - дата, за которую нужно использовать тарифы (прим.: _2022-08-01_)
- __numword__ - количество слов в телеграмме (число)
- __lux__ - тип телеграммы - ЛЮКС (_true/false_)
- __luxv__ - тип телеграммы - ЛЮКС/В (_true/false_)
- __notif__ - тип телеграммы - УВЕДОМЛЕНИЕ ТЕЛЕГРАФОМ (_true/false_)
- __notifurg__ - тип телеграммы - УВЕДОМЛЕНИЕ ТЕЛЕГРАФОМ СРОЧНОЕ (*true/fals*e)
- __radioord__ - категория телеграммы - обычная (*true/false*)
- __radiourg__ - категория телеграммы - СРОЧНАЯ (*true/false*)
- __radiopost__ - категория телеграммы - ПОЧТОЙ ЗАКАЗНОЕ (*true/false*)
- __radiobox__ - категория телеграммы - ДО ВОСТРЕБОВАНИЯ (А/Я) (*true/false*)
- __todate__ - тип телеграммы - ВРУЧИТЬ (*true/false*)
- __service__ - тип телеграммы - СЛУЖЕБНАЯ (*true/false*)
- __country__ - страна назначения (*Россия* или др. страна экс-СССР)

Ответ в формате json:

```
{    
    "cost_service": "0.00",  # стоимость типа телеграммы СЛУЖЕБНАЯ
    "cost_todate": "0.00",   # стоимость типа телеграммы ВРУЧИТЬ
    "cost_lux": "0.00",      # стоимость типа телеграммы ЛЮКС
    "cost_notif": "0.00",    # стоимость типа телеграммы УВЕДОМЛЕНИЕ ТЕЛЕГРАФОМ
    "cost_deliv": "47.30",   # стоимость доставки телеграммы
    "cost_word": "44.00",    # стоимость слов телеграммы
    "cost_summ": "91.30",    # общая стоимость телеграммы 
    "cost_nds": "109.56",    # стоимость телеграммы с НДС
    "errorAlert": ""         # описание ошибки
}
```

