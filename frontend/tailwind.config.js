const colors = require('tailwindcss/colors');
const plugin = require('tailwindcss/plugin')
const { transitionTimingFunction } = require('tailwindcss/defaultTheme');

const bodyFontFamily = [
  `system-ui`,
  `-apple-system`,
  `BlinkMacSystemFont`,
  `Segoe UI`,
  `Roboto`,
  `Ubuntu`,
  `Helvetica Neue`,
  `sans-serif`,
];

module.exports = {
  mode: 'jit',
  purge: ["./src/**/*.{js,jsx,ts,tsx}"],
  future: {
    removeDeprecatedGapUtilities: true,
    purgeLayersByDefault: true,
  },
  variants: {
    extend: {
      textColor: ["visited"],
    },
  },
  theme: {
    maxHeight: {
      0: "0",
      "1/4": "25%",
      "1/2": "50%",
      "2/3": "66%",
      "3/4": "75%",
      "7/8": "88%",
      full: "100%",
    },
    extend: {
      fontFamily: {
        sans: bodyFontFamily,
      },
      colors: {
        teal: colors.teal,
        emerald: colors.emerald,
        cyan: colors.cyan,
        lime: colors.lime,
        orange: colors.orange,
        stone: colors.warmGray,
        slate: colors.trueGray,
      },
      height: {
        '18': '4.5rem',
      },
      screens: {
        'lg': '800px',
      },
      transitionProperty: {
        'height': 'height',
        'width': 'width',
      },
      keyframes: {
        'fade-in-up': {
          '0%': {
            opacity: '0',
            transform: 'translateY(10px)'
          },
          '100%': {
            opacity: '1',
            transform: 'translateY(0)'
          },
        },
        'fade-out-down': {
          '0%': {
            opacity: '1',
            transform: 'translateY(0)'
          },
          '100%': {
            opacity: '0',
            transform: 'translateY(-10px)',
            display: 'none',
          },
        },
        'fade-in': {
          '0%': {
            opacity: '0',
          },
          '100%': {
            opacity: '1',
          }
        },
        'fade-out': {
          '0%': {
            opacity: '1',
          },
          '100%': {
            opacity: '0',
          }
        },
      },
      animation: {
        'fade-in-up': 'fade-in-up 0.2s ease-out',
        'fade-out-down': 'fade-out-down 0.2s ease-out forwards',
        'fade-in': 'fade-in 0.2s ease-out',
        'fade-out': 'fade-out 0.2s ease-out forwards'
      }
    },
  },
  plugins: [
    require("@tailwindcss/forms"),
    // require('tailwindcss-writing-mode')({
      // variants: ['responsive', 'hover']
    // }),
    plugin(function({ addUtilities }) {
      const newUtilities = {
        '.writing-mode-vertical': {
          writingMode: 'vertical-lr'
        },
      }
      addUtilities(newUtilities, {
        variants: ['responsive', 'hover'],
      })
    })
  ],
};
