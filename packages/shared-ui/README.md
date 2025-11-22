# @omnify/shared-ui

Shared UI components, hooks, and utilities for Omnify frontend applications.

## Installation

This package is used internally by `frontend-user` and `frontend-admin`. It should be installed as a local package dependency.

## Usage

### In frontend-user or frontend-admin:

```javascript
// Import components
import { Button, Card, Dialog } from '@omnify/shared-ui';

// Import hooks
import { useToast } from '@omnify/shared-ui';

// Import utilities
import { cn } from '@omnify/shared-ui';
```

## Structure

```
shared-ui/
├── components/     # Shared UI components (Radix UI based)
├── hooks/          # Shared React hooks
├── utils/          # Shared utility functions
└── index.js        # Main entry point
```

## Components

All Radix UI based components are available:
- Button, Card, Dialog, Input, Select, etc.
- Custom components: ErrorFallback, LoadingSpinner

## Hooks

- `useToast` - Toast notification hook

## Utils

- `cn` - Class name utility (clsx + tailwind-merge)

