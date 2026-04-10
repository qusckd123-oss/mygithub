#!/usr/bin/env python3
"""
musinsa-trend-crawler.py
무신사 검색어 랭킹 + 브랜드 랭킹 수집 (코어타겟 분석용)

Usage:
  python3 crawler.py [--format json|xlsx|both] [--no-images]

출력: workspace/musinsa-trend/trend_YYYYMMDD/
"""
import requests, json, os, sys, time
from datetime import datetime

BASE_URL = "https://api.musinsa.com/api2/hm/web/v5/pans/ranking"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
    "Referer": "https://www.musinsa.com/",
    "Origin": "https://www.musinsa.com",
}

BRAND_STYLE_TABS = {
    "1054": "전체",
    "1056": "영캐주얼",
    "1066": "스트릿캐주얼",
    "1058": "스포티/액티브",
    "1063": "여성캐주얼",
}

def fetch_keyword_ranking(gender="A"):
    """검색어 랭킹 Top 200 수집"""
    url = f"{BASE_URL}/sections/1067"
    params = {"storeCode": "musinsa", "gf": gender}
    try:
        resp = requests.get(url, headers=HEADERS, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        keywords = []
        for mod in data.get("data", {}).get("modules", []):
            if mod.get("type") != "RANKING_SEARCH":
                continue
            # Keyword data is at module level, not in items[]
            title = mod.get("title", {})
            fluct = mod.get("fluctuation", {})
            rank_str = mod.get("rank", "0")
            kw_text = title.get("text", "")
            if not kw_text:
                continue
            keywords.append({
                "rank": int(rank_str) if str(rank_str).isdigit() else 0,
                "keyword": kw_text,
                "change_type": fluct.get("type", "NONE"),
                "change_amount": fluct.get("amount", 0),
                "url": mod.get("onClick", {}).get("url", ""),
            })
        return keywords
    except Exception as e:
        print(f"  [ERROR] keyword ranking (gf={gender}): {e}")
        return []

def fetch_brand_ranking(section_id="1054", gender="A", age_band="AGE_BAND_ALL"):
    """브랜드 랭킹 Top 200 수집"""
    url = f"{BASE_URL}/sections/{section_id}"
    params = {"storeCode": "musinsa", "gf": gender, "ageBand": age_band}
    try:
        resp = requests.get(url, headers=HEADERS, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        brands = []
        for mod in data.get("data", {}).get("modules", []):
            if mod.get("type") != "RANKING_BRAND":
                continue
            # Brand data is at module.title level, not in items[]
            title_obj = mod.get("title", {})
            fluct = title_obj.get("fluctuation", {})
            rank_str = title_obj.get("rank", "0")
            brand_name = title_obj.get("title", {}).get("text", "")
            if not brand_name:
                continue
            brands.append({
                "rank": int(rank_str) if str(rank_str).isdigit() else 0,
                "brand": brand_name,
                "change_type": fluct.get("type", "NONE"),
                "change_amount": fluct.get("amount", 0),
                "logo": title_obj.get("imageUrl", ""),
                "labels": [lb.get("text", "") for lb in title_obj.get("labels", [])],
            })
        return brands
    except Exception as e:
        print(f"  [ERROR] brand ranking (section={section_id}, gf={gender}, age={age_band}): {e}")
        return []

def main():
    fmt = "json"
    for i, arg in enumerate(sys.argv):
        if arg == "--format" and i + 1 < len(sys.argv):
            fmt = sys.argv[i + 1]

    today = datetime.now().strftime("%Y%m%d")
    ts = datetime.now().strftime("%Y%m%d_%H%M")
    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                           "..", "workspace", "musinsa-trend", f"trend_{today}")
    os.makedirs(out_dir, exist_ok=True)

    result = {
        "meta": {
            "crawled_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "date": today,
        },
        "keywords": {},
        "brands": {},
    }

    # 1. 검색어 랭킹 (전체, 남성, 여성)
    for gender, label in [("A", "전체"), ("M", "남성"), ("F", "여성")]:
        print(f"  검색어 랭킹 수집: {label}...")
        kw = fetch_keyword_ranking(gender)
        result["keywords"][gender] = {
            "gender": gender,
            "gender_name": label,
            "count": len(kw),
            "items": kw,
        }
        time.sleep(0.5)

    # 2. 브랜드 랭킹 — 전체(전연령) + 전체(20대) + 전체(25세) + 스트릿(20대) + 여성캐주얼(20대)
    brand_configs = [
        ("1054", "A", "AGE_BAND_ALL", "전체_전연령"),
        ("1054", "A", "AGE_BAND_20", "전체_20대"),
        ("1054", "A", "AGE_BAND_25", "전체_25세"),
        ("1066", "A", "AGE_BAND_20", "스트릿_20대"),
        ("1063", "F", "AGE_BAND_20", "여성캐주얼_20대"),
        ("1056", "A", "AGE_BAND_20", "영캐주얼_20대"),
    ]
    for sec_id, gender, age, label in brand_configs:
        style_name = BRAND_STYLE_TABS.get(sec_id, sec_id)
        print(f"  브랜드 랭킹 수집: {label} ({style_name})...")
        br = fetch_brand_ranking(sec_id, gender, age)
        result["brands"][label] = {
            "section_id": sec_id,
            "style": style_name,
            "gender": gender,
            "age_band": age,
            "count": len(br),
            "items": br,
        }
        time.sleep(0.5)

    # Save
    out_file = os.path.join(out_dir, f"musinsa_trend_{ts}.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"\n  저장 완료: {out_file}")
    print(f"  검색어: {sum(d['count'] for d in result['keywords'].values())}개")
    print(f"  브랜드: {sum(d['count'] for d in result['brands'].values())}개")

    # Result meta
    meta_file = os.path.join(out_dir, "_result.json")
    with open(meta_file, "w", encoding="utf-8") as f:
        json.dump({"status": "success", "output_dir": out_dir, "files": [out_file],
                    "meta": result["meta"]}, f, ensure_ascii=False)

if __name__ == "__main__":
    main()
