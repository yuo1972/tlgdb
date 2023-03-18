// регистрация всплывающих подсказок
const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]')
const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl))
tooltipList.map(tooltipTr => tooltipTr.disable())

// подсветка проблемных record's-ов
tooltipList.map(function(tooltipTr) {
    if (tooltipTr._element.dataset.bsTitle != ' ') {
        tooltipTr.enable()
        tooltipTr._element.classList.add("table-danger")
    }
})

//////////////////////////////////////////////////////////////////////////
//    удалить (del) в таблице абонента
var dWin = {
    trElem: null,
    newspan: null,

    delRec: function(elem,del_url) {
        allWinClear()

	    dWin.trElem = elem.parentNode.parentNode

        let eX = getX(elem)
	    let eY = getY(elem)

        dWin.trElem.classList.add("table-danger")

	    dWin.newspan = document.createElement('span')
	    dWin.newspan.id = 'delRecord'
	    document.body.appendChild(dWin.newspan)

	    dWin.newspan.className = 'newspan'

	    S(dWin.newspan).top = (eY - 40) + 'px'
	    S(dWin.newspan).left = (eX + 40) + 'px'

	    dWin.newspan.innerHTML = `<div align=right>удалить?&nbsp;
            <button class='btn btn-success' onclick='dWin.delRecords("${del_url}")'>да</button>&nbsp;
            <button class='btn btn-outline-success' onclick='dWin.cancel()'>отмена</button>
            </div>`

    },

//    delRecords1: function(url) {
//        fetch(url)
//            .then((response) => {
//                return response.json();
//            })
//            .then((data) => {
//                if (data.result != 1) {
//                    console.log(data)
//                    if (typeof data.err_str !== 'undefined') { alert(data.err_str) }
//                    else { alert('неизвестная ошибка') }
//                }
//            })
//
//        dWin.close(500)
//    },

    delRecords: function(url) {
        let jsonanswer = JSON.parse(naprRequest(url))
        if (jsonanswer.result != 1) {
            console.log(jsonanswer)
            if (typeof jsonanswer.err_str !== 'undefined') { alert(jsonanswer.err_str) }
               else { alert('неизвестная ошибка') }
        }
        dWin.close()
    },

    close: function(tsleep = 0) {
	    dWin.cancel()
	    setTimeout(() => { window.location.reload(); }, tsleep);
    },

    cancel: function() {
	    dWin.newspan.parentNode.removeChild(dWin.newspan)
	    dWin.newspan = null

        dWin.trElem.classList.remove("table-danger")
    }
}

//////////////////////////////////////////////////////////////////////////

function allWinClear() {
   if (dWin.newspan != null) dWin.cancel()
}

function O(obj) {
    if (typeof obj == 'object') return obj
    else return document.getElementById(obj)
}

function S(obj) {
    return O(obj).style
}

function getX(e) {
    var x = 0;
    while(e) {
	    x += e.offsetLeft;
	    e = e.offsetParent;
    }
    return x;
}

function getY(e) {
    var y = 0;
    while(e) {
	    y += e.offsetTop;
	    e = e.offsetParent;
    }
    return y;
}

//////////////////////////////////////////////////////////////////////////


function changeCheck(elem) {
	    trElem = elem.parentNode.parentNode
        if (elem.checked)
            { trElem.classList.add("table-warning") }
        else
            { trElem.classList.remove("table-warning") }
}

function dblClick(elem, id) {
	    trElem = elem.parentNode
	    chbox = document.getElementById(id)
        if (chbox.checked) {
            chbox.checked = false
            trElem.classList.remove("table-warning")
        }
        else {
            chbox.checked = true
            trElem.classList.add("table-warning")
        }
}

function addRecords(elem, add_url, list_url) {
    let req = {}
    let arr = []

    let checkboxes = document.getElementsByName('records');
    for (let ch0 of checkboxes) {
        if (ch0.checked == true) {
            arr.push(ch0.id)
        }
    }
    req['records'] = arr
//    console.log(JSON.stringify(req))

    send_post(add_url, req).then((ret) => {
        if (typeof ret.reestr_id !== 'undefined') {
//            window.location.reload()
            window.location.assign(list_url.replace('$$$',ret.reestr_id))
        }
        else {
            if (typeof ret.err_str !== 'undefined') { alert(ret.err_str) }
            else { alert('неизвестная ошибка') }
        }
    })

}


function tarification(set_client_url, redir_url) {
    let req = {}
    let arr = []

    let sel = document.querySelectorAll('select')

    for (let elem of sel) {
        if (elem.value == '???') {
            document.getElementById('errorAlert').innerHTML = "укажите подателей каждой телеграммы"
            return
        }
        else if (elem.id.startsWith('select-')) {
            arr.push(elem.id.slice('select-'.length) + '-' + elem.value)
        }
    }
    req['records'] = arr
//    console.log(JSON.stringify(req))

    send_post(set_client_url, req).then((ret) => {
        if (ret.result != 1) {
            if (typeof ret.err_str !== 'undefined') {
                document.getElementById('errorAlert').innerHTML = ret.err_str
            }
            else {
                document.getElementById('errorAlert').innerHTML = 'неизвестная ошибка'
            }
        }
        else {
//            window.location.assign(redir_url)
            window.location.href = redir_url
        }
    })
}


function change_autocost(elem, upd_url) {
    recid = elem.id.slice('chkautocost-'.length)
    btnresetrec = document.getElementById('btnresetrec-' + recid)
    btncalcrec = document.getElementById('btncalcrec-' + recid)
    btnsaverec = document.getElementById('btnsaverec-' + recid)

    if (elem.checked) {     // ==============================================  выбран ручной расчет
        document.getElementById('inpnumword-' + recid).disabled = false
        document.getElementById('inpurgdeliv-' + recid).disabled = false
        document.getElementById('inpurgword-' + recid).disabled = false
        document.getElementById('inpnotif-' + recid).disabled = false
        document.getElementById('inplux-' + recid).disabled = false
        document.getElementById('inptodate-' + recid).disabled = false
        document.getElementById('inpkkv-' + recid).disabled = false
        document.getElementById('inpsumm-' + recid).disabled = false
        document.getElementById('inpnds-' + recid).disabled = false

        btnresetrec.hidden = 'hidden'
        btncalcrec.hidden = ''
        btnsaverec.hidden = ''
    }
    else {
        document.getElementById('inpnumword-' + recid).disabled = true
        document.getElementById('inpurgdeliv-' + recid).disabled = true
        document.getElementById('inpurgword-' + recid).disabled = true
        document.getElementById('inpnotif-' + recid).disabled = true
        document.getElementById('inplux-' + recid).disabled = true
        document.getElementById('inptodate-' + recid).disabled = true
        document.getElementById('inpkkv-' + recid).disabled = true
        document.getElementById('inpsumm-' + recid).disabled = true
        document.getElementById('inpnds-' + recid).disabled = true

        btnresetrec.hidden = ''
        btncalcrec.hidden = 'hidden'
        btnsaverec.hidden = 'hidden'
    }

    update_record_chekbox(elem, upd_url, 'autocost')
}


function refresh_tr(elemtr, record) {
    elemid = elemtr.id
    id = elemid.slice(elemid.indexOf('-')+1)

    document.getElementById('inpurgdeliv-' + id).value = record.cost_deliv
    document.getElementById('inpurgword-' + id).value = record.cost_word
    document.getElementById('inpnotif-' + id).value = record.cost_notif
    document.getElementById('inplux-' + id).value = record.cost_lux
    document.getElementById('inptodate-' + id).value = record.cost_todate
    document.getElementById('inpkkv-' + id).value = record.cost_service
    document.getElementById('inpsumm-' + id).value = record.cost
    document.getElementById('inpnds-' + id).value = record.cost_nds
    document.getElementById('selcountry-' + id).value = record.country_name
    document.getElementById('inpnumword-' + id).value = record.num_word
    document.getElementById('selurgent-' + id).value = record.typeUrg
    document.getElementById('selnotif-' + id).value = record.typeNot
    document.getElementById('sellux-' + id).value = record.typeLX
    document.getElementById('chktodate-' + id).checked = record.todate_bool
    document.getElementById('chkkkv-' + id).checked = record.kkv_bool

    if (record.alarm != '') {
        elemtr.classList.add("table-danger")

        tooltipList.map(function(tooltipTr) {
            if (tooltipTr._element == elemtr) {
                tooltipTr.setContent({ '.tooltip-inner': record.alarm })
                tooltipTr.enable()
                tooltipTr.show()
            }
        })
    }
    else {
        elemtr.classList.remove("table-danger")

        tooltipList.map(function(tooltipTr) {
            if (tooltipTr._element == elemtr) {
                tooltipTr.setContent({ '.tooltip-inner': '' })
                tooltipTr.hide()
                tooltipTr.disable()
            }
        })
    }
}


function get_parent_tr(elem) {   // возвр родительский tr
    let el = elem.parentNode

    for (let i = 0; i < 10; i++) { // не глубже 10 элем
        if (el.tagName === 'TR') {
            return el
        }
        else {
            el = el.parentNode
        }
    }
    return false
}


function update_record(elem, upd_url, field='') {
    let req = {}
    if (field != '') {
        req[field] = elem.value
    }
    elemtr = get_parent_tr(elem)

    send_post(upd_url, req).then((ret) => {
            if (typeof ret.cost !== 'undefined') {
                refresh_tr(elemtr, ret)
            }
            else {
                if (typeof ret.err_str !== 'undefined') {
                    document.getElementById('errorAlert').innerHTML = ret.err_str
                }
                else {
                    document.getElementById('errorAlert').innerHTML = 'неизвестная ошибка'
                }
            }
    })
}


function calculate_record(elem, calc_url) {
    document.getElementById('errorAlert').innerHTML = ''

    let req = {}
    recid = elem.id.slice('btncalcrec-'.length)
    req['numword'] = document.getElementById('inpnumword-' + recid).value
    elemtr = get_parent_tr(elem)

    send_post(calc_url, req).then((ret) => {
            if (typeof ret.cost !== 'undefined') {
                refresh_tr(elemtr, ret)
            }
            else {
                if (typeof ret.err_str !== 'undefined') {
                    document.getElementById('errorAlert').innerHTML = ret.err_str
                }
                else {
                    document.getElementById('errorAlert').innerHTML = 'неизвестная ошибка'
                }
            }
    })
}


function update_record_chekbox(elem, upd_url, field) {
    let req = {}
    req[field] = elem.checked
    elemtr = get_parent_tr(elem)

    send_post(upd_url, req).then((ret) => {
            if (typeof ret.cost !== 'undefined') {
                refresh_tr(elemtr, ret)
            }
            else {
                if (typeof ret.err_str !== 'undefined') {
                    document.getElementById('errorAlert').innerHTML = ret.err_str
                }
                else {
                    document.getElementById('errorAlert').innerHTML = 'неизвестная ошибка'
                }
            }
    })
}


function save_record(elem, save_url) {
    document.getElementById('errorAlert').innerHTML = ''

    let req = {}

    recid = elem.id.slice('btnsaverec-'.length)
    req['numword'] = document.getElementById('inpnumword-' + recid).value
    req['urgdeliv'] = document.getElementById('inpurgdeliv-' + recid).value
    req['urgword'] = document.getElementById('inpurgword-' + recid).value
    req['inpnotif'] = document.getElementById('inpnotif-' + recid).value
    req['inplux'] = document.getElementById('inplux-' + recid).value
    req['inptodate'] = document.getElementById('inptodate-' + recid).value
    req['inpkkv'] = document.getElementById('inpkkv-' + recid).value
    req['summ'] = document.getElementById('inpsumm-' + recid).value
    req['summnds'] = document.getElementById('inpnds-' + recid).value
    req['country'] = document.getElementById('selcountry-' + recid).value
    req['urgent'] = document.getElementById('selurgent-' + recid).value
    req['notification'] = document.getElementById('selnotif-' + recid).value
    req['lux'] = document.getElementById('sellux-' + recid).value
    req['todate'] = document.getElementById('chktodate-' + recid).checked
    req['kkv'] = document.getElementById('chkkkv-' + recid).checked

    elemtr = get_parent_tr(elem)

    send_post(save_url, req).then((ret) => {
            if (ret.result != 1) {
                if (typeof ret.err_str !== 'undefined') {
                    document.getElementById('errorAlert').innerHTML = ret.err_str
                }
                else {
                    document.getElementById('errorAlert').innerHTML = 'неизвестная ошибка'
                }
            }
    })

}


function fixed(fix_url) {

    let req = {}
    req['operator'] = document.getElementById('operatorid').value
    if (req['operator'] == '') {
        document.getElementById('errorAlert').innerHTML = 'не указана фамилия оператора'
        return
    }

    send_post(fix_url, req).then((ret) => {
            if (ret.result == 1) {
                window.location.reload()
            }
            else {
                if (typeof ret.err_str !== 'undefined') {
                    document.getElementById('errorAlert').innerHTML = ret.err_str
                }
                else {
                    document.getElementById('errorAlert').innerHTML = 'неизвестная ошибка'
                }
            }
    })

}


function change(ch_url, tar_url) {
    let jsonanswer = JSON.parse(naprRequest(ch_url))
    if (jsonanswer.result == 1) {
        window.location.href = tar_url
    }
    else {
        if (typeof jsonanswer.err_str !== 'undefined') {
            document.getElementById('errorAlert').innerHTML = jsonanswer.err_str
        }
        else {
            document.getElementById('errorAlert').innerHTML = 'неизвестная ошибка'
        }
    }
}


function select_() {
    tbodylist = document.getElementsByTagName('tbody')

    for(let tbody of tbodylist) {
            user = document.getElementById("user-" + tbody.id).innerHTML
            status = document.getElementById("status-" + tbody.id).innerHTML
            check_status = document.getElementById(status)
            check_user = document.getElementById(user)

            if (check_user.checked && check_status.checked) {
                tbody.style.display = ''
            }
            else {
                tbody.style.display = 'none'
            }
    }
}


function send_cmd_and_reload(bill_url) {
    let jsonanswer = JSON.parse(naprRequest(bill_url))
    if (jsonanswer.result == 1) {
        window.location.reload()
    }
    else {
        if (typeof jsonanswer.err_str !== 'undefined') {
            document.getElementById('errorAlert').innerHTML = jsonanswer.err_str
        }
        else {
            document.getElementById('errorAlert').innerHTML = 'неизвестная ошибка'
        }
    }
}


///////////////////////////////////////////////////////////////////////////////
// асинхронный POST-запрос
async function send_post(url, json_data) {
        let response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                "X-CSRFToken": getCookie("csrftoken")
            },
            body: JSON.stringify(json_data)
        })
        console.log(json_data)
        let result = await response.json()
        console.log(result)
        return result
}

function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = cookies[i].trim();
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }


// синхронный запрос
function naprRequest(orequest,callback) {
    var textansw = ''
    var request = new XMLHttpRequest()
    request.open("GET", orequest , false)
    request.onreadystatechange = function()	{
	    if (this.readyState == 4) {
		    if (this.status == 200)	{
			    if (this.responseText != null) {
			        textansw = this.responseText
				    if (callback) { callback(false) }
				 }
		    }
			else {
			    alert("Ошибка Ajax: Данные не получены ")
				if (callback) { callback(false) }
		    }
		}
		else {
		    alert( "Ошибка Ajax: " + this.statusText)
			if (callback) { callback(false) }
		}
	}

    request.send(null)
    return textansw
}
