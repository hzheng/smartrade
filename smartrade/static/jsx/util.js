export async function fetchData(url, options, onOk, onError, onException) {
  console.log(`fetching data from ${url}...`);
  await fetch(url, options).then((response) => {
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
