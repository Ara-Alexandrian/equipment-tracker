# GearVue Theme System Documentation

<div align="center">
  <img src="../Resources/gearvue-text.png" alt="GearVue Logo" width="400">
  <br>
  <i>Customizable visual experience for users</i>
  <br><br>
</div>

## Overview

GearVue supports multiple themes that can be cycled through using the theme button in the top navigation bar. The system uses:

1. Individual CSS files for each theme
2. A unified JavaScript theme switcher
3. Local storage for theme persistence
4. Theme-specific icons

## Current Themes

- **Light** - Default light theme with blue accents
- **Dark** - Dark mode with blue accents and reduced eye strain
- **Dracula** - Classic Dracula theme with purple/pink accents
- **Sweet Dracula** - A softer version of Dracula with enhanced UI elements
- **Pastel** - A light theme with soft pastel colors

## Theme Features

### Theme Persistence

Themes are saved in the browser's localStorage and persist across page loads and sessions. Users can set their preferred theme once, and it will be automatically applied on subsequent visits.

### Custom Theme Icons

Each theme has a unique icon in the navigation bar:
- Light mode uses a sun icon (☀️)
- Dark mode uses a moon icon (🌙)
- Dracula mode uses a custom vampire icon (🧛)
- Sweet Dracula mode uses a stylized vampire icon
- Pastel mode uses a flower icon (🌸)

### System Preference Detection

The theme system can detect the user's system preference for light or dark mode and automatically apply the appropriate theme on their first visit.

## How Themes Work

1. Each theme has its own CSS file (`app/static/css/{theme-name}-mode.css`)
2. The theme switcher JavaScript (`app/static/js/theme-unified.js`) handles toggling between themes
3. The active theme is saved to localStorage to persist between page loads
4. When a page loads, the theme is immediately applied before content rendering to prevent flickering

## Adding a New Theme

1. **Create a CSS file** for your theme in `app/static/css/{theme-name}-mode.css`
2. **Design your theme** using the existing themes as a template, ensuring all UI elements are styled
3. **Update base.html** to include your CSS file
4. **Modify theme-unified.js** to include your theme in the cycle and apply the proper classes
5. **Create a theme icon** to display in the theme button

### Step 1: Create CSS File

Create a new file at `app/static/css/{theme-name}-mode.css`. Use an existing theme as a template.

### Step 2: Update base.html

Add your CSS file to the list of theme CSS files in `app/templates/base.html`:

```html
<link rel="stylesheet" href="{{ url_for('static', filename='css/{theme-name}-mode.css') }}?v={{ now.timestamp()|int }}">
```

### Step 3: Update theme-unified.js

1. Add your theme to the valid themes list:

```javascript
if (!theme || !['light', 'dark', 'dracula', 'sweet-dracula', 'pastel', '{theme-name}'].includes(theme)) {
```

2. Add a case for applying your theme:

```javascript
else if (theme === '{theme-name}') {
    document.documentElement.classList.add('{theme-name}-mode');
    document.body.classList.add('{theme-name}-mode');
}
```

3. Update the theme cleanup function to include your theme:

```javascript
document.documentElement.classList.remove('dark-mode', 'dracula-mode', 'sweet-dracula-mode', 'pastel-mode', '{theme-name}-mode');
document.body.classList.remove('dark-mode', 'dracula-mode', 'sweet-dracula-mode', 'pastel-mode', '{theme-name}-mode');
```

4. Update the theme cycling function to include your theme:

```javascript
else if (currentTheme === 'sweet-dracula') {
    newTheme = 'pastel';
} else if (currentTheme === 'pastel') {
    newTheme = '{theme-name}';
} else {
    newTheme = 'light';
}
```

### Step 4: Add Theme Icon

1. Create an icon for your theme (SVG recommended)
2. Place it in `app/static/img/icons/{theme-name}-icon.svg`
3. Update the `updateThemeButtonIcon` function in `theme-unified.js`:

```javascript
else if (theme === '{theme-name}') {
    themeBtn.innerHTML = '<i id="theme-icon" class="bi bi-your-icon"></i>';
    // Or for custom SVG:
    // themeBtn.innerHTML = '<img id="theme-icon" src="/static/img/icons/{theme-name}-icon.svg" style="width:38px;height:38px;margin-top:-10px;margin-bottom:-10px;margin-left:-8px;margin-right:-8px;" />';
}
```

### Step 5: Update Immediate Application Script

Update the immediate theme application script in `base.html`:

```javascript
else if (theme === '{theme-name}') {
    document.documentElement.classList.add('{theme-name}-mode');
}
```

## Customizing Existing Themes

### CSS Structure Guidelines

Each theme CSS file should follow this structure:

1. **Base styling** - Root variables and HTML/body styles
2. **Navbar adjustments** - Styles for the main navigation
3. **Card styling** - Styles for cards and containers
4. **Form controls** - Styles for inputs, selects, etc.
5. **Table styling** - Styles for tables and data display
6. **Button styling** - Styles for various button types
7. **Special components** - Theme-specific styles for components

### Important Selectors

Use these selectors to ensure your theme is applied correctly:

- `body.{theme-name}-mode` - Apply to all elements within the theme
- `.{theme-name}-mode elementName` - Apply to specific elements

### Tips for Theme Development

1. Use `!important` flags when necessary to override Bootstrap styles
2. Test all UI components in your theme (tables, forms, buttons, cards, etc.)
3. Maintain good contrast for accessibility
4. Consider responsive behavior
5. Use CSS variables for color consistency

## Current Theme Implementation

The theme system is implemented with these key files:

### CSS Files

- `app/static/css/style.css` - Base styles for all themes
- `app/static/css/dark-mode.css` - Dark theme styles
- `app/static/css/dracula-mode.css` - Dracula theme styles
- `app/static/css/sweet-dracula-mode.css` - Sweet Dracula theme styles
- `app/static/css/pastel-mode.css` - Pastel theme styles

### JavaScript

- `app/static/js/theme-unified.js` - Main theme switching code
- `app/static/js/theme-switcher.js` - Legacy theme switching (for backward compatibility)

### HTML Integration

The `app/templates/base.html` file includes:

1. Theme CSS links in the head
2. Theme toggle button in the navbar
3. Immediate theme application script at the end of the body section

## Troubleshooting

- **Cache Issues**: Add version parameters to CSS links
- **Specificity Problems**: Use more specific selectors or `!important` flags
- **DOM Updates**: Ensure JavaScript applies theme after DOM changes
- **Console Debugging**: Check browser console for theme application logs

## Advanced Customizations

For more advanced UI enhancements, consider:

- Adding subtle animations and transitions
- Using gradients and shadows for depth
- Implementing custom scrollbars
- Adding hover effects to interactive elements

## Theme Preview System

To preview themes before applying:
1. Hold Shift + Click on the theme button
2. Preview mode activates for 5 seconds
3. Click to apply or wait for timeout to revert

## Accessibility Considerations

When designing themes, keep these accessibility guidelines in mind:

1. **Color Contrast**: Maintain WCAG 2.1 AA contrast ratios (4.5:1 for normal text, 3:1 for large text)
2. **Focus Indicators**: Ensure keyboard focus indicators are visible in all themes
3. **Text Legibility**: Maintain readable font sizes and weights
4. **Form Controls**: Ensure form controls are easily identifiable
5. **Error States**: Make sure error states are clearly visible in all themes