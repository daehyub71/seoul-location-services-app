# Supabase 스키마 매핑 문서

**작성일**: 2025-11-02
**목적**: Collector와 Supabase 테이블 스키마 간의 필드명 매핑

---

## 1. cultural_events (문화행사)

### Supabase 스키마 컬럼
```sql
- id UUID
- api_id VARCHAR(100) UNIQUE NOT NULL
- title VARCHAR(500) NOT NULL
- codename VARCHAR(100)
- guname VARCHAR(50)
- place VARCHAR(300)
- org_name VARCHAR(200)
- use_trgt VARCHAR(200)
- use_fee VARCHAR(100)
- player VARCHAR(300)
- program VARCHAR(1000)
- etc_desc TEXT
- org_link TEXT
- main_img TEXT
- rgstdate DATE
- ticket VARCHAR(200)
- strtdate DATE
- end_date DATE
- themecode VARCHAR(100)
- lot DECIMAL(11, 8)  -- Longitude (경도)
- lat DECIMAL(10, 8)  -- Latitude (위도)
- is_free VARCHAR(10)
- hmpg_addr TEXT
- location GEOGRAPHY(POINT, 4326)
- created_at TIMESTAMPTZ
- updated_at TIMESTAMPTZ
- data_source VARCHAR(50)
```

### Collector 수정 필요 사항
- ❌ `category` → 스키마에 없음 (제거 필요)
- ❌ `start_date` → ✅ `strtdate`로 변경
- ❌ `image_url` → ✅ `main_img`로 변경

---

## 2. libraries (도서관)

### Supabase 스키마 컬럼
```sql
- id UUID
- api_id VARCHAR(100) UNIQUE NOT NULL
- library_name VARCHAR(300) NOT NULL
- library_type VARCHAR(50) NOT NULL  -- 'public' or 'disabled'
- guname VARCHAR(50)
- address VARCHAR(500)
- tel VARCHAR(50)
- homepage TEXT
- latitude DECIMAL(10, 8)
- longitude DECIMAL(11, 8)
- opertime VARCHAR(200)
- closing_day VARCHAR(100)
- book_count INTEGER
- seat_count INTEGER
- facilities TEXT
- location GEOGRAPHY(POINT, 4326)
- created_at TIMESTAMPTZ
- updated_at TIMESTAMPTZ
- data_source VARCHAR(50)
```

### Collector 수정 필요 사항
- ❌ `phone` → ✅ `tel`로 변경
- ❌ `closed_days` → ✅ `closing_day`로 변경
- ❌ `operating_hours` → ✅ `opertime`으로 변경

---

## 3. cultural_spaces (문화공간)

### Supabase 스키마 컬럼
```sql
- id UUID
- api_id VARCHAR(100) UNIQUE NOT NULL
- fac_name VARCHAR(300) NOT NULL
- guname VARCHAR(50)
- subjcode VARCHAR(100)
- fac_code VARCHAR(50)
- codename VARCHAR(100)
- addr VARCHAR(500)
- zipcode VARCHAR(20)
- telno VARCHAR(50)
- homepage TEXT
- restroomyn VARCHAR(10)
- parking_info VARCHAR(200)
- main_purps TEXT
- latitude DECIMAL(10, 8)
- longitude DECIMAL(11, 8)
- location GEOGRAPHY(POINT, 4326)
- created_at TIMESTAMPTZ
- updated_at TIMESTAMPTZ
- data_source VARCHAR(50)
```

### Collector 수정 필요 사항
- ❌ `name` → ✅ `fac_name`으로 변경
- ❌ `address` → ✅ `addr`로 변경
- ❌ `phone` → ✅ `telno`로 변경
- ❌ `description` → ✅ `main_purps`로 변경
- ❌ 추가 필드 필요:
  - `subjcode` (API: SUBJCODE)
  - `fac_code` (API: FAC_CODE)
  - `zipcode` (API: ZIPCODE)
  - `restroomyn` (API: RESTROOMYN)
  - `parking_info` (API에서 파싱 필요)
- ❌ 제거할 필드:
  - `is_free` (스키마에 없음)
  - `rsrv_link` (스키마에 없음)
  - `main_img_url` (스키마에 없음)
  - `oper_time` (스키마에 없음)
  - `restde_guid_cn` (스키마에 없음)
  - `entrn_fee_info` (스키마에 없음)

---

## 4. public_reservations (공공예약)

### Supabase 스키마 컬럼
```sql
- id UUID
- api_id VARCHAR(100) UNIQUE NOT NULL
- service_type VARCHAR(50) NOT NULL  -- 'medical', 'education', 'culture', 'general'
- svcid VARCHAR(50)
- maxclassnm VARCHAR(100)
- minclassnm VARCHAR(100)
- svcstatnm VARCHAR(50)
- svcnm VARCHAR(500) NOT NULL
- payatnm VARCHAR(50)
- placenm VARCHAR(300)
- usetgtinfo VARCHAR(200)
- svcurl TEXT
- x_coord DECIMAL(11, 8)  -- X (Longitude)
- y_coord DECIMAL(10, 8)  -- Y (Latitude)
- svcopnbgndt DATE
- svcopnenddt DATE
- rcptbgndt TIMESTAMPTZ
- rcptenddt TIMESTAMPTZ
- areanm VARCHAR(100)
- imgurl TEXT
- dtlcont TEXT
- telno VARCHAR(50)
- v_max INTEGER
- v_min INTEGER
- revstddaynm VARCHAR(100)
- revstdday INTEGER
- location GEOGRAPHY(POINT, 4326)
- created_at TIMESTAMPTZ
- updated_at TIMESTAMPTZ
- data_source VARCHAR(50)
```

### Collector 수정 필요 사항
- ❌ `category` → ✅ `service_type`로 변경 (medical/education/culture)
- ❌ `service_name` → ✅ `svcnm`으로 변경
- ❌ `place_name` → ✅ `placenm`으로 변경
- ❌ `payment_method` → ✅ `payatnm`로 변경
- ❌ `reception_start` → ✅ `rcptbgndt`로 변경
- ❌ `reception_end` → ✅ `rcptenddt`로 변경
- ❌ `service_start` → ✅ `svcopnbgndt`로 변경
- ❌ `service_end` → ✅ `svcopnenddt`로 변경
- ❌ `district` → ✅ `areanm`으로 변경
- ❌ `description` → ✅ `dtlcont`로 변경
- ❌ `phone` → ✅ `telno`로 변경
- ❌ `max_capacity` → ✅ `v_max`로 변경
- ❌ `min_capacity` → ✅ `v_min`로 변경
- ❌ `reservation_deadline` → ✅ `revstddaynm`으로 변경
- ❌ `image_url` → ✅ `imgurl`로 변경
- ❌ `lat` → ✅ `y_coord`로 변경
- ❌ `lot` → ✅ `x_coord`로 변경
- ❌ 추가 필드 필요:
  - `svcid` (API: SVCID)
  - `maxclassnm` (API: MAXCLASSNM)
  - `minclassnm` (API: MINCLASSNM)
  - `svcstatnm` (API: SVCSTATNM)
  - `usetgtinfo` (API: USETGTINFO)
  - `svcurl` (API: SVCURL)
  - `revstdday` (API: REVSTDDAY)
- ❌ 제거할 필드:
  - `service_url`, `service_status`, `target_audience`, `cost_info`, `notice`, `operation_hours`, `facilities`, `reservation_url` (모두 스키마에 없음)

---

## 5. future_heritages (서울미래유산)

### Supabase 스키마 컬럼
```sql
- id UUID
- api_id VARCHAR(100) UNIQUE NOT NULL
- no INTEGER
- main_category VARCHAR(100)
- sub_category VARCHAR(100)
- name VARCHAR(300) NOT NULL
- year_designated INTEGER
- gu_name VARCHAR(50)
- dong_name VARCHAR(100)
- address VARCHAR(500)
- latitude DECIMAL(10, 8)
- longitude DECIMAL(11, 8)
- description TEXT
- reason TEXT
- main_img TEXT
- location GEOGRAPHY(POINT, 4326)
- created_at TIMESTAMPTZ
- updated_at TIMESTAMPTZ
- data_source VARCHAR(50)
```

### Collector 수정 필요 사항
- ❌ `category` → ✅ `main_category`로 변경
- ❌ `era` → 스키마에 없음 (제거하고 `sub_category` 사용)
- ❌ `content` → ✅ `description`으로 변경
- ❌ `main_purpose` → ✅ `reason`으로 변경
- ❌ `registered_at` → ✅ `year_designated`로 변경 (DATE → INTEGER)
- ❌ `main_image` → ✅ `main_img`로 변경
- ❌ `lat` → ✅ `latitude`로 변경
- ❌ `lot` → ✅ `longitude`로 변경
- ❌ 추가 필드 필요:
  - `no` (API: NO)
  - `gu_name` (API: GU_NAME)
  - `dong_name` (API: DONG_NAME)

---

## 6. collection_logs (수집 로그)

### Supabase 스키마 컬럼
```sql
- id UUID
- api_endpoint VARCHAR(100) NOT NULL
- collection_status VARCHAR(50) NOT NULL  -- 'success', 'partial', 'failed'
- total_records INTEGER DEFAULT 0
- new_records INTEGER DEFAULT 0
- updated_records INTEGER DEFAULT 0
- failed_records INTEGER DEFAULT 0
- error_message TEXT
- started_at TIMESTAMPTZ NOT NULL
- completed_at TIMESTAMPTZ
- duration_seconds INTEGER
- created_at TIMESTAMPTZ
```

### Collector 수정 필요 사항
- ✅ 이미 올바르게 매핑됨

---

## API 필드명 → Supabase 컬럼명 매핑 요약

### Cultural Events (culturalEventInfo)
```
TITLE → title
CODENAME → codename
GUNAME → guname
PLACE → place
ORG_NAME → org_name
USE_TRGT → use_trgt
USE_FEE → use_fee
PLAYER → player
PROGRAM → program
ETC_DESC → etc_desc
ORG_LINK → org_link
MAIN_IMG → main_img
RGSTDATE → rgstdate
TICKET → ticket
STRTDATE → strtdate
END_DATE → end_date
THEMECODE → themecode
LOT → lot
LAT → lat
IS_FREE → is_free
HMPG_ADDR → hmpg_addr
```

### Libraries (SeoulPublicLibraryInfo / SeoulDisableLibraryInfo)
```
LBRRY_NAME → library_name
library_type → library_type (Collector에서 생성: 'public' or 'disabled')
ADRES → address
XCNTS → longitude
YDNTS → latitude
TEL_NO → tel
HMPG_URL → homepage
OPERTIME → opertime
FDRM_CLOSE → closing_day
BOOK_CO → book_count
SEAT_CO → seat_count
```

### Cultural Spaces (culturalSpaceInfo)
```
FAC_NAME → fac_name
SUBJCODE → subjcode
FAC_CODE → fac_code
CODENAME → codename
ADDR → addr
ZIPCODE → zipcode
TELNO → telno
HOMEPAGE → homepage
RESTROOMYN → restroomyn
MAIN_PURPS → main_purps
```

### Public Reservations (ListPublicReservation*)
```
service_type → service_type (Collector에서 생성: 'medical'/'education'/'culture')
SVCID → svcid
MAXCLASSNM → maxclassnm
MINCLASSNM → minclassnm
SVCSTATNM → svcstatnm
SVCNM → svcnm
PAYATNM → payatnm
PLACENM → placenm
USETGTINFO → usetgtinfo
SVCURL → svcurl
X → x_coord (주의: X가 경도)
Y → y_coord (주의: Y가 위도)
SVCOPNBGNDT → svcopnbgndt
SVCOPNENDDT → svcopnenddt
RCPTBGNDT → rcptbgndt
RCPTENDDT → rcptenddt
AREANM → areanm
IMGURL → imgurl
DTLCONT → dtlcont
TELNO → telno
V_MAX → v_max
V_MIN → v_min
REVSTDDAYNM → revstddaynm
REVSTDDAY → revstdday
```

### Future Heritages (futureHeritageInfo)
```
NO → no
CATEGORY → main_category (또는 CATEGORY를 sub_category로 사용)
NM → name
REGIST_DATE → year_designated (연도만 추출)
ADDR → address
CONTENT → description
MAIN_PURPS → reason
T_IMAGE → main_img
MANAGE_NO → api_id (관리번호가 있으면 사용)
```

---

## 날짜 파싱 포맷 정리

### API 응답 날짜 포맷
1. **문화행사**: `YYYY-MM-DD` (예: `2025-10-20`)
2. **공공예약**: `YYYY-MM-DD HH:MM:SS.0` (예: `2025-10-20 10:00:00.0`)
3. **미래유산**: `YYYY` 또는 `YYYY-MM-DD`

### 필요한 파싱 로직
```python
def parse_date_flexible(date_str, target_type='date'):
    """
    여러 형식의 날짜 문자열 파싱

    Args:
        date_str: 날짜 문자열
        target_type: 'date' (DATE), 'timestamp' (TIMESTAMPTZ), 'year' (INTEGER)

    Returns:
        파싱된 날짜 또는 None
    """
    if not date_str:
        return None

    # Datetime 형식 (2025-10-20 10:00:00.0)
    if ' ' in date_str:
        date_str = date_str.split()[0]  # 날짜 부분만 추출

    # 포맷 시도 목록
    formats = [
        '%Y-%m-%d',      # 2025-10-20
        '%Y%m%d',        # 20251020
        '%Y',            # 2025 (year only)
    ]

    for fmt in formats:
        try:
            parsed = datetime.strptime(date_str, fmt)
            if target_type == 'year':
                return parsed.year
            elif target_type == 'date':
                return parsed.strftime('%Y-%m-%d')
            else:  # timestamp
                return parsed.isoformat()
        except ValueError:
            continue

    return None
```

---

## 다음 단계

1. ✅ BaseCollector의 `parse_date()` 메서드 수정
2. ✅ 각 Collector의 `transform_record()` 메서드 수정
3. ✅ 테스트 실행 및 검증

