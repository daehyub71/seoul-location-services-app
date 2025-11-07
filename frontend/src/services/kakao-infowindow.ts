import type { AnyService } from '@/types/services'
import { CATEGORY_COLORS, CATEGORY_LABELS } from '@/types/services'

/**
 * Create InfoWindow content HTML for a service
 * Displays category-specific fields based on user requirements
 */
export function createServiceInfoWindowContent(service: AnyService): string {
  const categoryLabel = CATEGORY_LABELS[service.category]
  const categoryColor = CATEGORY_COLORS[service.category]

  // Helper to safely get value from service or raw_data
  const getValue = (key: string): any => {
    const serviceObj = service as any
    return serviceObj[key] ?? serviceObj.raw_data?.[key]
  }

  // Helper to format field values
  const formatValue = (value: any, isUrl: boolean = false, isImage: boolean = false): string => {
    if (value === null || value === undefined || value === '') {
      return '-'
    }

    // Image URL
    if (isImage && typeof value === 'string') {
      return `<img src="${value}" style="max-width: 100%; height: auto; border-radius: 8px; margin-top: 8px;" alt="이미지" />`
    }

    // Check if it's a URL or marked as URL
    if (isUrl || (typeof value === 'string' && (value.startsWith('http://') || value.startsWith('https://')))) {
      return `<a href="${value}" target="_blank" style="color: #1971C2; text-decoration: underline;">바로가기</a>`
    }

    // Return as string
    return String(value).replace(/</g, '&lt;').replace(/>/g, '&gt;')
  }

  // Helper to add info row
  const addRow = (label: string, value: any, isUrl: boolean = false, isImage: boolean = false): string => {
    const formattedValue = formatValue(value, isUrl, isImage)
    if (formattedValue === '-') return ''

    return `
      <div class="info-row">
        <span class="label">${label}:</span>
        <span class="value">${formattedValue}</span>
      </div>
    `
  }

  let detailsHtml = ''

  // Category-specific field mapping
  switch (service.category) {
    case 'libraries': {
      // 도서관: 도서관명/구명/주소/전화번호/홈페이지(링크)/운영시간/정기휴관일/도서관구분명
      detailsHtml += addRow('도서관명', getValue('lbrry_name') || getValue('library_name') || service.name)
      detailsHtml += addRow('구명', getValue('guname') || getValue('region'))
      detailsHtml += addRow('주소', getValue('adres') || getValue('address') || service.address)
      detailsHtml += addRow('전화번호', getValue('tel_no') || getValue('tel'))
      detailsHtml += addRow('홈페이지', getValue('homepage') || getValue('hmpg_addr'), true)
      detailsHtml += addRow('운영시간', getValue('opertime') || getValue('operTime') || getValue('weekday_optime'))
      detailsHtml += addRow('정기휴관일', getValue('closing_day') || getValue('close_day') || getValue('closeDay'))
      detailsHtml += addRow('도서관구분', getValue('libraty_type') || getValue('code_value') || getValue('lbrry_se_name'))
      break
    }

    case 'cultural_spaces': {
      // 문화공간: 주제분류/문화시설명/주소/구명/전화번호/홈페이지/관람시간/관람료/휴관일/시설소개/무료구분
      detailsHtml += addRow('주제분류', getValue('subjcode') || getValue('codename'))
      detailsHtml += addRow('문화시설명', getValue('fac_name') || service.name)
      detailsHtml += addRow('주소', getValue('adres') || getValue('address') || service.address)
      detailsHtml += addRow('구명', getValue('region') || getValue('guname'))
      detailsHtml += addRow('전화번호', getValue('tel_no') || getValue('tel'))
      detailsHtml += addRow('홈페이지', getValue('homepage') || getValue('hmpg_addr'), true)
      detailsHtml += addRow('관람시간', getValue('openTime') || getValue('open_time'))

      const isFree = getValue('is_free') || getValue('fee_use_yn')
      if (isFree && (isFree === '무료' || isFree === 'N' || isFree === 'n')) {
        detailsHtml += addRow('관람료', '무료')
      } else {
        detailsHtml += addRow('관람료', getValue('fee') || getValue('adm_fee'))
      }

      detailsHtml += addRow('휴관일', getValue('close_day') || getValue('closeDay'))
      detailsHtml += addRow('시설소개', getValue('intro') || getValue('description'))
      break
    }

    case 'public_reservations': {
      // 공공예약: 대분류명/소분류명/서비스상태/서비스명/무료구분/장소명/서비스대상/홈페이지(링크)/시작일시/종료일시/구명/상세내용/전화번호
      detailsHtml += addRow('대분류', getValue('maxclassname') || getValue('category1'))
      detailsHtml += addRow('소분류', getValue('minclassname') || getValue('category2'))
      detailsHtml += addRow('서비스상태', getValue('svcstatnm') || getValue('status'))
      detailsHtml += addRow('서비스명', getValue('svcnm') || service.name)

      const payAt = getValue('payatnm') || getValue('is_free')
      if (payAt && (payAt.includes('무료') || payAt === 'N')) {
        detailsHtml += addRow('이용료', '무료')
      } else {
        detailsHtml += addRow('이용료', getValue('rcptcost') || '유료')
      }

      detailsHtml += addRow('장소명', getValue('placenm') || getValue('place'))
      detailsHtml += addRow('서비스대상', getValue('usetgtinfo') || getValue('target'))
      detailsHtml += addRow('홈페이지', getValue('svcurl') || getValue('homepage'), true)
      detailsHtml += addRow('시작일시', getValue('rcptbgndt') || getValue('start_date'))
      detailsHtml += addRow('종료일시', getValue('rcptenddt') || getValue('end_date'))
      detailsHtml += addRow('구명', getValue('areanm') || getValue('guname'))
      detailsHtml += addRow('상세내용', getValue('dtlcont') || getValue('description'))
      detailsHtml += addRow('전화번호', getValue('telno') || getValue('tel'))
      break
    }

    case 'future_heritage': {
      // 미래유산: 미래유산명/구명/주소/분류명/대분류명/소분류명/이력사항/보존필요성/설명문/주차장여부/주차대수/주차비용/주차시간/이미지
      detailsHtml += addRow('미래유산명', getValue('future_heritage_nm') || getValue('name') || service.name)
      detailsHtml += addRow('구명', getValue('location') || getValue('guname'))
      detailsHtml += addRow('주소', getValue('address') || getValue('addr') || service.address)
      detailsHtml += addRow('분류명', getValue('classification') || getValue('category_nm'))
      detailsHtml += addRow('대분류', getValue('large_category') || getValue('main_category'))
      detailsHtml += addRow('소분류', getValue('medium_category') || getValue('sub_category'))
      detailsHtml += addRow('이력사항', getValue('history') || getValue('background'))
      detailsHtml += addRow('보존필요성', getValue('preservation_necessity') || getValue('reason'))
      detailsHtml += addRow('설명문', getValue('description') || getValue('content'))

      const parkingYn = getValue('parking_available') || getValue('parking_yn')
      detailsHtml += addRow('주차장', parkingYn === 'Y' || parkingYn === 'y' ? '가능' : '불가')

      if (parkingYn === 'Y' || parkingYn === 'y') {
        detailsHtml += addRow('주차대수', getValue('parking_capacity') || getValue('parking_cnt'))
        detailsHtml += addRow('주차비용', getValue('parking_fee') || getValue('parking_cost'))
        detailsHtml += addRow('주차시간', getValue('parking_hours') || getValue('parking_time'))
      }

      // 이미지 (마지막에 추가)
      const imgPath = getValue('main_img') || getValue('image_path') || getValue('img_url')
      if (imgPath) {
        detailsHtml += addRow('사진', imgPath, false, true)
      }
      break
    }

    case 'cultural_events':
    default: {
      // 문화행사 - 주요 필드만 표시
      detailsHtml += addRow('행사명', getValue('title') || service.name)
      detailsHtml += addRow('구명', getValue('guname'))
      detailsHtml += addRow('장소', getValue('place'))
      detailsHtml += addRow('주관', getValue('org_name'))
      detailsHtml += addRow('시작일', getValue('strtdate'))
      detailsHtml += addRow('종료일', getValue('end_date'))
      detailsHtml += addRow('이용대상', getValue('use_trgt'))
      detailsHtml += addRow('이용료', getValue('is_free') || getValue('use_fee'))
      detailsHtml += addRow('프로그램', getValue('program'))
      detailsHtml += addRow('홈페이지', getValue('hmpg_addr') || getValue('org_link'), true)

      const mainImg = getValue('main_img')
      if (mainImg) {
        detailsHtml += addRow('포스터', mainImg, false, true)
      }
      break
    }
  }

  // Build complete HTML
  const html = `
    <div class="kakao-infowindow" style="padding: 16px; min-width: 320px; max-width: 450px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;">
      <div style="display: flex; align-items: center; margin-bottom: 12px; padding-bottom: 12px; border-bottom: 2px solid ${categoryColor};">
        <div style="width: 12px; height: 12px; border-radius: 50%; background-color: ${categoryColor}; margin-right: 8px;"></div>
        <div style="flex: 1;">
          <div style="font-size: 10px; color: #868e96; text-transform: uppercase; letter-spacing: 0.5px;">${categoryLabel}</div>
          <div style="font-size: 16px; font-weight: 700; color: #212529; margin-top: 2px;">${service.name}</div>
        </div>
      </div>
      <div style="font-size: 13px; line-height: 1.6; color: #495057; max-height: 500px; overflow-y: auto;">
        ${detailsHtml}
      </div>
    </div>
    <style>
      .kakao-infowindow .info-row {
        margin-bottom: 8px;
        display: flex;
        gap: 8px;
        align-items: flex-start;
      }
      .kakao-infowindow .label {
        font-weight: 600;
        color: #495057;
        min-width: 80px;
        flex-shrink: 0;
      }
      .kakao-infowindow .value {
        flex: 1;
        word-break: break-word;
        white-space: pre-wrap;
      }
      .kakao-infowindow a {
        word-break: break-all;
      }
    </style>
  `

  return html
}
