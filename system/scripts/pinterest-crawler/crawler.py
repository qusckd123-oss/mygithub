"""
Pinterest Image Crawler for Wacky Willy Moodboard
==================================================
와키윌리 브랜드 무드(Kitsch Street & IP Universe)에 맞는
핀터레스트 이미지를 Selenium으로 수집하는 파이프라인.

사용법:
  python crawler.py                          # 전체 카테고리 크롤링
  python crawler.py --category brand_mood    # 특정 카테고리만
  python crawler.py --keyword "kitsch fashion" --count 30  # 단일 키워드
  python crawler.py --filter-only            # 이미 다운된 이미지 AI 필터만 실행
"""

from __future__ import annotations

import os
import sys
import json
import time
import hashlib
import pickle
import argparse
import requests
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# 쿠키 저장 경로
COOKIE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_pinterest_cookies.pkl")


# ──────────────────────────────────────────────
# 1. 와키윌리 브랜드 기반 검색 키워드
# ──────────────────────────────────────────────

WACKY_WILLY_KEYWORDS = {
    # 브랜드 무드 — Kitsch Street & IP Universe
    "brand_mood": [
        "kitsch street fashion lookbook",
        "kitsch streetwear colorful outfit",
        "pop art fashion editorial",
        "Y2K kitsch outfit street snap",
        "harajuku street style colorful 2025",
        "bold graphic tee street look",
    ],

    # 캐릭터·IP 감성
    "character_ip": [
        "character graphic streetwear",
        "cartoon print oversized tee outfit",
        "kawaii street fashion snap",
        "mascot fashion brand lookbook",
        "doodle graffiti fashion",
        "IP collaboration streetwear",
    ],

    # 컬러 트렌드 (시그니처 옐로우 + 비비드)
    "color_vivid": [
        "vivid color blocking streetwear",
        "neon yellow street fashion",
        "bright color outfit gen z",
        "dopamine dressing street style",
        "pastel kitsch aesthetic outfit",
        "bold color mix street snap",
    ],

    # 타겟 스타일링 (18~25세 트렌드리더)
    "target_styling": [
        "gen z korean street style 2025",
        "K-fashion street snap seoul",
        "korean unisex streetwear lookbook",
        "oversized hoodie street look",
        "sporty casual kitsch outfit",
        "korean women street style trendy",
    ],

    # 캠페인·룩북 레퍼런스
    "campaign_ref": [
        "street fashion campaign colorful editorial",
        "lookbook photography street urban",
        "fashion brand campaign pop art",
        "street snap editorial vivid color",
    ],

    # 용품·악세서리
    "accessories": [
        "character backpack street fashion",
        "colorful streetwear accessories",
        "graphic cap bucket hat street",
        "kawaii bag street outfit",
    ],

    # 비주얼 머천다이징
    "visual_merch": [
        "colorful retail store display fashion",
        "street fashion pop up store",
        "kitsch fashion store interior",
        "fashion flagship store vivid display",
    ],
}


# ──────────────────────────────────────────────
# 2. 크롤러 클래스
# ──────────────────────────────────────────────

class PinterestCrawler:
    """Selenium 기반 핀터레스트 이미지 크롤러"""

    # 크롬 프로필 경로 (macOS 기본)
    CHROME_PROFILE_DIR = os.path.expanduser(
        "~/Library/Application Support/Google/Chrome"
    )

    def __init__(self, download_dir: str, headless: bool = False,
                 use_profile: bool = False):
        self.download_dir = download_dir
        os.makedirs(download_dir, exist_ok=True)

        options = Options()
        if headless:
            options.add_argument("--headless=new")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-notifications")

        # 기존 크롬 프로필 사용 (이미 로그인된 세션 재활용)
        if use_profile:
            options.add_argument(f"--user-data-dir={self.CHROME_PROFILE_DIR}")
            options.add_argument("--profile-directory=Default")
            print("[프로필] 기존 크롬 프로필 사용 — 이미 로그인된 세션 재활용")
            print("  ※ 크롬 브라우저가 열려있으면 먼저 닫아주세요!")
        else:
            options.add_argument(
                "--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
            )

        # 자동 크롬 드라이버 관리
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options,
        )
        self.driver.implicitly_wait(5)
        self._logged_in = use_profile  # 프로필 모드면 이미 로그인 상태

    # ── 쿠키 기반 로그인 ──
    def login_with_cookies(self):
        """저장된 쿠키로 로그인 시도. 없으면 브라우저에서 수동 로그인 대기."""
        print("[1/5] 핀터레스트 로그인...")
        self.driver.get("https://www.pinterest.com/")
        time.sleep(2)

        # 1) 저장된 쿠키가 있으면 로드 시도
        if os.path.exists(COOKIE_PATH):
            print("  -> 저장된 쿠키 발견, 로드 중...")
            with open(COOKIE_PATH, "rb") as f:
                cookies = pickle.load(f)
            for cookie in cookies:
                try:
                    self.driver.add_cookie(cookie)
                except Exception:
                    pass
            self.driver.refresh()
            time.sleep(3)

            if self._check_logged_in():
                self._logged_in = True
                print("  -> 쿠키 로그인 성공!")
                return
            else:
                print("  -> 쿠키 만료됨, 수동 로그인 필요")

        # 2) 수동 로그인 대기 (구글 로그인 등)
        print("\n  ╔══════════════════════════════════════════════╗")
        print("  ║  브라우저에서 핀터레스트에 로그인해주세요!   ║")
        print("  ║  (구글 로그인 OK)                            ║")
        print("  ║  로그인 완료 후 Enter를 눌러주세요...        ║")
        print("  ╚══════════════════════════════════════════════╝\n")

        self.driver.get("https://www.pinterest.com/login/")
        input("  >> 로그인 완료 후 Enter 키를 누르세요: ")

        time.sleep(2)
        if self._check_logged_in():
            self._logged_in = True
            self._save_cookies()
            print("  -> 로그인 성공! 쿠키 저장 완료 (다음부터 자동 로그인)")
        else:
            print("  -> 로그인 확인 실패, 비로그인 모드로 계속 진행합니다.")

    def _check_logged_in(self) -> bool:
        """핀터레스트 로그인 상태 확인"""
        try:
            self.driver.get("https://www.pinterest.com/")
            time.sleep(2)
            # 로그인 상태면 검색바 또는 홈피드가 보임
            logged_in_indicators = self.driver.find_elements(
                By.CSS_SELECTOR,
                "[data-test-id='header-search'], [data-test-id='homefeed-feed'],"
                "[aria-label='Search'], [data-test-id='search-input']"
            )
            return len(logged_in_indicators) > 0
        except Exception:
            return False

    def _save_cookies(self):
        """현재 세션 쿠키를 파일로 저장"""
        cookies = self.driver.get_cookies()
        with open(COOKIE_PATH, "wb") as f:
            pickle.dump(cookies, f)
        print(f"  -> 쿠키 저장: {COOKIE_PATH}")

    def login(self, email: str, password: str):
        """이메일/비밀번호 직접 로그인 (레거시)"""
        print("[1/5] 핀터레스트 이메일 로그인 중...")
        self.driver.get("https://www.pinterest.com/login/")
        time.sleep(3)
        try:
            email_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "email"))
            )
            email_input.clear()
            email_input.send_keys(email)
            pw_input = self.driver.find_element(By.ID, "password")
            pw_input.clear()
            pw_input.send_keys(password)
            pw_input.send_keys(Keys.RETURN)
            time.sleep(5)
            self._logged_in = True
            self._save_cookies()
            print("  -> 로그인 성공")
        except Exception as e:
            print(f"  -> 로그인 실패: {e}")
            print("  -> 비로그인 모드로 계속 진행합니다.")

    # ── 검색 + 스크롤 ──
    def search_and_collect(self, keyword: str, max_images: int = 50,
                           scroll_pause: float = 1.5) -> list[dict]:
        """키워드 검색 후 스크롤하며 이미지 URL + 메타데이터 수집"""
        encoded = keyword.replace(" ", "%20")
        self.driver.get(f"https://www.pinterest.com/search/pins/?q={encoded}")
        time.sleep(3)

        # 로그인 팝업 닫기 (비로그인 시)
        self._dismiss_popups()

        collected = {}  # url -> metadata
        no_new_count = 0

        for scroll_idx in range(40):  # 최대 40회 스크롤
            imgs = self.driver.find_elements(By.CSS_SELECTOR, "img[src*='pinimg.com']")

            for img in imgs:
                src = img.get_attribute("src")
                if not src or "pinimg.com" not in src:
                    continue

                high_res = self._to_high_res(src)
                if not high_res or high_res in collected:
                    continue

                # alt 텍스트에서 설명 추출
                alt = img.get_attribute("alt") or ""

                collected[high_res] = {
                    "url": high_res,
                    "alt": alt,
                    "keyword": keyword,
                    "collected_at": datetime.now().isoformat(),
                }

            prev_count = len(collected)
            if len(collected) >= max_images:
                break

            # 스크롤
            self.driver.execute_script("window.scrollBy(0, 1200);")
            time.sleep(scroll_pause)

            # 새 이미지가 없으면 3회까지 재시도 후 종료
            if len(collected) == prev_count:
                no_new_count += 1
                if no_new_count >= 3:
                    break
            else:
                no_new_count = 0

            if (scroll_idx + 1) % 5 == 0:
                print(f"    스크롤 {scroll_idx + 1} — 수집: {len(collected)}장")

        results = list(collected.values())[:max_images]
        return results

    # ── 이미지 다운로드 ──
    def download_images(self, items: list[dict], subfolder: str = "",
                        min_size_kb: int = 5, min_resolution: int = 100) -> int:
        """수집된 이미지 메타데이터 기반 다운로드

        Args:
            min_size_kb: 최소 파일 크기 (KB). 이보다 작으면 스킵.
            min_resolution: 최소 가로/세로 픽셀. 이보다 작으면 삭제.
        """
        save_dir = os.path.join(self.download_dir, subfolder) if subfolder else self.download_dir
        os.makedirs(save_dir, exist_ok=True)

        downloaded = 0
        skipped_small = 0
        for i, item in enumerate(items):
            url = item["url"]
            try:
                resp = requests.get(url, timeout=15, headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
                })
                if resp.status_code != 200:
                    continue

                # 파일 크기 필터 (너무 작은 썸네일/아이콘 제거)
                content_bytes = resp.content
                if len(content_bytes) < min_size_kb * 1024:
                    skipped_small += 1
                    continue

                # 파일명: URL 해시 (중복 방지)
                filename = hashlib.md5(url.encode()).hexdigest()[:12] + ".jpg"
                filepath = os.path.join(save_dir, filename)

                if os.path.exists(filepath):
                    continue

                with open(filepath, "wb") as f:
                    f.write(content_bytes)

                # 해상도 필터 (PIL 있으면 검사, 없으면 스킵)
                try:
                    from PIL import Image
                    with Image.open(filepath) as img:
                        w, h = img.size
                        if w < min_resolution or h < min_resolution:
                            os.remove(filepath)
                            skipped_small += 1
                            continue
                except ImportError:
                    pass

                # 메타데이터 저장
                item["local_path"] = filepath
                item["filename"] = filename
                downloaded += 1

            except Exception:
                continue

            if (i + 1) % 20 == 0:
                print(f"    다운로드: {i + 1}/{len(items)} ({downloaded}장 신규)")

        if skipped_small > 0:
            print(f"    소형 이미지 필터: {skipped_small}장 제외 (<{min_size_kb}KB 또는 <{min_resolution}px)")

        return downloaded

    # ── 유틸리티 ──
    def _to_high_res(self, url: str) -> str | None:
        """썸네일 → 고해상도 URL 변환 (모든 크기 패턴 → /736x/)"""
        import re
        if "pinimg.com" not in url:
            return None
        # /60x60/, /136x136/, /236x/, /474x/ 등 모든 크기 패턴을 /736x/로 변환
        converted = re.sub(r"/\d+x\d*/", "/736x/", url)
        return converted

    def _dismiss_popups(self):
        """핀터레스트 로그인/가입 팝업 닫기"""
        try:
            close_btns = self.driver.find_elements(
                By.CSS_SELECTOR, "[aria-label='close'], [data-test-id='close-button']"
            )
            for btn in close_btns:
                btn.click()
                time.sleep(0.5)
        except Exception:
            pass

    def close(self):
        self.driver.quit()


# ──────────────────────────────────────────────
# 3. 메타데이터 매니저
# ──────────────────────────────────────────────

class MetadataManager:
    """크롤링 결과 메타데이터 관리 (JSON)"""

    def __init__(self, base_dir: str):
        self.meta_path = os.path.join(base_dir, "_metadata.json")
        self.data = self._load()

    def _load(self) -> dict:
        if os.path.exists(self.meta_path):
            with open(self.meta_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {
            "brand": "Wacky Willy",
            "concept": "Kitsch Street & IP Universe",
            "created_at": datetime.now().isoformat(),
            "categories": {},
            "stats": {"total_collected": 0, "total_downloaded": 0},
        }

    def update_category(self, category: str, items: list[dict], downloaded: int):
        if category not in self.data["categories"]:
            self.data["categories"][category] = {
                "keywords": [],
                "image_count": 0,
                "items": [],
            }

        cat = self.data["categories"][category]
        keywords_used = list(set(item["keyword"] for item in items))
        cat["keywords"] = list(set(cat["keywords"] + keywords_used))
        cat["image_count"] += downloaded
        cat["items"].extend(items)

        self.data["stats"]["total_collected"] += len(items)
        self.data["stats"]["total_downloaded"] += downloaded

    def save(self):
        self.data["updated_at"] = datetime.now().isoformat()
        with open(self.meta_path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def print_summary(self):
        print("\n" + "=" * 60)
        print("  Pinterest Crawl Summary — Wacky Willy Moodboard")
        print("=" * 60)
        for cat, info in self.data["categories"].items():
            print(f"  {cat:20s} : {info['image_count']:4d}장  ({len(info['keywords'])} keywords)")
        print("-" * 60)
        stats = self.data["stats"]
        print(f"  {'TOTAL':20s} : {stats['total_downloaded']:4d}장 다운로드 / {stats['total_collected']}장 수집")
        print("=" * 60)


# ──────────────────────────────────────────────
# 4. 메인 파이프라인
# ──────────────────────────────────────────────

def run_pipeline(args):
    """크롤링 파이프라인 실행"""

    # 저장 경로
    timestamp = datetime.now().strftime("%Y%m%d")
    # 프로젝트 루트의 workspace/ 아래 저장
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    project_root = os.path.dirname(project_root)  # system/ 상위 = 프로젝트 루트
    base_dir = args.output or os.path.join(
        project_root, "workspace", "moodboard", f"pinterest_{timestamp}"
    )
    os.makedirs(base_dir, exist_ok=True)

    meta = MetadataManager(base_dir)
    crawler = PinterestCrawler(
        download_dir=base_dir,
        headless=args.headless,
        use_profile=args.login,
    )

    try:
        # 로그인 (선택)
        if args.login:
            print("[1/5] 크롬 프로필 로그인 모드 (기존 세션 재활용)")
        elif args.email and args.password:
            crawler.login(args.email, args.password)
        else:
            print("[1/5] 비로그인 모드 (검색 결과가 제한될 수 있음)")
            print("  -> 로그인: --login (구글 로그인) 또는 --email/--password")

        # 단일 키워드 모드
        if args.keyword:
            print(f"\n[2/5] 단일 키워드 크롤링: '{args.keyword}'")
            items = crawler.search_and_collect(args.keyword, max_images=args.count)
            print(f"  -> {len(items)}장 수집 완료")

            print("[3/5] 이미지 다운로드 중...")
            downloaded = crawler.download_images(items, subfolder="custom")
            meta.update_category("custom", items, downloaded)
            print(f"  -> {downloaded}장 다운로드 완료")

        # 카테고리 모드 (기본)
        else:
            categories = WACKY_WILLY_KEYWORDS
            if args.category:
                if args.category not in categories:
                    print(f"카테고리 '{args.category}' 없음. 가능한 값:")
                    for k in categories:
                        print(f"  - {k}")
                    return
                categories = {args.category: categories[args.category]}

            total_cats = len(categories)
            for idx, (category, keywords) in enumerate(categories.items(), 1):
                print(f"\n[2/5] 카테고리 {idx}/{total_cats}: {category}")
                print(f"  키워드 {len(keywords)}개")

                all_items = []
                for kw in keywords:
                    print(f"\n  검색: '{kw}'")
                    items = crawler.search_and_collect(
                        kw, max_images=args.count_per_keyword
                    )
                    all_items.extend(items)
                    print(f"  -> {len(items)}장 수집")
                    time.sleep(2)  # 키워드 간 쿨다운

                # 중복 제거 (URL 기준)
                seen = set()
                unique_items = []
                for item in all_items:
                    if item["url"] not in seen:
                        seen.add(item["url"])
                        unique_items.append(item)

                print(f"\n[3/5] {category} 다운로드 중... ({len(unique_items)}장, 중복 제거)")
                downloaded = crawler.download_images(unique_items, subfolder=category)
                meta.update_category(category, unique_items, downloaded)
                print(f"  -> {downloaded}장 다운로드 완료")

                time.sleep(3)  # 카테고리 간 쿨다운

        # 인터랙티브 모드
        if args.interactive:
            run_interactive(crawler, meta, base_dir, args.count)

        # 메타데이터 저장
        print("\n[4/5] 메타데이터 저장 중...")
        meta.save()

        # 결과 요약
        print("\n[5/5] 완료!")
        meta.print_summary()
        print(f"\n  저장 위치: {base_dir}")
        print(f"  메타데이터: {meta.meta_path}")

    finally:
        crawler.close()


# ──────────────────────────────────────────────
# 5. 인터랙티브 모드
# ──────────────────────────────────────────────

def run_interactive(crawler, meta, base_dir: str, default_count: int = 30):
    """키워드를 입력받아 바로 수집하는 대화형 모드"""
    print("\n" + "=" * 60)
    print("  Pinterest Interactive Crawler — Wacky Willy")
    print("=" * 60)
    print("  키워드를 입력하면 핀터레스트에서 이미지를 수집합니다.")
    print("  여러 키워드는 쉼표(,)로 구분하세요.")
    print("  수량 변경: 키워드 뒤에 /숫자 (예: kitsch fashion /50)")
    print("  종료: q 또는 exit")
    print("=" * 60)

    session_total = 0

    while True:
        print()
        user_input = input("  🔍 검색 키워드: ").strip()

        if not user_input:
            continue
        if user_input.lower() in ("q", "quit", "exit", "종료"):
            print(f"\n  세션 종료 — 총 {session_total}장 수집")
            break

        # 수량 파싱 (예: "kitsch fashion /50")
        count = default_count
        if "/" in user_input:
            parts = user_input.rsplit("/", 1)
            try:
                count = int(parts[1].strip())
                user_input = parts[0].strip()
            except ValueError:
                pass

        # 쉼표로 여러 키워드 분리
        keywords = [kw.strip() for kw in user_input.split(",") if kw.strip()]

        # 폴더명 생성 (첫 키워드 기반)
        folder_name = keywords[0].replace(" ", "-")[:30]
        # 파일명 안전 문자만
        folder_name = "".join(c if c.isalnum() or c in "-_" else "-" for c in folder_name)

        all_items = []
        for kw in keywords:
            print(f"\n  검색: '{kw}' (최대 {count}장)")
            items = crawler.search_and_collect(kw, max_images=count)
            all_items.extend(items)
            print(f"  -> {len(items)}장 수집")
            if len(keywords) > 1:
                time.sleep(2)

        # 중복 제거
        seen = set()
        unique = []
        for item in all_items:
            if item["url"] not in seen:
                seen.add(item["url"])
                unique.append(item)

        print(f"\n  다운로드 중... ({len(unique)}장, 중복 제거)")
        downloaded = crawler.download_images(unique, subfolder=folder_name)
        meta.update_category(folder_name, unique, downloaded)
        meta.save()

        session_total += downloaded
        save_path = os.path.join(base_dir, folder_name)
        print(f"  -> {downloaded}장 다운로드 완료")
        print(f"  -> 저장: {save_path}")


# ──────────────────────────────────────────────
# 6. CLI
# ──────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Pinterest Image Crawler for Wacky Willy Moodboard"
    )

    # 인증
    parser.add_argument("--login", action="store_true",
                        help="브라우저에서 수동 로그인 (구글 로그인 지원, 쿠키 자동 저장)")
    parser.add_argument("--email", help="핀터레스트 이메일 로그인")
    parser.add_argument("--password", help="핀터레스트 비밀번호")

    # 크롤링 모드
    parser.add_argument("--interactive", "-i", action="store_true",
                        help="인터랙티브 모드 — 키워드를 입력하면 바로 수집")
    parser.add_argument("--keyword", help="단일 키워드 검색")
    parser.add_argument("--category", help="특정 카테고리만 크롤링",
                        choices=list(WACKY_WILLY_KEYWORDS.keys()))
    parser.add_argument("--count", type=int, default=50,
                        help="단일 키워드 모드: 수집할 이미지 수 (기본: 50)")
    parser.add_argument("--count-per-keyword", type=int, default=30,
                        help="카테고리 모드: 키워드당 이미지 수 (기본: 30)")

    # 옵션
    parser.add_argument("--output", "-o", help="저장 디렉토리 경로")
    parser.add_argument("--headless", action="store_true",
                        help="헤드리스 모드 (브라우저 안 보임)")

    args = parser.parse_args()
    run_pipeline(args)


if __name__ == "__main__":
    main()
