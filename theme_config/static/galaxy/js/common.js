export function dataFilterToArrayParams(data, filterTypes, filterTel, filterPrices) {
  const arrParams = []
  let filterCnt = 0
  let friendlyURL = "";
  let ignoreOldUrl = false;
  if (data.d && parseInt(data.d)!=0) {
    arrParams.push(`d=${data.d}`)
  }
  if (data.c && data.c.length > 0) {
    const cnt = data.c.split(',').length;
    filterCnt += cnt;
    // neu chi chon 1 category
    if (cnt===1 && friendlyURL==="") {
      const item = filterTypes.find((item) => item.c === data.c);
      friendlyURL = item?.link;
      ignoreOldUrl = true;
    } else {
      arrParams.push(`c=${data.c}`)
    }
  }
  if (data.t && data.t.length > 0) {
    const cnt = data.t.split(',').length;
    filterCnt += cnt;
    if (cnt===1) {
      const item = filterTel.find((item) => item.t === data.t);
      if (friendlyURL) {
        friendlyURL = `${friendlyURL}-${item?.link.replace('/sim-','')}`;
      } else {
        friendlyURL = item?.link;
      }
      ignoreOldUrl = true;
    } else {
      arrParams.push(`t=${data.t}`)
    }
  }
  if (data.notin && data.notin.length > 0) {
    arrParams.push(`notin=${data.notin}`)
    filterCnt += data.notin.split(',').length
  }
  if (data.s && data.s.length > 0) {
    arrParams.push(`s=${data.s}`)
  }
  if (data.yc && data.yc.length > 0) {
    arrParams.push(`yc=${data.yc}`)
    filterCnt += 1
  }
  if (data.cf && data.cf.length > 0) {
    arrParams.push(`cf=${data.cf}`)
    filterCnt += 1
  }
  if (data.h && data.h.length > 0) {
    arrParams.push(`h=${data.h}`)
    filterCnt += data.h.split(',').length
    if (!ignoreOldUrl) {
      if (friendlyURL) {
        friendlyURL = `${friendlyURL}-dau-so${data.h}}`;
      } else {
        friendlyURL = `/sim-dau-so-${data.h}`;
      }
      ignoreOldUrl = true;
    }
  }
  if (data.pr && data.pr.length > 0) {
    if(data.pr[0] ===",") {
      data.pr = data.pr.slice(1)
    }
    const newDataPrices = [...new Set(data.pr.split(","))].join(",")
    data.pr = newDataPrices

    const priceItems = newDataPrices.split(",");
    const cnt = priceItems.length;
    filterCnt += cnt;
    // neu chi chon 1 category
    if (cnt===1 && friendlyURL==="") {
      const item = filterPrices.find((item) => item.pr === priceItems[0]);
      friendlyURL = item?.link;
      ignoreOldUrl = true;
    } else {
      arrParams.push(`pr=${data.pr}`)
    }
    filterCnt += newDataPrices.split(",").length
  }
  if (data.tail && data.tail.length > 0) {
    arrParams.push(`tail=${data.tail}`)
  }
  if (data.mid && data.mid.length > 0) {
    arrParams.push(`mid=${data.mid}`)
    filterCnt += 1
  }
  if (data.q && data.q.length > 0) {
    arrParams.push(`q=${data.q}`)
  }
  if (data.limit) {
    arrParams.push(`limit=${data.limit}`)
  }
  if (data.p && parseInt(data.p)>1) {
    arrParams.push(`page=${data.p}`)
  }
  if (data.includesSim && data.includesSim.length > 0) {
    arrParams.push(`includesSim=${data.includesSim}`)
  }
  return [arrParams, filterCnt, friendlyURL, ignoreOldUrl]
}