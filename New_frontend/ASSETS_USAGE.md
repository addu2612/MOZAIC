# Feather Assets Usage Tracking

This file tracks which SVG files from `public/assets/feather/` are currently being used in the project.

**Note**: Assets have been moved to the `public/assets/` folder for proper deployment on Vercel. All paths use `/assets/` (relative to public folder).

## Currently Used Assets

The following feather SVG files are actively used in the project:

### Login Page (`src/components/common/Login.jsx`)
- ✅ `facebook.svg` - Social login button
- ✅ `linkedin.svg` - Social login button
- ✅ `twitter.svg` - Social login button
- ✅ `instagram.svg` - Social login button

### Dashboard Components

#### Main Dashboard (`src/components/protected/Dashboard/Dashboard.jsx`)
- ✅ `home.svg` - Breadcrumb home icon
- ✅ `chevron-right.svg` - Breadcrumb separator (used 2x)

#### WelcomeCard (`src/components/protected/Dashboard/WelcomeCard.jsx`)
- ✅ `briefcase.svg` - Weather icon

#### WelcomeCard (`src/components/protected/Dashboard/WelcomeCard.jsx`)
- ✅ `sun.svg` - Weather icon
- ✅ `check-circle.svg` - User verification badge

#### Dashboard Cards (Multiple Components)
- ✅ `more-vertical.svg` - Card menu icon (used in RevenueCard, UsersCard, InvestmentCard, EarningCard, AppointmentCard, CountryCard)

#### NavBar (`src/components/protected/Dashboard/NavBar.jsx`)
- ✅ `menu.svg` - Sidebar toggle button
- ✅ `chevron-down.svg` - Dropdown menu indicator
- ✅ `search.svg` - Search input icon
- ✅ `bookmark.svg` - Bookmark button
- ✅ `moon.svg` - Dark mode toggle
- ✅ `bell.svg` - Notifications button
- ✅ `message-square.svg` - Messages button
- ✅ `maximize.svg` - Fullscreen button
- ✅ `globe.svg` - Language/region selector
- ✅ `user.svg` - User profile button and account menu item
- ✅ `inbox.svg` - Inbox menu item in profile dropdown
- ✅ `settings.svg` - Settings menu item in profile dropdown
- ✅ `log-out.svg` - Logout menu item in profile dropdown

#### Auth Pages (`src/components/auth/*/`)
- ✅ `mail.svg` - Email input icon (all login pages)
- ✅ `lock.svg` - Password input icon (all login pages, forgot password, reset password)
- ✅ `eye.svg` - Show password toggle (all login pages, register, reset password)
- ✅ `eye-off.svg` - Hide password toggle (all login pages, register, reset password)
- ✅ `shield.svg` - Admin login security icon
- ✅ `alert-triangle.svg` - Admin login security warning
- ✅ `check-circle.svg` - Email verification success, password reset email sent
- ✅ `x.svg` - Invalid/expired token indicator (reset password)

#### Sidebar (`src/components/utils/Sidebar.jsx`)
- ✅ `layout.svg` - Sidebar close button
- ✅ `chevron-down.svg` - Submenu expand indicator (reused)
- ✅ `chevron-right.svg` - Submenu collapse indicator (reused)

#### Features Config (`src/components/data/dynamic.js`)
- ✅ `home.svg` - Dashboard icon in sidebar (replaced lucide-react HomeIcon)

---

## Notes

- This list is maintained to help identify unused assets for cleanup
- Total currently used: **28 unique files** (some used multiple times)
- All dashboard components now use feather SVG files instead of Lucide React icons
- SVG colors are adjusted using CSS filters to match the design
- **Before deleting unused files, ensure no dynamic imports or future features require them**

---

## Update History

- **2025-12-30**: Added auth page assets (mail.svg, lock.svg, eye.svg, eye-off.svg, shield.svg, alert-triangle.svg)
- **2025-12-29**: Added inbox.svg, settings.svg, and log-out.svg for profile dropdown menu in NavBar
- **2025-12-15**: Updated all asset paths from `/src/assets/` to `/assets/` for Vercel compatibility
- **2025-12-15**: Replaced lucide-react HomeIcon in dynamic.js with feather home.svg
- **2025-12-13**: Initial tracking - 4 assets in use (social login icons)

---

## Cleanup Checklist

When ready to clean up:
1. ✅ Verify all used assets are listed above
2. ⬜ Check for any dynamic/conditional imports
3. ⬜ Backup the feather directory before deletion
4. ⬜ Delete unused assets
5. ⬜ Test all pages to ensure no broken images
