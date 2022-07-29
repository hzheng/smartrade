import React from 'react';

import { FormattedDate, FormattedNumber } from 'react-intl';

export function FormattedField({ value, style, className, tag, timeZone, time }) {
  const props = { style, value };
  let Formatter = FormattedNumber;
  let classVal = className || "";
  switch (style) {
    case 'currency':
      props['currency'] = "USD";
      classVal += " amount currency"
      break;
    case 'percent':
      props['minimumFractionDigits'] = 2;
      classVal += " amount percent"
      break;
    case 'date':
      Formatter = FormattedDate;
      props['day'] = "2-digit";
      props['month'] = "2-digit";
      props['year'] = "numeric";
      if (time) {
        props['hour'] = "2-digit";
        props['minute'] = "2-digit";
        props['second'] = "2-digit";
      }
      if (timeZone) {
        props['timeZone'] = timeZone;
      }
      classVal += " date"
      break;
    default:
  }
  if (typeof (value) == 'number' && value < 0) {
    classVal += " negative";
  }
  const fieldProps = { className: classVal };
  if (tag == "") {
    return (<>{value == null ? "N/A" : <Formatter {...props} />}</>);
  }

  const CustomTag = tag || 'td';
  return (<CustomTag {...fieldProps}>
    {value == null ? "N/A" : <Formatter {...props} />}
  </CustomTag>);
}
