import {Goods} from "src/store/berries_store/models";

export function parseReport(data) {
  const rows = [];
  const columns = [];
  const idxCol = {};
  columns.push({
    name: 'name',
    label: 'name',
    field: 'name',
  });
  const sumRow = {
    name: "итог"
  };
  if(false) {
    columns.push({
    name: ' sum, , , ',
    label: ' sum, , , ',
    field: ' sum, , , ',
    })
    idxCol[' sum, , , '] = true;
  }
  for (const client in data) {
    let client_id;// = data[client]["('', 'client_id', '', '', '')"];
    let comment;
    const row = {
      name: {
        client_id: null,
        value: client
      }
    };
    const cli_data = data[client];
    for (const good in cli_data) {
      //убираем скобки и апострофы
      let good_id = 0;
      let key = good.replace(/\(/g, "").replace(/\)/g, "").replace(/'/g, "");
      if (key.includes("client_id")) {
        client_id = cli_data[good]
      } else if (key.includes("comment")) {
        comment = cli_data[good];
      } else {
        const split = key.split(",");
        good_id = split[0];
        const goodObj = Goods.find(good_id);
        key = split.slice(1).join(",");
        row[key] = {
          good_id: good_id,
          // client_id: client_id,
          value: cli_data[good],
          // comment: comment
        };
        let key_sum = (sumRow[key] && sumRow[key].value) ?? 0;
        sumRow[key] = {
          value: key_sum + cli_data[good]
        }
        if (!idxCol[key]) {
          let col = {
            name: key,
            label: key,
            field: key,
            good_id: good_id,
            active: goodObj && goodObj.active
          };
          columns.push(col);
          idxCol[key] = true;
        }
      }
    }
    row.name.client_id = client_id;
    if(comment) {
      row.name.comment = comment;
    }
    rows.push(row)
  }
  rows.push(sumRow)
  return {rows: rows, columns: columns};
}
