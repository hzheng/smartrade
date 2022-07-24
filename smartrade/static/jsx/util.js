import $ from 'jquery';

export async function fetchData(url, onOk, onError, onException) {
  console.log(`fetching data from ${url}...`);
  await fetch(url).then((response) => {
    if (response.ok) {
      console.log("OK response from ", url, ":", response);
      response.json().then((data) => {
        console.log("OK data=", data);
        if (onOk) {
          onOk(data);
        }
      });
    } else {
      console.log("Error response from ", url, ":", response);
      response.text().then((data) => {
        console.log("Error data:", data);
        if (onError) {
          onError(data, response);
        }
      });
    }
  }).catch((error) => {
    console.log("No response from the server.", error);
    if (onException) {
      onException(error);
    }
  });
}

export function getElementData(element) {
  const data = {};
  for (const attr of element.attributes) {
    const [prefix, key, key2] = attr.nodeName.split("-");
    if (prefix != 'data') {
      continue;
    }
    const value = attr.nodeValue;
    if (!key2) {
      data[key] = value;
      continue;
    }
    const index = parseInt(key2);
    if (isNaN(index)) {
      if (!data[key]) {
        data[key] = {}
      }
      data[key][key2] = value;
    } else {
      if (!data[key]) {
        data[key] = []
      }
      data[key][index] = value;
    }
  }
  return data;
}

function convertQuantity(quantity) {
  if (!quantity) return "0";

  if (typeof (quantity) != 'number') {
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
}

function convertDate(date, format) {
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
}

function convertAmount(amount) {
  if (!amount) return "0.00";

  if (typeof (amount) == 'number') {
    return amount.toFixed(2).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
  }
  return amount;
}

export function setValue($field, value, dataType) {
  if ($field.hasClass('date') || dataType == 'date') {
    $field.text(convertDate(value, $field.attr('format')));
    return $field;
  }

  if ($field.hasClass('quantity') || dataType == 'quantity') {
    $field.text(convertQuantity(value));
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

  console.assert(typeof (value) == 'number');
  let postfix = "";
  if (isPercentType) {
    value *= 100;
    postfix = "%";
  }
  const amountStr = convertAmount(value);
  $field.text(amountStr + postfix);
  if (amountStr.startsWith("-")) {
    $field.addClass('negative');
  } else {
    $field.removeClass('negative');
  }
  return $field;
}

export function resetValues(context, fill) {
  $("td:not(.label)", context).text(fill);
}