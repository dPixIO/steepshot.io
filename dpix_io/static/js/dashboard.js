/**
 * Created by evgeni on 21.12.17.
 */

    window.dpix = window.dpix || {};
    dpix.classBtn = $("#btn_7");
    dpix.classBtn.css({
        background: '#fe6637',
        color: '#fff'
    });



    var nameData, dataGraph;
    function checkNameRatio (nameData) {
        if (nameData==='dweb'){
            dataGraph = 'data_dweb'
        }
        else if (nameData==='sum'){
            dataGraph='data_sum'
            }
        else
            dataGraph='data_dpay';
    }
    checkNameRatio(nameData);
    function check_radio(platform) {
        nameData = document.getElementsByName("myRadio").value = platform;
        checkNameRatio(nameData);
        drawGraphs(dataGraph_1);
        drawGraphs(dataGraph_2);
        drawGraphs(dataGraph_3);
        drawGraphs(dataGraph_4);
        drawGraphs(dataGraph_5);
        drawGraphs(dataGraph_6);
        drawGraphs(dataGraph_7);
        drawGraphs(dataGraph_8);
        drawGraphs(dataGraph_9);
        }
    var apiQuery = {'date_to': null,
                    'date_from': null};
    var dataGraph_1, dataGraph_2, dataGraph_3, dataGraph_4, dataGraph_5, dataGraph_6, dataGraph_7, dataGraph_8, dataGraph_9;
    function get_data(apiQuery) {

        if (apiQuery['date_to'] != null) {
            var date_from = '&date_from=' + apiQuery['date_from'];
            var date_to = '&date_to=' + apiQuery['date_to'];
        }
        else {
            var date_from = '';
            var date_to = '';
        }
        var api = ['?graph=1', '?graph=2', '?graph=3', '?graph=4', '?graph=5', '?graph=6', '?graph=7', '?graph=8', '?graph=9'];
        api.forEach(function(item, i, arr) {
        $.getJSON('.'+ item+date_to+date_from, function (data) {
        switch (i) {
            case 0:
                dataGraph_1 = data;
                drawGraphs(dataGraph_1);
                break;
            case 1:
                dataGraph_2 = data;
                drawGraphs(dataGraph_2);
                break;
            case 2:
                dataGraph_3 = data;
                drawGraphs(dataGraph_3);
                break;
            case 3:
                dataGraph_4 = data;
                drawGraphs(dataGraph_4);
                break;
            case 4:
                dataGraph_5 = data;
                drawGraphs(dataGraph_5);
                break;
            case 5:
                dataGraph_6 = data;
                drawGraphs(dataGraph_6);
                break;
            case 6:
                dataGraph_7 = data;
                drawGraphs(dataGraph_7);
                break;
            case 7:
                dataGraph_8 = data;
                drawGraphs(dataGraph_8);
                break;
            case 8:
                dataGraph_9 = data;
                drawGraphs(dataGraph_9);
                break;
            default:
                break;
        }
    })})}
    function drawGraphs(data) {
        console.log(data);
        var chartDiv = document.getElementById(data['name_div']);
        var dataY1 = {
            'x' : data['date'],
            'y': data[dataGraph][0],
             type: 'scatter',
             name: data['name_data_line_1']

        };
        if (data[dataGraph].length == 2) {
            var dataY2 = {
                'x': data['date'],
                'y': data[dataGraph][1],
                type: 'scatter',
                name: data['name_data_line_2']
            };
             data_res = [dataY1, dataY2];
        }
        else {
             data_res = [dataY1]
        }
        console.log(dataY1);
        var layout = {xaxis: {
            tickformat: "%Y-%m-%d"
        },
                    title: data['title'],
                    hovermode: 'closest',
                    autosize: true
                };
        Plotly.newPlot(chartDiv, data_res, layout);
    }
    get_data(apiQuery);
    function data_from_input(form) {
        var elems = form.elements;
        apiQuery['date_to'] = elems.date_to.value;
        apiQuery['date_from'] = elems.date_from.value;
        var checkDate = new Date();
        if (format_date(checkDate) <= apiQuery['date_to']) {
            $('#error').css('display', 'block');
        }
    else {
            $('#error').css('display', 'none');
            get_data(apiQuery);
        }
    }
    function format_date(date){
        var yyyy = date.getFullYear();
        var mm = parseInt(date.getMonth())+1;
        var dd = date.getDate();
        if(dd<10)
        {
            dd='0'+dd;
        }
        if(mm<10)
        {
            mm='0'+mm;
        }
        return yyyy+'-'+mm+'-'+dd
    }


    function click_btn(btn) {
        if (dpix.classBtn.attr('id') !== btn.id) {
            $(btn).css({
            background: '#fe6637',
            color: '#fff'
        });
          $(dpix.classBtn).css({
              background: '#f6f6fb',
              color: '#fe6637'
          });
          dpix.classBtn = $('#' + btn.id);
        }}

    function data_from_button(btn) {
        var dateTo = new Date();
        var dateFrom = new Date();
        dateTo.setDate(dateTo.getDate() - 1);
        if (btn.value === '90'){
            dateFrom.setDate(dateFrom.getDate() - 90 - 1);
        }
        else if (btn.value==='7'){
            dateFrom.setDate(dateFrom.getDate() - 7 - 1);
        }
        else
        {
            dateFrom.setDate(dateFrom.getDate() - 30 - 1);
        }
        dateFrom = format_date(dateFrom);
        dateTo = format_date(dateTo);
        apiQuery['date_to'] = dateTo;
        apiQuery['date_from'] = dateFrom;
        click_btn(btn);
        get_data(apiQuery);
    }
