#!/usr/bin/env python3
import re, json, html
from urllib.request import Request, urlopen
from urllib.parse import urlencode
from datetime import date, datetime
from pathlib import Path

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
BASE = Path(__file__).resolve().parent


def get(url: str) -> str:
    req = Request(url, headers={"User-Agent": UA, "Accept-Language": "ko-KR,ko;q=0.9,en;q=0.8"})
    with urlopen(req, timeout=20) as r:
        return r.read().decode("utf-8", errors="ignore")


def post_text(url: str, data: dict, extra_headers=None) -> str:
    body = urlencode(data).encode("utf-8")
    headers = {
        "User-Agent": UA,
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://www.egbiz.or.kr",
        "Referer": "https://www.egbiz.or.kr/index.do",
    }
    if extra_headers:
        headers.update(extra_headers)
    req = Request(url, data=body, headers=headers)
    with urlopen(req, timeout=20) as r:
        return r.read().decode("utf-8", errors="ignore")


def clean(s: str) -> str:
    s = re.sub(r"<[^>]+>", "", s)
    s = html.unescape(s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def days_until(deadline: str):
    if not deadline:
        return None
    try:
        dl = datetime.strptime(deadline, "%Y-%m-%d").date()
        return (dl - date.today()).days
    except Exception:
        return None


def normalize_date(s: str) -> str:
    s = (s or "").strip()
    if not s:
        return ""
    s = s.replace(".", "-").replace("/", "-")
    m = re.search(r"(\d{4})-(\d{2})-(\d{2})", s)
    if m:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
    m2 = re.search(r"(\d{2})-(\d{2})-(\d{2})", s)
    if m2:
        return f"20{m2.group(1)}-{m2.group(2)}-{m2.group(3)}"
    return ""


def extract_deadline_from_text(s: str) -> str:
    s = (s or "").strip()
    s = s.replace(".", "-").replace("/", "-")
    # 우선 YYYY-MM-DD가 있으면 마지막 날짜를 마감일로 사용
    all_full = re.findall(r"(\d{4}-\d{2}-\d{2})", s)
    if all_full:
        return all_full[-1]
    # YY-MM-DD 형태만 있으면 20YY로 보정
    all_short = re.findall(r"(\d{2}-\d{2}-\d{2})", s)
    if all_short:
        return "20" + all_short[-1]
    return ""


def parse_kstartup() -> list:
    url = "https://www.k-startup.go.kr/web/contents/bizpbanc-ongoing.do"
    txt = get(url)
    pat = re.compile(
        r"go_view\((\d+)\).*?"
        r"<span class=\"flag type\d+\">\s*([^<]+?)\s*</span>.*?"
        r"<span class=\"flag day\">\s*D-(\d+)\s*</span>.*?"
        r"마감일자\s*([0-9\-]{10}).*?"
        r"<p class=\"tit\">\s*(.*?)\s*</p>",
        re.S,
    )
    out = []
    seen = set()
    for m in pat.finditer(txt):
        pbanc_sn, category, dday, deadline, title = m.groups()
        title = clean(title)
        if not title or pbanc_sn in seen:
            continue
        seen.add(pbanc_sn)
        out.append(
            {
                "id": f"k-{pbanc_sn}",
                "source": "kstartup",
                "title": title,
                "category": clean(category),
                "deadline": deadline,
                "dday": int(dday),
                "url": f"https://www.k-startup.go.kr/web/contents/bizpbanc-ongoing.do?schM=view&pbancSn={pbanc_sn}",
            }
        )
    return out[:80]


def parse_bizinfo() -> list:
    url = "https://www.bizinfo.go.kr/web/lay1/bbs/S1T122C128/AS/74/list.do"
    txt = get(url)
    rows = re.findall(r"<tr>.*?</tr>", txt, flags=re.S)
    out = []
    for row in rows:
        if "pblancId=PBLN_" not in row:
            continue
        tds = re.findall(r"<td[^>]*>(.*?)</td>", row, flags=re.S)
        if len(tds) < 7:
            continue
        category = clean(tds[1])
        link_match = re.search(r"<a\s+href=\s*\"([^\"]*pblancId=PBLN_[0-9]+)[^\"]*\"[^>]*>(.*?)</a>", tds[2], flags=re.S)
        if not link_match:
            continue
        href, title = link_match.groups()
        title = clean(title)
        period = clean(tds[3])
        reg_date = clean(tds[6])

        dl_match = re.search(r"~\s*([0-9]{4}-[0-9]{2}-[0-9]{2})", period)
        deadline = dl_match.group(1) if dl_match else ""
        dday = days_until(deadline)

        full_url = href if href.startswith("http") else f"https://www.bizinfo.go.kr{href}"
        pid_match = re.search(r"(PBLN_[0-9]+)", full_url)
        pid = pid_match.group(1) if pid_match else str(abs(hash(full_url)))

        out.append(
            {
                "id": f"b-{pid}",
                "source": "bizinfo",
                "title": title,
                "category": category,
                "deadline": deadline,
                "dday": dday,
                "period": period,
                "regDate": reg_date,
                "url": full_url,
            }
        )
    return out[:140]


def parse_iris() -> list:
    url = "https://www.iris.go.kr/contents/retrieveBsnsAncmBtinSituListView.do"
    txt = get(url)

    # ancmId, title, category(institution), date
    pat = re.compile(
        r"f_bsnsAncmBtinSituListForm_view\('(\d+)'\s*,\s*'([^']+)'\).*?"
        r"<span class=\"inst_title\">(.*?)</span>.*?"
        r"<strong class=\"title\"><a [^>]*>(.*?)</a></strong>.*?"
        r"<span class=\"ancmDe\"><em>공고일자\s*:</em>\s*([0-9\-]{10})</span>",
        re.S,
    )

    out = []
    seen = set()
    for m in pat.finditer(txt):
        ancm_id, ancm_prg, inst_title, title, reg_date = m.groups()
        if ancm_id in seen:
            continue
        seen.add(ancm_id)
        title = clean(title)
        inst_title = clean(inst_title)

        out.append(
            {
                "id": f"i-{ancm_id}",
                "source": "iris",
                "title": title,
                "category": inst_title,
                "deadline": "",  # 페이지에 마감일이 리스트에서 바로 안 보임
                "dday": None,
                "regDate": reg_date,
                "url": f"https://www.iris.go.kr/contents/retrieveBsnsAncmView.do?ancmId={ancm_id}&ancmPrg={ancm_prg}",
            }
        )
    return out[:120]


def parse_egbiz() -> list:
    url = "https://www.egbiz.or.kr/sp/selectSupportPrjListAjax.do"

    # month/day별로 분산돼 있어 12개월 조회 후 합치기
    merged = {}
    for m in range(1, 13):
        raw = post_text(url, {"month": str(m), "day": "1", "sortCd": "bizCyclId"})
        obj = json.loads(raw)
        for item in obj.get("value", []) or []:
            biz_id = item.get("bizCyclId")
            if not biz_id:
                continue
            if biz_id in merged:
                continue
            title = (item.get("bizNm") or "").strip()
            if not title:
                continue
            deadline = (item.get("aplyEndDt") or "").strip()
            start = (item.get("aplyBgngDt") or "").strip()
            category = (item.get("categoryNm") or "기타").strip()
            org = (item.get("outsdInstNm") or item.get("insttNm") or "").strip()
            reg_date = (item.get("mdfcnDt") or "").strip()

            merged[biz_id] = {
                "id": f"e-{biz_id}",
                "source": "egbiz",
                "title": title,
                "category": category,
                "deadline": deadline,
                "dday": days_until(deadline),
                "period": f"{start} ~ {deadline}" if start and deadline else "",
                "regDate": reg_date,
                "org": org,
                # 로그인 없이 열리는 상세 링크(팝업 호출 페이지)
                "url": f"https://www.egbiz.or.kr/mainHotDetail.do?bizCyclId={biz_id}",
            }

    out = list(merged.values())
    out.sort(key=lambda x: (9999 if x.get("dday") is None else x["dday"], x.get("deadline") or "9999-12-31"))
    return out[:180]


def parse_smtech() -> list:
    url = "https://www.smtech.go.kr/front/ifg/no/notice02_intro.do"
    txt = get(url)

    # 월별 일정표 셀의 링크 + 아이콘 title에 공고명/접수기간이 함께 들어있음
    pat = re.compile(
        r"<a\s+href=\"([^\"]*notice02_list\.do[^\"]*ancmId=([^&\"]+)[^\"]*)\"[^>]*>\s*"
        r"(?:.*?)<img[^>]*title=\"([^\"]+)\"",
        re.S,
    )

    out = []
    seen = set()
    for m in pat.finditer(txt):
        href, ancm_id, title_blob = m.groups()
        if ancm_id in seen:
            continue
        seen.add(ancm_id)

        title_blob = clean(title_blob)
        deadline = extract_deadline_from_text(title_blob)

        # 제목에서 날짜표현 제거
        title = re.sub(r"\s*\d{4}[\.\-]\d{2}[\.\-]\d{2}\s*[~~-]\s*\d{4}[\.\-]\d{2}[\.\-]\d{2}\s*$", "", title_blob).strip()
        if not title:
            title = title_blob

        full_url = href if href.startswith("http") else f"https://www.smtech.go.kr{href}"
        full_url = full_url.replace("&amp;", "&")
        full_url = re.sub(r";jsessionid=[^?]+", "", full_url, flags=re.I)

        out.append(
            {
                "id": f"smt-{ancm_id}",
                "source": "smtech",
                "title": title,
                "category": "R&D 사업공고",
                "deadline": deadline,
                "dday": days_until(deadline),
                "url": full_url,
            }
        )

    return out[:120]


def parse_smes24() -> list:
    url = "https://www.smes.go.kr/main/bizApply"
    txt = get(url)

    # 팝업 인덱스 -> 상세 링크 맵 추출
    idx_to_url = {}
    for idx, link in re.findall(r"if\(index\s*==\s*\"(\d+)\"\)\{.*?fn_popupDtl\('[^']*',\s*'([^']+)'", txt, flags=re.S):
        idx_to_url[idx] = link.replace("|amp;", "&")

    tbody_m = re.search(r"<tbody>(.*?)</tbody>", txt, flags=re.S)
    if not tbody_m:
        return []

    rows = re.findall(r"<tr>.*?</tr>", tbody_m.group(1), flags=re.S)
    out = []
    seen = set()

    for row in rows:
        args_m = re.search(
            r"fn_include_popOpen2\('([^']*)','([^']*)',\s*'([^']*)',\s*'([^']*)','([^']*)',\s*'([^']*)'\)",
            row,
        )
        if not args_m:
            continue

        pblanc_seq, idx, cntc_cd, pblanc_id, org_from_args, status = args_m.groups()
        if pblanc_id in seen:
            continue
        seen.add(pblanc_id)

        tds = re.findall(r"<td[^>]*>(.*?)</td>", row, flags=re.S)
        if len(tds) < 6:
            continue

        title_a = re.search(r"<a [^>]*title=\"([^\"]+)\"", row, flags=re.S)
        title = clean(title_a.group(1)) if title_a else clean(tds[1])

        period = clean(tds[2])
        category = clean(tds[4])
        org = clean(tds[5]) or org_from_args
        deadline = extract_deadline_from_text(period)

        detail_url = idx_to_url.get(idx)
        if not detail_url:
            detail_url = f"https://www.bizinfo.go.kr/web/lay1/bbs/S1T122C128/AS/74/view.do?pblancId={pblanc_id}"

        out.append(
            {
                "id": f"s24-{pblanc_id}",
                "source": "smes24",
                "title": title,
                "category": category or "지원사업",
                "deadline": deadline,
                "dday": days_until(deadline),
                "period": period,
                "status": status,
                "org": org,
                "cntcInsttCd": cntc_cd,
                "pblancSeq": pblanc_seq,
                "url": detail_url,
            }
        )

    return out[:200]


def parse_gosims() -> list:
    # 보조금통합포털(bojo.go.kr) 공모사업 목록 API
    api = "https://www.bojo.go.kr/da/retrieveTaskReqstList.do"
    out = []
    seen = set()

    # 현재연도 중심으로 조회(공모 진행 상태: 접수중)
    year = str(date.today().year)
    per_page = 200

    for page in range(1, 6):
        data = {
            "searchBsnsYear": year,
            "selSido": "",        # 전국
            "selSigungu": "",
            "selectedMultiType": "",
            "curPage": str(page),
            "perPage": str(per_page),
            "searchPssrpSttus": "1",  # 접수중
        }
        raw = post_text(
            api,
            data,
            {
                "Origin": "https://www.bojo.go.kr",
                "Referer": "https://www.bojo.go.kr/bojo.do",
            },
        )
        obj = json.loads(raw)
        rows = obj.get("ntbdList", []) or []
        if not rows:
            break

        for item in rows:
            ntt_id = (item.get("nttId") or "").strip()
            if not ntt_id or ntt_id in seen:
                continue
            seen.add(ntt_id)

            title = clean(item.get("sjCn") or item.get("pblancNm") or "")
            if not title:
                continue

            start = normalize_date(item.get("rceptBeginDe") or "")
            end = normalize_date(item.get("rceptEndDe") or "")
            deadline = end

            org = clean(item.get("pssrpInsttNm") or item.get("wdrInsttNm") or item.get("wrterCn") or "")
            pblanc_type = (item.get("pblancSeCode") or "").strip()
            pblanc_type_nm = "e나라도움" if pblanc_type == "A" else ("보탬e" if pblanc_type == "B" else "공모사업")
            bsns_se = (item.get("bsnsSe") or "").strip()
            biz_type = "국고" if bsns_se == "1" else ("지방" if bsns_se == "2" else "기타")

            out.append(
                {
                    "id": f"g-{ntt_id}",
                    "source": "gosims",
                    "title": title,
                    "category": f"{pblanc_type_nm} {biz_type}".strip(),
                    "deadline": deadline,
                    "dday": days_until(deadline),
                    "period": f"{start} ~ {end}" if start and end else "",
                    "org": org,
                    "url": f"https://www.bojo.go.kr/ia/getIA005100Popup.do?nttId={ntt_id}",
                }
            )

        # 마지막 페이지 판단
        if len(rows) < per_page:
            break

    return out[:240]


SOURCE_PRIORITY = {
    "gosims": 100,
    "smtech": 95,
    "kstartup": 90,
    "bizinfo": 85,
    "egbiz": 80,
    "smes24": 75,
    "iris": 70,
}


def normalize_title(s: str) -> str:
    s = clean(s or "").lower()
    s = re.sub(r"\([^)]*\)", " ", s)
    s = re.sub(r"\[[^\]]*\]", " ", s)
    s = re.sub(r"[0-9]{4}[\.\-/][0-9]{1,2}[\.\-/][0-9]{1,2}", " ", s)
    s = re.sub(r"[^0-9a-z가-힣]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def notice_quality_score(n: dict) -> tuple:
    # 품질 우선순위: 마감일 보유 > 기간/기관 보유 > 소스 우선순위
    has_deadline = 1 if n.get("deadline") else 0
    has_period = 1 if n.get("period") else 0
    has_org = 1 if n.get("org") else 0
    src = n.get("source") or ""
    src_score = SOURCE_PRIORITY.get(src, 0)
    title_len = len(n.get("title") or "")
    return (has_deadline, has_period, has_org, src_score, title_len)


def dedupe_notices(notices: list) -> tuple[list, int]:
    by_key = {}
    removed = 0

    for n in notices:
        tnorm = normalize_title(n.get("title") or "")
        if not tnorm:
            continue
        deadline = n.get("deadline") or ""
        period = n.get("period") or ""
        org = normalize_title(n.get("org") or "")

        # 1차: 제목 + (기간 또는 마감)
        key1 = f"{tnorm}|{period or deadline}"
        # 2차(백업): 제목 + 기관 + 마감
        key2 = f"{tnorm}|{org}|{deadline}"

        chosen_key = key1 if (period or deadline) else key2

        old = by_key.get(chosen_key)
        if old is None:
            by_key[chosen_key] = n
            continue

        if notice_quality_score(n) > notice_quality_score(old):
            by_key[chosen_key] = n
            removed += 1
        else:
            removed += 1

    return list(by_key.values()), removed


def sort_key(n: dict):
    # 마감 지난 공고는 아래로, 마감일 없는 공고는 가장 아래로
    dday = n.get("dday")
    if dday is None:
        grp = 2
        dval = 9999
    elif dday < 0:
        grp = 1
        dval = dday
    else:
        grp = 0
        dval = dday
    return (grp, dval, n.get("deadline") or "9999-12-31", -(SOURCE_PRIORITY.get(n.get("source") or "", 0)))


def main():
    all_notices = []
    errs = []

    for name, fn in [
        ("kstartup", parse_kstartup),
        ("bizinfo", parse_bizinfo),
        ("iris", parse_iris),
        ("egbiz", parse_egbiz),
        ("smtech", parse_smtech),
        ("smes24", parse_smes24),
        ("gosims", parse_gosims),
    ]:
        try:
            data = fn()
            all_notices.extend(data)
        except Exception as e:
            errs.append(f"{name}: {e}")

    before_count = len(all_notices)
    all_notices, dedup_removed = dedupe_notices(all_notices)
    all_notices.sort(key=sort_key)

    source_stats = {}
    for n in all_notices:
        src = n.get("source") or "unknown"
        source_stats[src] = source_stats.get(src, 0) + 1

    no_deadline_count = sum(1 for n in all_notices if not n.get("deadline"))

    payload = {
        "updatedAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "count": len(all_notices),
        "beforeDedupeCount": before_count,
        "dedupRemoved": dedup_removed,
        "noDeadlineCount": no_deadline_count,
        "sourceStats": source_stats,
        "errors": errs,
        "notices": all_notices,
    }

    (BASE / "notices.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    (BASE / "notices.js").write_text(
        "window.GOV_DATA = " + json.dumps(payload, ensure_ascii=False) + ";\n",
        encoding="utf-8",
    )
    print(f"saved {len(all_notices)} notices (dedupe -{dedup_removed})")
    if errs:
        print("errors:", " | ".join(errs))


if __name__ == "__main__":
    main()
