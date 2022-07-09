'use strict';

const app = {
    /** load page at the first stage */
    loadPage: function (baseUrl, $tab) {
        if ($tab.data("loaded")) {
            console.log("loaded");
            return;
        }
        const tabContentId = $tab.attr('href');
        const accountId = app.getAccountId(tabContentId);
        const url = baseUrl + "?ajax=1&account=" + accountId;
        let loadFunction;
        switch (baseUrl) {
            case '/': case'/home':
                loadFunction = "_loadAccountSummary";
                break;
            case '/transactionGroups':
                loadFunction = "_initLoadTransactionGroups";
                break;
            case '/transactions':
                loadFunction = "_initLoadTransactions";
                break;
            case '/balances':
                loadFunction = "_initLoadBalances";
                break;
            default:
                console.assert(false, "unknown url: " + baseUrl);
        }
        const $tabContent = $(tabContentId);
        app.showMessage($tabContent, "Loading page " + url + "...");
        $.ajax({
            type: "GET",
            url: url,
            success: data => app[loadFunction](data, $tab, $tabContent),
            error: function (xhr, textStatus, errorThrown) {
                app.showMessage($tabContent, "Failed to load " + url + ": " + errorThrown, true);
            }
        });
    },

    _loadAccountSummary: function (data, $tab, $tabContent) {
        const $derived = $('section.derived', $tabContent);
        let $rows = $('tr[name="position"]', $derived);
        let $total = $('td[name="total_value"]', $derived);
        for (let i = 0; i < 2; i++) {
            const $row = $rows.eq(i);
            for (const [symbol, [quantity, price, value]] of Object.entries(data.values[i])) {
                const $newRow = $row.clone().insertBefore($row);
                app.setValue($("td[name='symbol']", $newRow), symbol);
                app.setValue($("td[name='quantity']", $newRow), quantity);
                app.setValue($("td[name='price']", $newRow), price);
                app.setValue($("td[name='value']", $newRow), value);
            }
            app.setValue($total.eq(i), data.values[i + 2]);
            $row.remove();
        }

        const accountInfo = data.accountInfo;
        const balance = accountInfo.balance;
        const $broker = $('section.broker', $tabContent);
        if (balance) {
            $broker.show();
            const stockValue = balance.stock_value;
            const optionValue = balance.option_value;
            for (const [key, value] of Object.entries(balance)) {
                //console.log(key, "=>", value);
                app.setValue($('td[name="' + key + '"]', $broker), value);
            }
            const marketValue = balance.account_value;
            const cost = data.summary.total_investment;
            const profit = marketValue - cost;
            app.setValue($('td[name="profit"]', $broker), profit);
            app.setValue($('td[name="profit_rate"]', $broker), profit / cost);
            // show positions
            $rows = $('tr[name="position"]', $broker);
            $total = $('td[name="total_value"]', $broker);
            const positions = accountInfo.positions;
            positions.sort((p, q) => p.symbol > q.symbol ? 1 : -1);
            for (let i = 0; i < 2; i++) {
                const $row = $rows.eq(i);
                for (const pos of positions) {
                    const symbol = pos.symbol;
                    const isOption = symbol.indexOf("_") >= 0;
                    if (isOption ^ (i > 0)) { continue; }

                    const $newRow = $row.clone().insertBefore($row);
                    const k = isOption ? 100 : 1;
                    app.setValue($("td[name='symbol']", $newRow), symbol);
                    app.setValue($("td[name='quantity']", $newRow), pos.quantity);
                    app.setValue($("td[name='cost']", $newRow), pos.cost);
                    app.setValue($("td[name='price']", $newRow), pos.price / k);
                    app.setValue($("td[name='day_gain']", $newRow), pos.day_gain);
                    app.setValue($("td[name='day_gain_percent']", $newRow), pos.day_gain_percent / 100);
                    const marketValue = pos.quantity * pos.price;
                    const totalCost = pos.cost * pos.quantity * k;
                    const gain = marketValue - totalCost;
                    app.setValue($("td[name='gain']", $newRow), gain);
                    app.setValue($("td[name='gain_percent']", $newRow), gain / totalCost);
                    app.setValue($("td[name='value']", $newRow), marketValue);
                }
                app.setValue($total.eq(i), i == 0 ? stockValue : optionValue);
                $row.remove();
            }
        }
        for (const [key, value] of Object.entries(data.summary)) { // may override the above values
            app.setValue($('td[name="' + key + '"]', $tabContent), value);
        }
        app._commonLoad(data, $tab, $tabContent);
    },
    
    _loadTransactionInfo: function (data, $tab, $tabContent) {
        const $select = $('select[name="ticker"]', $tabContent);
        for (const [ticker, hasPosition] of Object.entries(data.positions)) {
            if (hasPosition) {
                $('<option>').val(ticker).text("*" + ticker).appendTo($select);
            }
        }
        for (const [ticker, hasPosition] of Object.entries(data.positions)) {
            if (!hasPosition) {
                $('<option>').val(ticker).text(ticker).appendTo($select);
            }
        }
        app._commonLoad(data, $tab, $tabContent);
    },
    
    _initLoadTransactionGroups: function (data, $tab, $tabContent) {
        app._loadTransactionInfo(data, $tab, $tabContent);
    },
    
    _initLoadTransactions: function (data, $tab, $tabContent) {
        app._loadTransactionInfo(data, $tab, $tabContent);
    },

    _commonLoad: function (data, $tab, $tabContent) {
        app.setValue($("span[name='start_time']", $tabContent), data.period[0]);
        app.setValue($("span[name='end_time']", $tabContent), data.period[1]);
        $tab.data("loaded", true);
        app.showMessage($tabContent, "Loaded page");
    },

    convertQuantity: function(quantity) {
        if (!quantity) return "0";

        if (typeof(quantity) != 'number') {
             return quantity;
        }

        let q = quantity.toFixed(6).toString();
        let i = q.length - 1;
        outer:
        for (; i >= 0; i--) {
            switch (q.charAt(i)) {
                case '0':
                    break;
                case '.':
                    i--;
                    break outer;
                default:
                    break outer;
            }
        }
        return q.substring(0, i + 1);
    },

    convertAmount: function(amount) {
        if (!amount) return "0.00";

        if (typeof(amount) == 'number') {
            return amount.toFixed(2).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
        }
        return amount;
    },

    convertDate: function(date, format) {
        if (!date) {
            return "";
        }
        const dateObj = new Date(Date.parse(date));
        if (!format) {
            format = 'yy-mm-dd';
        }
        const times = format.split(" ")
        let res = $.datepicker.formatDate(times[0], dateObj);
        if (times.length > 1) {
            const zeroPad = (num) => String(num).padStart(2, '0');
            let h = zeroPad(dateObj.getHours());
            let m = zeroPad(dateObj.getMinutes());
            let s = zeroPad(dateObj.getSeconds());
            res += " " + h + ":" + m + ":" + s;
        }
        return res;
    },

    setValue: function($field, value, dataType) {
        if ($field.hasClass('date') || dataType == 'date') {
            $field.text(app.convertDate(value, $field.attr('format')));
            return $field;
        }
        if ($field.hasClass('quantity') || dataType == 'quantity') {
            $field.text(app.convertQuantity(value));
            return $field;
        }
        const isPercentType = (dataType == 'percent' || $field.hasClass('percent'));
        if (dataType != 'amount' && !$field.hasClass('amount') && !isPercentType) {
            $field.text(value);
            return $field;
        }
        if (value == null) {
            $field.text("N/A");
            return $field;
        }
        console.assert(typeof(value) == 'number');
        let postfix = "";
        if (isPercentType) {
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
        return $field;
    },

    searchTransactionGroups: function($form, afterSuccess) {
        const url = $form.attr('action');
        $('input[name="ajax"]', $form).val(2);
        const $tabContent = $form.closest("div.ui-tabs-panel");
        const tabContentId = $tabContent.attr("id");
        const accountId = app.getAccountId(tabContentId);
        const $searchResult = $(".search_result", $tabContent);
        $('input[name="account"]', $form).val(accountId);

        const transactionGroupSelector = ".tx_group";
        const positionSelector = "table.positions tbody tr";
        app.showMessage($tabContent, "Loading transaction groups...");
        $.ajax({
            type: "GET",
            url: url,
            data: $form.serialize(),
            success: function (data) {
                $searchResult.css("visibility", "visible");
                app.setValue($("span[name='totalProfit']", $tabContent), data.profit);
                const ticker = $('select[name="ticker"]', $form).val();
                app.setValue($("span[name='tickerPrice']", $tabContent), data.prices[ticker][0]);
                app.setValue($("span[name='tickerPerChange']", $tabContent), data.prices[ticker][2] / 100);
                const positions = data.positions[ticker];
                const $positionTemplate = $(positionSelector, $tabContent).eq(0);
                $(positionSelector + ":gt(0)", $tabContent).remove();
                const hasPositions = (Object.keys(positions).length > 0);
                if (hasPositions) {
                    let $prevPosition = $positionTemplate;
                    for (const [symbol, quantity] of Object.entries(positions)) {
                        let $curPosition = $positionTemplate.clone().css("display", "");
                        $curPosition.insertAfter($prevPosition);
                        $(".symbol", $curPosition).text(symbol);
                        $(".quantity", $curPosition).text(quantity);
                        app.setValue($("td[name='price']", $curPosition), data.prices[symbol][0]);
                        app.setValue($("td[name='change']", $curPosition), data.prices[symbol][1]);
                        app.setValue($("td[name='perChange']", $curPosition), data.prices[symbol][2] / 100);
                        $prevPosition = $curPosition;
                    }
                }
                $positionTemplate.closest('table').css(
                    "display", hasPositions ? 'block' : 'none');
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
                            } else { // close transactions
                                let $prevRow = $("tr.close", $curSection).last();
                                $row = $prevRow.clone();
                                $row.insertAfter($prevRow);
                                $row.css("display", "");
                            }
                            $row.children("td").each(function() {
                                app.setValue($(this), tx[$(this).attr('name')]);
                            });
                        });
                    });
                    if (group.completed) {
                        $('table.transaction', $curSection).addClass("completed").parent()
                            .toggle($("input[name='showCompleted']", $form).is(':checked'));
                    }
                    $("div.summary span", $curSection).each(function() {
                        app.setValue($(this), group[$(this).attr('name')]);
                    })
                    $prevSection = $curSection;
                });
                app.showMessage($tabContent, "Loaded transaction groups");
                if (afterSuccess) {
                    afterSuccess(ticker);
                }
            },
            error: function (xhr, textStatus, errorThrown) {
                app.showMessage($tabContent, "Failed to load transaction groups: " + errorThrown, true);
            }
        });
    },

    searchTransactionHistory: function($form, afterSuccess) {
        const url = $form.attr('action');
        $('input[name="ajax"]', $form).val(2);
        const $tabContent = $form.closest("div.ui-tabs-panel");
        const tabContentId = $tabContent.attr("id");
        const accountId = app.getAccountId(tabContentId);
        $('input[name="account"]', $form).val(accountId);

        if ($('.customDate', $tabContent).css('visibility') != 'hidden') {
            const startDate = $("input[name='start_date']", $tabContent).val();
            const endDate = $("input[name='end_date']", $tabContent).val();
            $("option[name='custom']").val(startDate + ',' + endDate);
        }
        app.showMessage($tabContent, "Loading transaction history...");
        $.ajax({
            type: "GET",
            url: url,
            data: $form.serialize(),
            success: function (data) {
                const $tbody = $('table.history tbody', $tabContent);
                $tbody.empty();
                const transactions = data['transactions'];
                const cash = data['cash'];
                $('.history_summary>span', $tabContent).each(function () {
                    const splitAttr = $(this).attr("name").split("_");
                    if (splitAttr[0] == 'cash') {
                        app.setValue($(this), cash[splitAttr[1]]);
                    } else {
                        app.setValue($(this), transactions.length);
                    }
                })
                // const valid = $("select[name='valid']", $form).val();
                transactions.forEach(function (tx, index) {
                    // console.log("_id=" + tx._id + ";merge=" + tx.merge_parent + ";slice=" + tx.slice_parent);
                    const isSliced = tx.slice_parent && tx.slice_parent != tx._id;
                    const isMerged = tx.merge_parent && tx.merge_parent != tx._id && tx.merge_parent != tx.slice_parent
                    const isVirtual = tx.merge_parent == tx._id || isSliced;
                    const isEffective = !isMerged && (tx.slice_parent != tx._id);
                    const $row = $('<tr>').append(
                        $('<td>').text(index + 1),
                        app.setValue($('<td>').attr('format', 'yy-mm-dd HH:mm:ss'), tx.date, 'date'),
                        $('<td>').text(tx.symbol),
                        $('<td>').text(tx.action),
                        app.setValue($('<td>'), tx.price, 'amount'),
                        app.setValue($('<td>'), tx.quantity, 'quantity'),
                        app.setValue($('<td>'), tx.fee, 'amount'),
                        app.setValue($('<td>'), tx.amount, 'amount'),
                        $('<td>').text(tx.description)
                    ).appendTo($tbody);
                    if (isVirtual) {
                        $row.addClass("virtual");
                    } else {
                        $row.addClass("original");
                    }
                    if (isEffective) {
                        $row.addClass("effective");
                    } else {
                        $row.addClass("ineffective");
                    }
                    if (isMerged) {
                        $row.addClass("merged");
                    }
                    if (isSliced) {
                        $row.addClass("sliced");
                    }
                    if (tx.valid <= 0) {
                        $row.addClass(tx.valid == 0 ? 'ignored' : 'invalid');
                    }
                    if (tx.grouped) {
                        $row.addClass("completed");
                    } else if (tx.grouped === false) {
                        $row.addClass("uncompleted");
                    }
                    $row.attr("id", tx._id);
                });
                app.showMessage($tabContent, "Loaded transaction history");
                if (afterSuccess) {
                    afterSuccess();
                }
            },
            error: function (xhr, textStatus, errorThrown) {
                app.showMessage($tabContent, "Failed to load transaction history: " + errorThrown, true);
            }
        });
    },

    searchBalanceHistory: function($form) {
        const url = $form.attr('action');
        $('input[name="ajax"]', $form).val(2);
        const $tabContent = $form.closest("div.ui-tabs-panel");
        const tabContentId = $tabContent.attr("id");
        const accountId = app.getAccountId(tabContentId);
        $('input[name="account"]', $form).val(accountId);

        if ($('.customDate', $tabContent).css('visibility') != 'hidden') {
            const startDate = $("input[name='start_date']", $tabContent).val();
            const endDate = $("input[name='end_date']", $tabContent).val();
            $("option[name='custom']").val(startDate + ',' + endDate);
        }
        app.showMessage($tabContent, "Loading balance history...");
        app._doSearchBalanceHistory(url, $form, $tabContent);
    },

    _doSearchBalanceHistory: async function(url, $form, $tabContent) {
        console.log("searching balance history...", new Date());
        const retry = (error) => {
            app.showMessage($tabContent, (error.statusText || error.message) + "; retrying...", true);
            setTimeout(() => app._doSearchBalanceHistory(url, $form, $tabContent), 10000);
        };
        const fail = error => {
            app.showMessage($tabContent, "Failed to load balance history: " + (error.statusText || error.message), true);
        }
        fetch(url + "?" + $form.serialize()).then(
            response => {
                if (response.status != 200) {
                    if (response.status == 502) { // timeout
                        retry(response);
                    } else {
                        fail(response);
                    }
                    return;
                }
                response.json().then(data => {
                    const $tbody = $('table.balance_history tbody', $tabContent);
                    $tbody.empty();
                    for (const [date, [bal, actual_bal]] of Object.entries(data.balances)) {
                        let diff = null;
                        if (actual_bal) {
                            diff = (bal - actual_bal) / actual_bal;
                        }
                        const $row = $('<tr>').append(
                            app.setValue($('<td>'), date, 'date'),
                            app.setValue($('<td>'), bal, 'amount'),
                            app.setValue($('<td>'), actual_bal, 'amount'),
                            app.setValue($('<td>'), diff, 'percent')
                        ).appendTo($tbody);
                    };
                    app.showMessage($tabContent, "Loaded balance history");
                }).catch(fail);
            }).catch(error => {
                if (error instanceof TypeError) { // timeout
                    retry(error);
                } else {
                    console.log("err:", error);
                    fail(error);
                }
            });
    },

    uploadBalanceHistory: function($form) {
        const url = $form.attr('action');
        const $tabContent = $form.closest("div.ui-tabs-panel");
        const tabContentId = $tabContent.attr("id");
        const accountId = app.getAccountId(tabContentId);
        $('input[name="account"]', $form).val(accountId);
        $.ajax({
            url: url,
            type: 'POST',
            data: new FormData($form[0]),
            cache: false,
            contentType: false,
            processData: false,
            xhr: function () {
                var myXhr = $.ajaxSettings.xhr();
                if (myXhr.upload) {
                    myXhr.upload.addEventListener('progress', function (e) {
                        if (e.lengthComputable) {
                            $('progress').attr({
                                value: e.loaded,
                                max: e.total,
                            });
                        }
                    }, false);
                }
                return myXhr;
            }
        });
    },

    initAccountSummary: function($tabContents) {
        const $accountTemplates = $("#account_template section");
        $tabContents.each(function () {
            const $tabContent = $(this);
            $accountTemplates.each(function () {
                $(this).clone().appendTo($tabContent);
            });
        });
    },

    initTransactionGroups: function($tabContents) {
        const $transactionGroupTemplates = $("#transaction_group_template").children();
        $tabContents.each(function () {
            const $tabContent = $(this);
            $transactionGroupTemplates.each(function () {
                $(this).clone().appendTo($tabContent);
            });

            const $form = $('form[name="searchTransactionGroupForm"]', $tabContent);
            $("select[name='ticker']", $form).on('change', function (e) {
                if (!$(this).val()) {
                    $(".search_result", $tabContent).css("visibility", "hidden");
                    return;
                }
                app.searchTransactionGroups($form,
                    function (ticker) {
                        $('.transaction_group_summary span.ticker', $tabContent).text(ticker);
                    });
            });

            $("input[name='showCompleted']", $form).on('click', function (e) {
                $(".completed", $form.closest(".account_content")).parent().toggle();
            });
        });
    },

    initTransactionHistory: function($tabContents) {
        const $transactionTemplates = $("#transaction_template").children();
        $tabContents.each(function () {
            const $tabContent = $(this);
            $transactionTemplates.each(function () {
                $(this).clone().appendTo($tabContent);
            });

            $("input[name='start_date']", $tabContent).datepicker();
            $("input[name='end_date']", $tabContent).datepicker();

            $("button[name='searchTransactionBtn']", $tabContent).click(function (e) {
                e.preventDefault();
                e.stopPropagation();
                e.stopImmediatePropagation();
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
    },
    
    initBalanceHistory: function($tabContents) {
        const $balTemplates = $("#balance_template").children();
        $tabContents.each(function () {
            const $tabContent = $(this);
            $balTemplates.each(function () {
                $(this).clone().appendTo($tabContent);
            });
            $("input[name='start_date']", $tabContent).datepicker();
            $("input[name='end_date']", $tabContent).datepicker();
            $("button[name='searchBalanceBtn']", $tabContent).click(function (e) {
                e.preventDefault();
                e.stopPropagation();
                e.stopImmediatePropagation();
                app.searchBalanceHistory($(this).closest('form'));
            });
            $("select[name='dateRange']", $tabContent).on('change', function (e) {
                const optionSelected = $("option:selected", this);
                $('.customDate', $tabContent).css('visibility',
                    optionSelected.attr('name') == 'custom' ? 'visible' : 'hidden');
            });
            $(":file", $tabContent).on('change', function () {
                //var file = this.files[0];
            });
            $(":button", $tabContent).click(function (e) {
                e.preventDefault();
                app.uploadBalanceHistory($(this).closest('form'));
            });
        });
    },

    _initLoadBalances: function (data, $tab, $tabContent) {
        console.log("data", data);
        app._commonLoad(data, $tab, $tabContent);
        const $content = $(".balance_summary", $tabContent);
        // $content.append("cash=" + data.balance[1] + "<br/>");
        // $content.append("balance=" + data.balance[2] + "<br/>");
        // for (const [key, value] of Object.entries(data.balance[0])) {
        //     $content.append(key + "=>" + value + "<br/>");
        // }
    },

    initLoad: function($tabContents) {
        $tabContents.each(function () {
            const $tabContent = $(this);
            $(".load a", $tabContent).each(function () {
                const $link = $(this);
                const url = $link.attr('href');
                $link.click(function (e) {
                    e.preventDefault();
                    app.showMessage($tabContent, "Loading transaction data...");
                    $.ajax({
                        url: url, type: 'GET',
                        success: function (data, textStatus) {
                            app.showMessage($tabContent, "Loaded "
                             + data.transactions + " transaction(s) and " + data.transactionGroups + " transaction group(s)");
                        },
                        error: function (xhr, textStatus, errorThrown) {
                            app.showMessage($tabContent, "Failed to load: " + errorThrown, true);
                        }
                    });
                });
            });
        });
    },

    showMessage: function ($context, message, error) {
        const $messageBoard = $(".message", $context);
        $messageBoard.text(message);
        if (error) {
            $messageBoard.addClass("error");
        } else {
            $messageBoard.removeClass("error");
            if (!message.endsWith("...")) {
                setTimeout(() => $messageBoard.text(''), 10000);
            }
        }
    },

    getAccountId: function (value) {
        const accountId = value.split("-")[1];
        console.assert(accountId);
        return accountId;
    }
}

$(function() {
    // set up outer tabs
    const $accounts = $("#accounts").tabs();
    const $tabs = $(">ul li a", $accounts);
    let initAccount = $accounts.attr('init_account');
    if (!initAccount) {
        initAccount = app.getAccountId($tabs.eq(0).attr("href"));
    }
    $tabs.click(function () {
        const url = $accounts.attr('url');
        app.loadPage(url, $(this));
        const accountId = app.getAccountId($(this).attr('href'));
        window.history.replaceState("", "", url + "?account=" + accountId);
    }).each(function () {
        if ($(this).attr("href").endsWith(initAccount)) {
            $(this).click();
        }
    });
 
    // set up inner tabs
    $("ul.account_nav li:not(.load) a", $accounts).click(function (e) {
        if ($(this).parent().hasClass('ui-tabs-active')) {
            e.preventDefault();
            return;
        }
        const accountId = app.getAccountId($(this).closest("div").attr('id'));
        $(this).attr('href', $(this).attr('href') + "?account=" + accountId);
    });

    // set up pages
    const $tabContents = $("div", $accounts);
    app.initAccountSummary($tabContents);
    app.initTransactionGroups($tabContents);
    app.initTransactionHistory($tabContents);
    app.initBalanceHistory($tabContents);
    app.initLoad($tabContents);
});