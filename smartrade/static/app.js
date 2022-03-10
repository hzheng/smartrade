'use strict';

var app = {
    convertAmount: function(amount) {
        if (!amount) return "0.00";

        if (typeof(amount) == 'number') {
            return amount.toFixed(2);
        }
        return amount;
    },

    setAmount: function($field, amount, postfix) {
        var amountStr = app.convertAmount(amount);
        $field.text(amountStr + (postfix ? postfix : ""));
        if (amountStr.startsWith("-")) {
            $field.addClass('negative');
        } else {
            $field.removeClass('negative');
        }
    },

    setPercentage: function($field, amount) {
        if (!amount) {
            $field.text("N/A");
        } else {
            app.setAmount($field, amount * 100, '%');
        }
    },

    convertDate: function(date, format) {
        var dataObj = new Date(Date.parse(date));
        if (!format) {
            format = 'yy-mm-dd';
        }
        return $.datepicker.formatDate(format, dataObj);
    },

    _fillTransactionGroupData: function($row, tx) {
        var $cell = $row.children("td");
        var index = $cell.length - 1;
        app.setAmount($cell.eq(index--), tx.amount);
        app.setAmount($cell.eq(index--), tx.fee);
        $cell.eq(index--).text(tx.quantity);
        app.setAmount($cell.eq(index--), tx.price);
        $cell.eq(index--).text(tx.action);
        $cell.eq(index).text(app.convertDate(tx.date));
    },

    searchTransactionGroups: function($form, afterSuccess) {
        var url = $form.attr('action');
        $('input[name="ajax"]', $form).val(true);
        var transactionGroupSelector = "section.tx_group";
        var positionSelector = "table.positions tr";
        $.ajax({
            type: "GET",
            url: url,
            data: $form.serialize(),
            success: function (data) {
                app.setAmount($("span[name='totalProfit']"), data.profit);
                var ticker = $('select[name="ticker"]', $form).val();
                var positions = data.positions[ticker];
                var $positionTemplate = $(positionSelector).eq(0);
                $(positionSelector + ":gt(0)").remove();
                var hasPositions = (Object.keys(positions).length > 0);
                if (hasPositions) {
                    var $prevPosition = $positionTemplate;
                    for (const [symbol, quantity] of Object.entries(positions)) {
                        var $curPosition = $positionTemplate.clone();
                        $curPosition.insertAfter($prevPosition);
                        $(".symbol", $curPosition).text(symbol);
                        $(".quantity", $curPosition).text(quantity);
                        $prevPosition = $curPosition;
                    }
                }
                $('.none', $positionTemplate.closest('div')).css(
                    "display", hasPositions ? 'none' : 'block');

                var $sectionTemplate = $(transactionGroupSelector).eq(0);
                var $tableTemplate = $("table", $sectionTemplate).eq(0);
                var $prevSection = $sectionTemplate;
                $(transactionGroupSelector + ":gt(0)").remove();
                data.transactionGroups.forEach(function (group) {
                    var $curSection = $sectionTemplate.clone();
                    $curSection.insertAfter($prevSection);
                    $curSection.css("display", "block");

                    group.chains.forEach(function (chain, chainIndex) {
                        if (chainIndex > 0) {
                            var $prevTable = $("table", $curSection).last();
                            var $newTable = $tableTemplate.clone().insertAfter($prevTable);
                            $("tr[name='header']", $newTable).remove();
                        }
                        chain.forEach(function (tx, txIndex) {
                            var $row;
                            if (txIndex == 0) { // open transaction
                                $row = $("tr.open", $curSection).last();
                                $row.children("td").eq(0).text(tx.symbol);
                            } else { // close transactions
                                var $prevRow = $("tr.close", $curSection).last();
                                $row = $prevRow.clone();
                                $row.insertAfter($prevRow);
                                $row.css("display", "");
                            }
                            app._fillTransactionGroupData($row, tx);
                        });
                    });
                    if (group.completed) {
                        $('table.transaction', $curSection).addClass("completed");
                    }
                    app.setAmount($('span[name="profit"]', $curSection), group.profit);
                    app.setPercentage($('span[name="roi"]', $curSection), group.roi);
                    app.setAmount($('span[name="cost"]', $curSection), group.cost);
                    $('span[name="duration"]', $curSection).text(group.duration);
                    $prevSection = $curSection;
                });
                if (afterSuccess) {
                    afterSuccess(ticker);
                }
            }
        });
    },

    searchTransactionHistory: function($form, afterSuccess) {
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
            success: function (data) {
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
                transactions.forEach(function (tx, index) {
                    var $amount = $('<td>').text(tx.amount).addClass('amount money');
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
                if (afterSuccess) {
                    afterSuccess();
                }
            }
        });
    }
}

$(function() {
    var $searchTransactionGroupForm = $("#searchTransactionGroupForm");
    var $searchTransactionGroupBtn = $("#searchTransactionGroupBtn");
    $('#ticker', $searchTransactionGroupForm).on('change', function (e) {
        $searchTransactionGroupBtn.prop("disabled", $(this).val() == "");
    });
    $searchTransactionGroupBtn.click(function(e) {
        e.preventDefault();
        app.searchTransactionGroups($(this).closest('form'),
            function (ticker) {
                $('.transaction_group_summary span.ticker').text(ticker);
            })
    });

    $("#searchTransactionBtn").click(function(e) {
        e.preventDefault();
        app.searchTransactionHistory($(this).closest('form'))
    });

    $('#date_order').on('click', function (e) {
        var dateOrderInput = $('input[name="dateOrder"]');
        var cur = dateOrderInput.val();
        dateOrderInput.val(1 - parseInt(cur));
        app.searchTransactionHistory($('#searchTransactionForm'), function() {
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