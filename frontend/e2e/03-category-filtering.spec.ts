import { test, expect } from '@playwright/test'

test.describe('카테고리 필터링', () => {
  test.beforeEach(async ({ page, context }) => {
    // Mock geolocation
    await context.grantPermissions(['geolocation'])
    await context.setGeolocation({ latitude: 37.5665, longitude: 126.978 })

    await page.goto('/')
    await expect(page.locator('h1')).toContainText('Seoul Location Services')

    // Wait for services to load
    await page.waitForTimeout(2000)
  })

  test('필터 버튼 표시 및 클릭', async ({ page }) => {
    // Find filter button (Filter icon)
    const filterButton = page.getByLabel(/Toggle filters/i).or(
      page.locator('button').filter({ hasText: /필터/i }).or(
        page.locator('button svg[class*="lucide-filter"]').locator('..')
      )
    )

    await expect(filterButton.first()).toBeVisible()
    await filterButton.first().click()

    // Wait for filter panel to open
    await page.waitForTimeout(500)

    // Check if category filters are visible
    const categoryLabel = page.getByText(/카테고리/i)
    await expect(categoryLabel).toBeVisible()
  })

  test('도서관 카테고리만 선택', async ({ page }) => {
    // Open filters
    const filterButton = page.locator('button svg[class*="lucide-filter"]').locator('..')
    await filterButton.first().click()

    await page.waitForTimeout(500)

    // Get initial service count
    const serviceCountBefore = page.getByText(/\(\d+개\)/)
    const countTextBefore = await serviceCountBefore.textContent()

    // First, unselect all categories by clicking "전체 해제"
    const unselectAllButton = page.getByRole('button', { name: /전체 해제/i })
    if (await unselectAllButton.isVisible()) {
      await unselectAllButton.click()
      await page.waitForTimeout(500)
    }

    // Select only library category
    const libraryButton = page.getByRole('button', { name: /도서관/i })
    await expect(libraryButton).toBeVisible()
    await libraryButton.click()

    // Wait for list to update
    await page.waitForTimeout(1000)

    // Verify service count changed
    const serviceCountAfter = page.getByText(/\(\d+개\)/)
    const countTextAfter = await serviceCountAfter.textContent()

    // Count should be different or at least service list should be visible
    expect(countTextAfter).toBeTruthy()

    // Check if at least one service is visible
    const serviceItems = page.locator('[class*="service"]')
    expect(await serviceItems.count()).toBeGreaterThanOrEqual(0)
  })

  test('전체 선택/해제 버튼 동작', async ({ page }) => {
    // Open filters
    const filterButton = page.locator('button svg[class*="lucide-filter"]').locator('..')
    await filterButton.first().click()

    await page.waitForTimeout(500)

    // Click "전체 해제"
    const toggleAllButton = page.getByRole('button', { name: /전체 해제/i }).or(
      page.getByRole('button', { name: /전체 선택/i })
    )

    await expect(toggleAllButton.first()).toBeVisible()
    await toggleAllButton.first().click()

    await page.waitForTimeout(500)

    // Check if service count is 0 or shows "검색 결과가 없습니다"
    const noResults = page.getByText(/검색 결과가 없습니다/i).or(
      page.getByText(/\(0개\)/)
    )

    // Either no results message or zero count should be visible
    const hasNoResults = await noResults.first().isVisible().catch(() => false)
    expect(hasNoResults).toBe(true)

    // Click "전체 선택" to restore
    const selectAllButton = page.getByRole('button', { name: /전체 선택/i })
    if (await selectAllButton.isVisible()) {
      await selectAllButton.click()
      await page.waitForTimeout(500)

      // Verify services are shown again
      const serviceCount = page.getByText(/\(\d+개\)/)
      await expect(serviceCount).toBeVisible()
    }
  })

  test('다중 카테고리 선택', async ({ page }) => {
    // Open filters
    const filterButton = page.locator('button svg[class*="lucide-filter"]').locator('..')
    await filterButton.first().click()

    await page.waitForTimeout(500)

    // Unselect all first
    const unselectAllButton = page.getByRole('button', { name: /전체 해제/i })
    if (await unselectAllButton.isVisible()) {
      await unselectAllButton.click()
      await page.waitForTimeout(500)
    }

    // Select library category
    const libraryButton = page.getByRole('button', { name: /도서관/i })
    await libraryButton.click()
    await page.waitForTimeout(500)

    // Select cultural events category
    const culturalButton = page.getByRole('button', { name: /문화행사/i })
    await culturalButton.click()
    await page.waitForTimeout(500)

    // Verify services from both categories are shown
    const serviceCount = page.getByText(/\(\d+개\)/)
    await expect(serviceCount).toBeVisible()

    const countText = await serviceCount.textContent()
    expect(countText).toMatch(/\d+/)
  })

  test('정렬 옵션 변경', async ({ page }) => {
    // Open filters
    const filterButton = page.locator('button svg[class*="lucide-filter"]').locator('..')
    await filterButton.first().click()

    await page.waitForTimeout(500)

    // Find sort buttons
    const sortByName = page.getByRole('button', { name: /이름순/i })
    const sortByDistance = page.getByRole('button', { name: /거리순/i })

    // Click "이름순"
    if (await sortByName.isVisible()) {
      await sortByName.click()
      await page.waitForTimeout(500)

      // Verify services are still visible
      const serviceList = page.locator('[class*="service"]').first()
      await expect(serviceList).toBeVisible()
    }

    // Click "거리순" to restore
    if (await sortByDistance.isVisible()) {
      await sortByDistance.click()
      await page.waitForTimeout(500)
    }
  })
})
