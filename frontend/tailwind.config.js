module.exports = {
  // ... other config
  theme: {
    extend: {
      keyframes: {
        'fade-out': {
          '0%': { opacity: '1' },
          '75%': { opacity: '1' },
          '100%': { opacity: '0' },
        }
      },
      animation: {
        'fade-out': 'fade-out 2s ease-out'
      }
    }
  }
} 