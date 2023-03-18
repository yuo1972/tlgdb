
function notif_change() {
    elem_notif = document.getElementById('notifid')
    if (elem_notif.checked) {
        elem_notifurgent = document.getElementById('notifurgentid')
        if (elem_notifurgent.checked) elem_notifurgent.checked = false

    }

    calculate_tlg()
}


function notifurgent_change() {
    elem_notifurgent = document.getElementById('notifurgentid')
    if (elem_notifurgent.checked) {
        elem_notif = document.getElementById('notifid')
        if (elem_notif.checked) elem_notif.checked = false
    }

    calculate_tlg()
}


function lux_change() {
    elem_lux = document.getElementById('luxid')
    if (elem_lux.checked) {
        elem_luxv = document.getElementById('luxvid')
        if (elem_luxv.checked) elem_luxv.checked = false
    }

    calculate_tlg()
}


function luxv_change() {
    elem_luxv = document.getElementById('luxvid')
    if (elem_luxv.checked) {
        elem_lux = document.getElementById('luxid')
        if (elem_lux.checked) elem_lux.checked = false
    }

    calculate_tlg()
}


function calculate_tlg() {
    calc_url = document.getElementById('tcalc_url').value + '?'

    calc_url += "date=" + document.getElementById('dateid').value + "&"
    calc_url += "numword=" + document.getElementById('numwordid').value + "&"
    calc_url += "lux=" + document.getElementById('luxid').checked + "&"
    calc_url += "luxv=" + document.getElementById('luxvid').checked + "&"
    calc_url += "notif=" + document.getElementById('notifid').checked + "&"
    calc_url += "notifurg=" + document.getElementById('notifurgentid').checked + "&"
    calc_url += "radioord=" + document.getElementById('radioOrdinary').checked + "&"
    calc_url += "radiourg=" + document.getElementById('radioUrgent').checked + "&"
    calc_url += "radiopost=" + document.getElementById('radioPost').checked + "&"
    calc_url += "radiobox=" + document.getElementById('radioBox').checked + "&"
    calc_url += "todate=" + document.getElementById('todateid').checked + "&"
    calc_url += "service=" + document.getElementById('serviceid').checked + "&"
    calc_url += "country=" + encodeURIComponent(document.getElementById('selectcountryid').value)
//        console.log(calc_url)

    fetch(calc_url).then(async function(response){
        let body = await response.json();
//        console.log(body);
        document.getElementById('cost_service').innerHTML = body.cost_service
        document.getElementById('cost_todate').innerHTML = body.cost_todate
        document.getElementById('cost_lux').innerHTML = body.cost_lux
        document.getElementById('cost_notif').innerHTML = body.cost_notif
        document.getElementById('cost_deliv').innerHTML = body.cost_deliv
        document.getElementById('cost_word').innerHTML = body.cost_word
        document.getElementById('cost_summ').innerHTML = body.cost_summ
        document.getElementById('cost_nds').innerHTML = body.cost_nds
        document.getElementById('errorAlert').innerHTML = body.errorAlert
    })

}

/////////////////////////////////////////////////////////////////

function showT() {
    tlist_url = document.getElementById('tlist_url').value + '?date=' + document.getElementById('dateid').value
    fetch(tlist_url).then(async function(response){
        let body = await response.text();
//        console.log(body);
        document.getElementById('tarifModalBody').innerHTML = body
    })
}

