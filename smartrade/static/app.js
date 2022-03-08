var app = {
    historySearch: function($form, onSuccess) {
        var url = $form.attr('action');
        $('input[name="ajax"]', $form).val(true);
        if ($('.customDate').css('visibility') != 'hidden') {
            var startDate = $('#start_date').val();
            var endDate = $('#end_date').val();
            $('#custom').val(startDate + ',' + endDate);
        }

        $.ajax({
            type: "GET",
            url: url,
            data: $form.serialize(),
            success: function(data) {
                var $tbody = $('table.history tbody');
                $tbody.empty();
                // console.log(data)
                var transactions = data['transactions'];
                var $span = $('.history_summary span')
                $span.eq(0).text(transactions.length);
                var cash = data['cash'];
                $span.eq(1).text(cash.start);
                $span.eq(2).text(cash.end);
                $span.eq(3).text(cash.total);
                transactions.forEach(function(tx, index) {
                    var $amount = $('<td>').text(tx.amount).addClass('money');
                    if (tx.amount.startsWith("-")) {
                        $amount.addClass('negative');
                    }
                    $('<tr>').append(
                        $('<td>').text(index + 1),
                        $('<td>').text(tx.date),
                        $('<td>').text(tx.symbol).addClass('symbol'),
                        $('<td>').text(tx.action),
                        $('<td>').text(tx.price).addClass('money'),
                        $('<td>').text(tx.quantity),
                        $('<td>').text(tx.fee).addClass('money'),
                        $amount,
                        $('<td>').text(tx.description).addClass('description')
                    ).appendTo($tbody);
                  });
                  if (onSuccess) {
                      onSuccess();
                  }
            }
        });
    }
}

$(function() {
    $("#searchBtn").click(function(e) {
        e.preventDefault();
        app.historySearch($(this).parents('form:first'))
    });

    $('#date_order').on('click', function (e) {
        var dateOrderInput = $('input[name="dateOrder"]');
        var cur = dateOrderInput.val();
        dateOrderInput.val(1 - parseInt(cur));
        app.historySearch($('#searchForm'), function() {
            $('#date_order').toggleClass("ui-icon-triangle-1-s")
                .toggleClass("ui-icon-triangle-1-n");
        })
    });

    $("#start_date").datepicker();
    $("#end_date").datepicker();
    $('#dateRange').on('change', function (e) {
        var optionSelected = $("option:selected", this);
        $('.customDate').css('visibility', optionSelected.attr('id') == 'custom' ? 'visible' : 'hidden');
    });
});