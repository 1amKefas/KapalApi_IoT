window.tailwind = window.tailwind || {}
window.tailwind.config = {
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        "on-tertiary": "#ffffff",
        "primary-container": "#00855d",
        "on-secondary-fixed": "#001d31",
        "outline-variant": "#bccac0",
        "on-error-container": "#93000a",
        "surface-tint": "#006c4a",
        "tertiary-fixed": "#ffdad7",
        "surface-container-lowest": "#ffffff",
        "on-primary-fixed": "#002114",
        "background": "#f7f9fb",
        "on-primary-container": "#f5fff7",
        "surface": "#f7f9fb",
        "surface-dim": "#d8dadc",
        "on-primary-fixed-variant": "#005137",
        "primary-fixed": "#85f8c4",
        "on-surface-variant": "#3d4a42",
        "on-secondary-container": "#00476e",
        "surface-variant": "#e0e3e5",
        "primary-fixed-dim": "#68dba9",
        "surface-container-highest": "#e0e3e5",
        "surface-bright": "#f7f9fb",
        "on-secondary": "#ffffff",
        "on-primary": "#ffffff",
        "outline": "#6d7a72",
        "surface-container-high": "#e6e8ea",
        "tertiary-container": "#ba5551",
        "secondary-fixed": "#cce5ff",
        "secondary": "#006398",
        "surface-container-low": "#f2f4f6",
        "tertiary": "#9b3e3b",
        "inverse-surface": "#2d3133",
        "on-background": "#191c1e",
        "inverse-on-surface": "#eff1f3",
        "on-secondary-fixed-variant": "#004b73",
        "error-container": "#ffdad6",
        "tertiary-fixed-dim": "#ffb3ae",
        "on-error": "#ffffff",
        "secondary-container": "#5bb8fe",
        "surface-container": "#eceef0",
        "on-tertiary-fixed-variant": "#7f2928",
        "primary": "#006948",
        "on-tertiary-fixed": "#410004",
        "secondary-fixed-dim": "#93ccff",
        "error": "#ba1a1a",
        "on-tertiary-container": "#fffbff",
        "inverse-primary": "#68dba9",
        "on-surface": "#191c1e"
      },
      borderRadius: {
        DEFAULT: "0.25rem",
        lg: "0.5rem",
        xl: "0.75rem",
        full: "9999px"
      },
      spacing: {
        "margin-mobile": "16px",
        "card-padding": "20px",
        "margin-desktop": "32px",
        "base": "8px",
        "gutter": "24px"
      },
      fontFamily: {
        "headline-md": ["Inter"],
        "data-mono": ["Inter"],
        "label-caps": ["Inter"],
        "display": ["Inter"],
        "headline-lg-mobile": ["Inter"],
        "headline-lg": ["Inter"],
        "body-lg": ["Inter"],
        "body-sm": ["Inter"]
      },
      fontSize: {
        "headline-md": ["18px", { lineHeight: "24px", fontWeight: "600" }],
        "data-mono": ["14px", { lineHeight: "20px", fontWeight: "500" }],
        "label-caps": ["12px", { lineHeight: "16px", letterSpacing: "0.05em", fontWeight: "600" }],
        "display": ["36px", { lineHeight: "44px", letterSpacing: "-0.02em", fontWeight: "700" }],
        "headline-lg-mobile": ["20px", { lineHeight: "28px", fontWeight: "600" }],
        "headline-lg": ["24px", { lineHeight: "32px", letterSpacing: "-0.01em", fontWeight: "600" }],
        "body-lg": ["16px", { lineHeight: "24px", fontWeight: "400" }],
        "body-sm": ["14px", { lineHeight: "20px", fontWeight: "400" }]
      }
    }
  }
}
