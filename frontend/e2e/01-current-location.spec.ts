import { test, expect } from '@playwright/test'

test.describe('현재 위치 조회', () => {
  test.beforeEach(async ({ page, context }) => {
    // Mock geolocation to Seoul City Hall
    await context.grantPermissions(['geolocation'])
    await context.setGeolocation({ latitude: 37.5665, longitude: 126.978 })
  })

  test('GPS 위치 허용 및 지도 중심 이동 확인', async ({ page }) => {
    await page.goto('/')

    // Check if page loads
    await expect(page.locator('h1')).toContainText('Seoul Location Services')

    // Click "현재 위치" button
    const currentLocationButton = page.getByRole('button', { name: /현재 위치/i })
    await expect(currentLocationButton).toBeVisible()
    await currentLocationButton.click()

    // Wait for location to be updated (check if button shows loading or success)
    await page.waitForTimeout(2000)

    // Verify that services are loaded (check service list count)
    const serviceList = page.locator('[class*="service"]').first()
    await expect(serviceList).toBeVisible({ timeout: 10000 })

    // Check if service count is displayed
    const serviceCount = page.getByText(/개\)/)
    await expect(serviceCount).toBeVisible({ timeout: 5000 })
  })

  test('주변 서비스 마커 표시 확인', async ({ page }) => {
    await page.goto('/')

    // Click current location button
    const currentLocationButton = page.getByRole('button', { name: /현재 위치/i })
    await currentLocationButton.click()

    // Wait for map to load
    await page.waitForTimeout(3000)

    // Check if Kakao Map is loaded (look for map container)
    const mapContainer = page.locator('#map, [class*="kakao-map"]').first()
    await expect(mapContainer).toBeVisible({ timeout: 10000 })

    // Verify service list has items
    const serviceItems = page.locator('[class*="service"]')
    const count = await serviceItems.count()
    expect(count).toBeGreaterThan(0)
  })

  test('검색 반경 변경 테스트', async ({ page }) => {
    await page.goto('/')

    // Select search radius dropdown
    const radiusSelect = page.locator('select').filter({ hasText: /km/ })
    await expect(radiusSelect).toBeVisible()

    // Change radius to 2km
    await radiusSelect.selectOption('2000')

    // Wait for services to reload
    await page.waitForTimeout(2000)

    // Verify services are filtered
    await expect(page.getByText(/개\)/)).toBeVisible()
  })
})
