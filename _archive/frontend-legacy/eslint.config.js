// ESLint configuration for OmniFy Frontend
// ESLint 9.x flat config format (CommonJS)

const js = require('@eslint/js');
const globals = require('globals');
const react = require('eslint-plugin-react');
const jsxA11y = require('eslint-plugin-jsx-a11y');
const importPlugin = require('eslint-plugin-import');

module.exports = [
  js.configs.recommended,
  {
    files: ['**/*.{js,jsx}'],
    languageOptions: {
      ecmaVersion: 2022,
      sourceType: 'module',
      globals: {
        ...globals.browser,
        ...globals.node,
        ...globals.es2021,
      },
      parserOptions: {
        ecmaVersion: 2022,
        ecmaFeatures: {
          jsx: true,
        },
      },
    },
    plugins: {
      react,
      'jsx-a11y': jsxA11y,
      import: importPlugin,
    },
    settings: {
      react: {
        version: 'detect',
      },
    },
    rules: {
      ...react.configs.recommended.rules,
      ...jsxA11y.configs.recommended.rules,
      'react/react-in-jsx-scope': 'off', // Not needed in React 17+
      'react/prop-types': 'warn',
      'no-unused-vars': ['warn', { argsIgnorePattern: '^_' }],
      'no-console': ['warn', { allow: ['warn', 'error'] }],
      'import/order': [
        'warn',
        {
          groups: ['builtin', 'external', 'internal', 'parent', 'sibling', 'index'],
          'newlines-between': 'always',
        },
      ],
    },
  },
  {
    ignores: [
      'node_modules/**',
      'build/**',
      'coverage/**',
      'cypress/**',
      'public/**',
      '*.config.js',
    ],
  },
];

