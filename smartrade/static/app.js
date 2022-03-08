$(function () {
    $("#start_date").datepicker();
    $("#end_date").datepicker();
    $('#dateRange').on('change', function (e) {
        var optionSelected = $("option:selected", this);
        $('.customDate').css('visibility', optionSelected.attr('id') == 'custom' ? 'visible' : 'hidden');
    });

    $('#searchForm').on("submit", function(){
        if ($('.customDate').css('visibility') != 'hidden') {
            var startDate = $('#start_date').val();
            var endDate = $('#end_date').val();
            $('#custom').val(startDate + ',' + endDate);
        }
        return true;
      });

    $('#date_order').on('click', function (e) {
        var dateOrderInput = $('input[name="dateOrder"]');
        var cur = dateOrderInput.val();
        dateOrderInput.val(1 - parseInt(cur));
        $('#searchForm').submit();
    });
});

function setDateStyle(dateOrderArrow) {
    if ($(dateOrderArrow).val() == "1") {
        $('#date_order').removeClass("ui-icon-triangle-1-s").addClass("ui-icon-triangle-1-n");
    }
}