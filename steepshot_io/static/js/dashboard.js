/**
 * Created by evgeni on 21.12.17.
 */

    window.steepshot = window.steepshot || {};
    steepshot.classBtn = $("#btn_7");
    steepshot.classBtn.css({
        background: '#fe6637',
        color: '#fff'
    });

    var namePlatform = document.getElementsByName("myRadio")[0].value;
    function check_radio(platform) {
        // nameData = platform;
        namePlatform = platform;
        apiQuery['platform'] = namePlatform;
        get_data(apiQuery)
        }
    var apiQuery = {'date_to': null,
                    'date_from': null,
                    'platform': namePlatform};
    function get_data(apiQuery) {

        if (apiQuery['date_to'] != null) {
            var date_from = '&date_from=' + apiQuery['date_from'];
            var date_to = '&date_to=' + apiQuery['date_to'];
            var platform = '&platform=' + apiQuery['platform']
        }
        else {
            var date_from = '';
            var date_to = '';
            var platform = '&platform=' +namePlatform;
        }
        var api = ['?graph=DAU', '?graph=post_count', '?graph=votes_comments', '?graph=usd',
                    '?graph=steem', '?graph=timeouts', '?graph=LTV'];
        api.forEach(function(item, i, arr) {
        $.getJSON('.'+ item+date_to+date_from+platform, function (data) {
            drawGraphs(data)
    })})}
    function drawGraphs(data) {
        console.log(data);
        var chartDiv = document.getElementById(data['name_div']);
        var dataY1 = {
            'x' : data['data_x'][0],
            'y': data['data_y'][0],
             type: 'scatter',
             name: data['name_data_line_1']

        };
        if (data['data_y'].length == 2) {
            var dataY2 = {
                'x': data['data_x'][0],
                'y': data['data_y'][1],
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
        if (steepshot.classBtn.attr('id') !== btn.id) {
            $(btn).css({
            background: '#fe6637',
            color: '#fff'
        });
          $(steepshot.classBtn).css({
              background: '#f6f6fb',
              color: '#fe6637'
          });
          steepshot.classBtn = $('#' + btn.id);
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
