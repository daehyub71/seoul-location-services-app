import { test, expect } from '@playwright/test'

test.describe('주소 검색', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
    // Wait for page to load
    await expect(page.locator('h1')).toContainText('Seoul Location Services')
  })

  test('주소 입력 및 검색', async ({ page }) => {
    // Find the address input field
    const addressInput = page.getByPlaceholder(/주소를 검색하세요/i)
    await expect(addressInput).toBeVisible()

    // Type an address
    await addressInput.fill('서울시청')

    // Click the search button
    const searchButton = page.getByRole('button', { name: /검색/i })
    await expect(searchButton).toBeVisible()
    await expect(searchButton).toBeEnabled()
    await searchButton.click()

    // Wait for geocoding to complete (check for success message or loading indicator)
    await page.waitForTimeout(3000)

    // Check if search was successful (look for success message or coordinate display)
    const successMessage = page.getByText(/선택된 주소/i).or(page.getByText(/위도:/i))
    await expect(successMessage).toBeVisible({ timeout: 10000 })

    // Verify service list is updated
    const serviceList = page.locator('[class*="service"]').first()
    await expect(serviceList).toBeVisible({ timeout: 5000 })
  })

  test('주소 검색 후 지도 이동 확인', async ({ page }) => {
    // Input address
    const addressInput = page.getByPlaceholder(/주소를 검색하세요/i)
    await addressInput.fill('강남역')

    // Search
    const searchButton = page.getByRole('button', { name: /검색/i })
    await searchButton.click()

    // Wait for geocoding
    await page.waitForTimeout(3000)

    // Check if coordinates are displayed
    const coords = page.getByText(/위도:/)
    await expect(coords).toBeVisible({ timeout: 10000 })

    // Verify map is still visible (shouldn't crash)
    const mapContainer = page.locator('#map, [class*="kakao-map"]').first()
    await expect(mapContainer).toBeVisible()
  })

  test('잘못된 주소 검색 시 에러 처리', async ({ page }) => {
    // Input invalid address
    const addressInput = page.getByPlaceholder(/주소를 검색하세요/i)
    await addressInput.fill('이상한주소123456')

    // Search
    const searchButton = page.getByRole('button', { name: /검색/i })
    await searchButton.click()

    // Wait for error message
    await page.waitForTimeout(3000)

    // Check for error message
    const errorMessage = page.getByText(/주소를 찾을 수 없습니다/i)
    await expect(errorMessage).toBeVisible({ timeout: 10000 })
  })

  test('주소 입력 클리어 기능', async ({ page }) => {
    // Input address
    const addressInput = page.getByPlaceholder(/주소를 검색하세요/i)
    await addressInput.fill('서울시청')

    // Click clear button (X icon)
    const clearButton = page.getByLabel(/Clear input/i)
    await expect(clearButton).toBeVisible()
    await clearButton.click()

    // Verify input is cleared
    await expect(addressInput).toHaveValue('')
  })

  test('Enter 키로 검색 실행', async ({ page }) => {
    // Input address
    const addressInput = page.getByPlaceholder(/주소를 검색하세요/i)
    await addressInput.fill('서울시청')

    // Press Enter key
    await addressInput.press('Enter')

    // Wait for geocoding
    await page.waitForTimeout(3000)

    // Check if search was successful
    const successMessage = page.getByText(/선택된 주소/i).or(page.getByText(/위도:/i))
    await expect(successMessage).toBeVisible({ timeout: 10000 })
  })
})
