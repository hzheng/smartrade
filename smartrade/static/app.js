'use strict';

const app = {
    loadPage: function (baseUrl, $tab) {
        if ($tab.data("loaded")) {
            console.log("loaded");
            return;
        }
        const tabContentId = $tab.attr('href');
        const $tabContent = $(tabContentId);
        const accountId = tabContentId.split("-")[1];
        const url = baseUrl + "?ajax=1&account=" + accountId;
        console.log("loading", url);
        let loadFunction;
        switch (baseUrl) {
            case '/home':
                loadFunction = "_loadAccountSummary";
                break;
            case '/transactionGroups':
                loadFunction = "_initLoadTransactionGroups";
                break;
            case '/transactions':
                loadFunction = "_initLoadTransactions";
                break;
            default:
                console.assert(false, "unknown url:" + baseUrl);
        }
        $.get(url, data => app[loadFunction](data, $tab, $tabContent));
    },

    _loadAccountSummary: function (data, $tab, $tabContent) {
        for (const [key, value] of Object.entries(data.summary)) {
            app.setValue($('td[name="' + key + '"]', $tabContent), value);
        }
        const $rows = $('tr[name="position"]', $tabContent);
        const $total = $('td[name="total_value"]', $tabContent);
        for (let i = 0; i < 2; i++) {
            const $row = $rows.eq(i);
            for (const [symbol, [quantity, price, value]] of Object.entries(data.values[i])) {
                const $newRow = $row.clone().insertBefore($row);
                app.setValue($('td[name="symbol"]', $newRow), symbol);
                app.setValue($('td[name="quantity"]', $newRow), quantity);
                app.setValue($('td[name="price"]', $newRow), price);
                app.setValue($('td[name="value"]', $newRow), value);
            }
            app.setValue($total.eq(i), data.values[i + 2]);
            $row.remove();
        }
        app._commonLoad(data, $tab, $tabContent);
    },
    
    _initLoadTransactionGroups: function (data, $tab, $tabContent) {
        const $select = $('select[name="ticker"]', $tabContent);
        for (const [_, ticker] of Object.entries(data.tickers)) {
            $('<option>').val(ticker).text(ticker).appendTo($select);
        }
        app._commonLoad(data, $tab, $tabContent);
    },
    
    _initLoadTransactions: function (data, $tab, $tabContent) {
        const $select = $('select[name="ticker"]', $tabContent);
        for (const [_, ticker] of Object.entries(data.tickers)) {
            $('<option>').val(ticker).text(ticker).appendTo($select);
        }
        app._commonLoad(data, $tab, $tabContent);
    },

    _commonLoad: function (data, $tab, $tabContent) {
        app.setValue($('span[name="start_time"]', $tabContent), data.period[0]);
        app.setValue($('span[name="end_time"]', $tabContent), data.period[1]);
        $tab.data("loaded", true);
    },

    convertAmount: function(amount) {
        if (!amount) return "0.00";

        if (typeof(amount) == 'number') {
            return amount.toFixed(2);
        }
        return amount;
    },

    convertDate: function(date, format) {
        const dataObj = new Date(Date.parse(date));
        if (!format) {
            format = 'yy-mm-dd';
        }
        return $.datepicker.formatDate(format, dataObj);
    },

    setValue: function($field, value, isAmount) {
        if ($field.hasClass('date')) {
            $field.text(app.convertDate(value, $field.attr('format')));
            return;
        }
        if (!isAmount && !$field.hasClass('amount')) {
            $field.text(value);
            return;
        }
        if (value == null) {
            $field.text("N/A");
            return;
        }
        if (isAmount && typeof(value) == 'string') {
            value = parseInt(value);
        }
        console.assert(typeof(value) == 'number');
        let postfix = "";
        if ($field.hasClass('percent')) {
            value *= 100;
            postfix = "%";
        }
        const amountStr = app.convertAmount(value);
        $field.text(amountStr + postfix);
        if (amountStr.startsWith("-")) {
            $field.addClass('negative');
        } else {
            $field.removeClass('negative');
        }
    },

    _fillTransactionGroupData: function($row, tx) {
        const $cell = $row.children("td");
        let index = $cell.length - 1;
        app.setValue($cell.eq(index--), tx.amount);
        app.setValue($cell.eq(index--), tx.fee);
        $cell.eq(index--).text(tx.quantity);
        app.setValue($cell.eq(index--), tx.price);
        $cell.eq(index--).text(tx.action);
        app.setValue($cell.eq(index--), tx.date);
    },

    searchTransactionGroups: function($form, afterSuccess) {
        const url = $form.attr('action');
        $('input[name="ajax"]', $form).val(2);
        const $tabContent = $form.closest("div.ui-tabs-panel");
        const tabContentId = $tabContent.attr("id");
        const accountId = tabContentId.split("-")[1];
        $('input[name="account"]', $form).val(accountId);

        const transactionGroupSelector = ".tx_group";
        const positionSelector = "table.positions tr";
        $.ajax({
            type: "GET",
            url: url,
            data: $form.serialize(),
            success: function (data) {
                app.setValue($("span[name='totalProfit']", $tabContent), data.profit);
                const ticker = $('select[name="ticker"]', $form).val();
                const positions = data.positions[ticker];
                const $positionTemplate = $(positionSelector, $tabContent).eq(0);
                $(positionSelector + ":gt(0)", $tabContent).remove();
                const hasPositions = (Object.keys(positions).length > 0);
                if (hasPositions) {
                    let $prevPosition = $positionTemplate;
                    for (const [symbol, quantity] of Object.entries(positions)) {
                        let $curPosition = $positionTemplate.clone();
                        $curPosition.insertAfter($prevPosition);
                        $(".symbol", $curPosition).text(symbol);
                        $(".quantity", $curPosition).text(quantity);
                        $prevPosition = $curPosition;
                    }
                }
                $('.none', $positionTemplate.closest('div')).css(
                    "display", hasPositions ? 'none' : 'block');

                const $sectionTemplate = $(transactionGroupSelector, $tabContent).eq(0);
                const $tableTemplate = $("table", $sectionTemplate).eq(0);
                let $prevSection = $sectionTemplate;
                $(transactionGroupSelector + ":gt(0)", $tabContent).remove();
                data.transactionGroups.forEach(function (group) {
                    const $curSection = $sectionTemplate.clone();
                    $curSection.insertAfter($prevSection);
                    $curSection.css("display", "block");

                    group.chains.forEach(function (chain, chainIndex) {
                        if (chainIndex > 0) {
                            const $prevTable = $("table", $curSection).last();
                            const $newTable = $tableTemplate.clone().insertAfter($prevTable);
                            $("tr[name='header']", $newTable).remove();
                        }
                        chain.forEach(function (tx, txIndex) {
                            let $row;
                            if (txIndex == 0) { // open transaction
                                $row = $("tr.open", $curSection).last();
                                $row.children("td").eq(0).text(tx.symbol);
                            } else { // close transactions
                                let $prevRow = $("tr.close", $curSection).last();
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
                    app.setValue($('span[name="profit"]', $curSection), group.profit);
                    app.setValue($('span[name="roi"]', $curSection), group.roi);
                    app.setValue($('span[name="cost"]', $curSection), group.cost);
                    app.setValue($('span[name="duration"]', $curSection), group.duration);
                    $prevSection = $curSection;
                });
                if (afterSuccess) {
                    afterSuccess(ticker);
                }
            }
        });
    },

    searchTransactionHistory: function($form, afterSuccess) {
        const url = $form.attr('action');
        $('input[name="ajax"]', $form).val(2);
        const $tabContent = $form.closest("div.ui-tabs-panel");
        const tabContentId = $tabContent.attr("id");
        const accountId = tabContentId.split("-")[1];
        $('input[name="account"]', $form).val(accountId);

        if ($('.customDate', $tabContent).css('visibility') != 'hidden') {
            const startDate = $("input[name='start_date']", $tabContent).val();
            const endDate = $("input[name='end_date']", $tabContent).val();
            $("option[name='custom']").val(startDate + ',' + endDate);
        }
        $.ajax({
            type: "GET",
            url: url,
            data: $form.serialize(),
            success: function (data) {
                const $tbody = $('table.history tbody', $tabContent);
                $tbody.empty();
                const transactions = data['transactions'];
                const cash = data['cash'];
                $('.history_summary span', $tabContent).each(function () {
                    const splitAttr = $(this).attr("name").split("_");
                    if (splitAttr[0] == 'cash') {
                        app.setValue($(this), cash[splitAttr[1]]);
                    } else {
                        app.setValue($(this), transactions.length);
                    }
                })
                transactions.forEach(function (tx, index) {
                    const $amount = $('<td>').text(tx.amount);
                    const $row = $('<tr>').append(
                        $('<td>').text(index + 1),
                        $('<td>').text(tx.date),
                        $('<td>').text(tx.symbol),
                        $('<td>').text(tx.action),
                        $('<td>').text(tx.price),
                        $('<td>').text(tx.quantity),
                        $('<td>').text(tx.fee),
                        $amount,
                        $('<td>').text(tx.description)
                    ).appendTo($tbody);
                    app.setValue($amount, tx.amount, true);
                });
                if (afterSuccess) {
                    afterSuccess();
                }
            }
        });
    }
}

$(function() {
    // set up tabs
    const $accounts = $("#accounts").tabs();
    $("ul li a", $accounts).click(function() {
        app.loadPage($accounts.attr('url'), $(this));
    })[0].click(); // load the first tab content

    // set up account summary
    const $accountTemplates = $("#account_template section");
    $("div", $accounts).each(function() {
        const $wrapper = $(this);
        $accountTemplates.each(function() {
            $(this).clone().appendTo($wrapper);
        });
    });

    // set up transaction groups
    const $transactionGroupTemplates = $("#transaction_group_template").children();
    $("div", $accounts).each(function() {
        const $tabContent = $(this);
        $transactionGroupTemplates.each(function() {
            $(this).clone().appendTo($tabContent);
        });

        const $form = $('form[name="searchTransactionGroupForm"]', $tabContent);
        const $btn = $('button[name="searchTransactionGroupBtn"]', $tabContent);
        $('select[name="ticker"]', $form).on('change', function (e) {
            $btn.prop("disabled", $(this).val() == "");
        });
        $btn.click(function (e) {
            e.preventDefault();
            app.searchTransactionGroups($form,
                function (ticker) {
                    $('.transaction_group_summary span.ticker', $tabContent).text(ticker);
                })
        });
    });

    // set up transaction history
    const $transactionTemplates = $("#transaction_template").children();
    $("div", $accounts).each(function() {
        const $tabContent = $(this);
        $transactionTemplates.each(function() {
            $(this).clone().appendTo($tabContent);
        });

        $("input[name='start_date']", $tabContent).datepicker();
        $("input[name='end_date']", $tabContent).datepicker();

        $("button[name='searchTransactionBtn']", $tabContent).click(function (e) {
            e.preventDefault();
            app.searchTransactionHistory($(this).closest('form'))
        });
        $("span[name='dateOrderArrow']", $tabContent).on('click', function (e) {
            const dateOrderInput = $("input[name='dateOrder']", $tabContent);
            const cur = dateOrderInput.val();
            dateOrderInput.val(1 - parseInt(cur));
            const $arrow = $(this);
            app.searchTransactionHistory($("form[name='searchTransactionForm']", $tabContent),
                function () {
                    $arrow.toggleClass("ui-icon-triangle-1-s")
                        .toggleClass("ui-icon-triangle-1-n");
                })
        });
        $("select[name='dateRange']", $tabContent).on('change', function (e) {
            const optionSelected = $("option:selected", this);
            $('.customDate', $tabContent).css('visibility',
                optionSelected.attr('name') == 'custom' ? 'visible' : 'hidden');
        });
    });
});