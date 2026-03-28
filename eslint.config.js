import globals from 'globals'

export default [
  {
    files: ['custom_components/flatastic/www/**/*.js'],
    languageOptions: {
      globals: globals.browser,
      ecmaVersion: 2022,
    },
    rules: {
      'no-unused-vars': 'error',
      'no-undef': 'error',
    },
  },
]
