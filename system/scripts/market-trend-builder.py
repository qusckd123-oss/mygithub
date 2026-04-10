#!/usr/bin/env python3
"""
market-trend-builder.py
무신사 랭킹/발매 JSON → 대시보드 인라인 데이터 생성

Usage:
  python3 system/scripts/market-trend-builder.py [--date YYYYMMDD]

기본적으로 가장 최근 크롤링 데이터를 사용합니다.
출력: workspace/26SS/dashboard/data_market-trend.json
"""
import json, glob, os, sys, re
from datetime import datetime

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RANK_DIR = os.path.join(BASE, "workspace/musinsa-ranking")
RELEASE_DIR = os.path.join(BASE, "workspace/musinsa-release")
TREND_DIR = os.path.join(BASE, "workspace/musinsa-trend")
OUT_PATH = os.path.join(BASE, "workspace/26SS/dashboard/data_market-trend.json")

CAT_MAP = {"001":"상의","002":"아우터","003":"바지","004":"가방","103":"신발",
           "100":"원피스/스커트","101":"소품","104":"뷰티","026":"속옷","017":"스포츠"}

def latest_dir(base, prefix):
    dirs = sorted(glob.glob(os.path.join(base, f"{prefix}_*")))
    if not dirs:
        return None
    return dirs[-1]

def load_json_files(directory, pattern):
    files = sorted(glob.glob(os.path.join(directory, pattern)))
    results = []
    for f in files:
        with open(f, "r", encoding="utf-8") as fh:
            results.append(json.load(fh))
    return results

def parse_ranking(data, top_n=30):
    """Parse ranking JSON → {category_code: [{rank,brand,name,price,discount,img,url,labels}]}"""
    cats = {}
    gender = data.get("meta",{}).get("gender","?")
    gender_name = data.get("meta",{}).get("gender_name","?")
    period = data.get("meta",{}).get("period_name","?")

    for p in data.get("products",[]):
        cc = p.get("category_code","?")
        cn = p.get("category_name", CAT_MAP.get(cc, cc))
        if cc not in cats:
            cats[cc] = {"code":cc, "name":cn, "items":[]}
        if len(cats[cc]["items"]) >= top_n:
            continue
        cats[cc]["items"].append({
            "r": p["rank"],
            "b": p["brand_name"],
            "n": p["product_name"],
            "op": p.get("original_price",0),
            "fp": p.get("final_price",0),
            "d": p.get("discount_ratio",0),
            "img": p.get("image_url",""),
            "url": p.get("product_url",""),
            "lb": p.get("labels",""),
            "ai": p.get("additional_info",""),
        })

    return {
        "gender": gender,
        "gender_name": gender_name,
        "period": period,
        "categories": cats,
    }

def parse_release(data):
    """Parse release JSON → [{brand,name,date,dday,status,price,img,url,soldout}]"""
    items = []
    for it in data.get("items",[]):
        items.append({
            "b": it.get("brand_name",""),
            "n": it.get("product_name",""),
            "rd": it.get("release_date",""),
            "rt": it.get("release_datetime",""),
            "dd": it.get("dday",""),
            "st": it.get("release_status",""),
            "fp": it.get("final_price",0),
            "op": it.get("original_price",0),
            "so": it.get("is_sold_out", False),
            "img": it.get("image_url",""),
            "url": it.get("product_url",""),
            "sub": it.get("sub_title",{}).get("text","") if isinstance(it.get("sub_title"), dict) else str(it.get("sub_title","")),
            "type": it.get("item_type","product"),
        })
    return {
        "tab": data.get("meta",{}).get("tab",""),
        "tab_name": data.get("meta",{}).get("tab_name",""),
        "gender": data.get("meta",{}).get("gender","A"),
        "count": data.get("count",len(items)),
        "crawled_at": data.get("meta",{}).get("crawled_at",""),
        "items": items,
    }

def brand_stats(ranking_data):
    """Compute brand frequency across all categories for a ranking dataset."""
    brand_count = {}
    brand_cats = {}
    for cc, cat in ranking_data["categories"].items():
        for it in cat["items"]:
            b = it["b"]
            brand_count[b] = brand_count.get(b, 0) + 1
            if b not in brand_cats:
                brand_cats[b] = set()
            brand_cats[b].add(cat["name"])
    # Sort by count desc
    top = sorted(brand_count.items(), key=lambda x: -x[1])[:20]
    return [{"b":b, "cnt":c, "cats":sorted(list(brand_cats.get(b,set())))} for b,c in top]

def price_stats(ranking_data):
    """Compute avg price per category."""
    result = {}
    for cc, cat in ranking_data["categories"].items():
        prices = [it["fp"] for it in cat["items"] if it["fp"] > 0]
        if prices:
            result[cat["name"]] = {
                "avg": round(sum(prices)/len(prices)),
                "min": min(prices),
                "max": max(prices),
                "cnt": len(prices),
            }
    return result

def main():
    date_filter = None
    if len(sys.argv) > 1 and sys.argv[1] == "--date" and len(sys.argv) > 2:
        date_filter = sys.argv[2]

    # Find latest ranking directory
    rank_dir = None
    if date_filter:
        candidate = os.path.join(RANK_DIR, f"ranking_{date_filter}")
        if os.path.isdir(candidate):
            rank_dir = candidate
    if not rank_dir:
        rank_dir = latest_dir(RANK_DIR, "ranking")

    # Find latest release directory
    rel_dir = None
    if date_filter:
        candidate = os.path.join(RELEASE_DIR, f"release_{date_filter}")
        if os.path.isdir(candidate):
            rel_dir = candidate
    if not rel_dir:
        rel_dir = latest_dir(RELEASE_DIR, "release")

    # Find latest trend directory
    trend_dir = None
    if date_filter:
        candidate = os.path.join(TREND_DIR, f"trend_{date_filter}")
        if os.path.isdir(candidate):
            trend_dir = candidate
    if not trend_dir:
        trend_dir = latest_dir(TREND_DIR, "trend")

    output = {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "ranking": {"uni":None, "womens":None},
        "release": [],
        "brand_stats": {"uni":[], "womens":[]},
        "price_stats": {"uni":{}, "womens":{}},
        "trends": {"keywords":{}, "brands":{}},
    }

    # Parse rankings
    if rank_dir:
        rank_files = sorted(glob.glob(os.path.join(rank_dir, "*.json")))
        rank_files = [f for f in rank_files if not f.endswith("_result.json")]
        for rf in rank_files:
            with open(rf, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            parsed = parse_ranking(data, top_n=30)
            gender = data.get("meta",{}).get("gender","?")
            if gender == "M":
                output["ranking"]["uni"] = parsed
                output["brand_stats"]["uni"] = brand_stats(parsed)
                output["price_stats"]["uni"] = price_stats(parsed)
            elif gender == "F":
                output["ranking"]["womens"] = parsed
                output["brand_stats"]["womens"] = brand_stats(parsed)
                output["price_stats"]["womens"] = price_stats(parsed)
        print(f"[ranking] {rank_dir} → {len(rank_files)} files parsed")

    # Parse releases
    if rel_dir:
        rel_files = sorted(glob.glob(os.path.join(rel_dir, "*.json")))
        rel_files = [f for f in rel_files if not f.endswith("_result.json")]
        for rf in rel_files:
            with open(rf, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            parsed = parse_release(data)
            output["release"].append(parsed)
        print(f"[release] {rel_dir} → {len(rel_files)} files parsed")

    # Parse trends (keywords + brand rankings)
    if trend_dir:
        trend_files = sorted(glob.glob(os.path.join(trend_dir, "musinsa_trend_*.json")))
        if trend_files:
            with open(trend_files[-1], "r", encoding="utf-8") as fh:
                tdata = json.load(fh)
            # Keywords: keep top 50 per gender, compact format
            for gk, gv in tdata.get("keywords", {}).items():
                items = gv.get("items", [])[:50]
                output["trends"]["keywords"][gk] = {
                    "gender_name": gv.get("gender_name",""),
                    "items": [{"r":it["rank"],"k":it["keyword"],
                               "ct":it.get("change_type","NONE"),
                               "ca":it.get("change_amount",0)} for it in items],
                }
            # Brands: keep top 30 per config, compact format
            for bk, bv in tdata.get("brands", {}).items():
                items = bv.get("items", [])[:30]
                output["trends"]["brands"][bk] = {
                    "style": bv.get("style",""),
                    "age_band": bv.get("age_band",""),
                    "gender": bv.get("gender",""),
                    "items": [{"r":it["rank"],"b":it["brand"],
                               "ct":it.get("change_type","NONE"),
                               "ca":it.get("change_amount",0),
                               "lb":it.get("labels",[])} for it in items],
                }
            print(f"[trends] {trend_files[-1]} → keywords {sum(len(v['items']) for v in output['trends']['keywords'].values())}, brands {sum(len(v['items']) for v in output['trends']['brands'].values())}")

    # Write output
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as fh:
        json.dump(output, fh, ensure_ascii=False, separators=(",",":"))
    size_kb = os.path.getsize(OUT_PATH) / 1024
    print(f"[output] {OUT_PATH} ({size_kb:.1f} KB)")

if __name__ == "__main__":
    main()
