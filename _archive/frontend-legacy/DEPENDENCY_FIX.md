# 🔧 Dependency Issue Fix - ajv Module Not Found

**Date**: November 22, 2025  
**Issue**: `Error: Cannot find module 'ajv/dist/compile/codegen'`  
**Status**: ✅ **RESOLVED**

---

## 🐛 Problem

When running `npm start`, the following error occurred:

```
Error: Cannot find module 'ajv/dist/compile/codegen'
Require stack:
- C:\share\repos\ai\omnifyproduct\frontend\node_modules\ajv-keywords\dist\definitions\typeof.js
```

**Root Cause:**
- Version conflict between `ajv` packages
- `ajv-keywords@5.1.0` requires `ajv@^8.8.2`
- But `ajv@6.12.6` was being used by some dependencies
- Missing or corrupted `node_modules` directory

---

## ✅ Solution

### Step 1: Clean Install
```bash
# Clear npm cache
npm cache clean --force

# Remove node_modules and package-lock.json
Remove-Item -Recurse -Force node_modules
Remove-Item -Force package-lock.json

# Reinstall with legacy peer deps (to handle React 19 conflicts)
npm install --legacy-peer-deps
```

### Step 2: Fix ajv Version Conflict
```bash
# Install correct ajv and ajv-keywords versions
npm install ajv@^8.17.1 ajv-keywords@^5.1.0 --legacy-peer-deps --save-dev
```

### Step 3: Verify
```bash
# Start development server
npm start

# Server should start successfully at http://localhost:3000
```

---

## 📋 Why `--legacy-peer-deps`?

The `--legacy-peer-deps` flag is needed because:

1. **React 19 Compatibility**
   - Project uses React 19.0.0
   - Some packages (like `react-day-picker@8.10.1`) require React 16-18
   - `--legacy-peer-deps` allows installation despite peer dependency conflicts

2. **Node.js Version**
   - Some packages require Node.js 20+
   - Current: Node.js 18.20.8
   - `--legacy-peer-deps` allows installation despite engine warnings

---

## ⚠️ Important Notes

### Using `--legacy-peer-deps` Going Forward

For all npm commands, use `--legacy-peer-deps`:

```bash
# Install new packages
npm install <package> --legacy-peer-deps

# Update packages
npm update --legacy-peer-deps

# Install all dependencies
npm install --legacy-peer-deps
```

### Alternative: Configure npm

Add to `.npmrc` file in frontend directory:
```
legacy-peer-deps=true
```

This makes `--legacy-peer-deps` the default for all npm commands.

---

## ✅ Verification

After applying the fix:

1. **Server Starts Successfully**
   ```bash
   npm start
   # Should start without errors
   ```

2. **Server Responds**
   ```bash
   curl http://localhost:3000
   # Should return HTML (200 OK)
   ```

3. **No Module Errors**
   - No "Cannot find module" errors
   - No ajv-related errors
   - Development server runs normally

---

## 🔍 Dependencies Status

### ajv Versions (After Fix)
- `ajv@8.17.1` - Installed as devDependency
- `ajv-keywords@5.1.0` - Installed as devDependency
- `ajv@6.12.6` - Still present for some dependencies (OK, not conflicting)

### React Versions
- `react@19.0.0` - Main React version
- `react-dom@19.0.0` - React DOM version
- Some packages still expect React 16-18 (handled by `--legacy-peer-deps`)

---

## 📝 Package.json Changes

Added to `devDependencies`:
```json
{
  "devDependencies": {
    "ajv": "^8.17.1",
    "ajv-keywords": "^5.1.0"
  }
}
```

---

## 🚀 Current Status

✅ **RESOLVED** - Frontend server starts successfully

**Verification:**
- ✅ `npm start` runs without errors
- ✅ Server responds at http://localhost:3000
- ✅ No module not found errors
- ✅ Development server functional

---

## 🔄 Future Updates

### Recommended Actions

1. **Create `.npmrc` file** (recommended):
   ```bash
   echo "legacy-peer-deps=true" > .npmrc
   ```

2. **Update React-dependent packages** (when available):
   - Wait for `react-day-picker` to support React 19
   - Or downgrade React to 18.x if needed

3. **Update Node.js** (optional):
   - Consider upgrading to Node.js 20+ for better compatibility
   - Some packages require Node 20+

---

## 🆘 If Issue Persists

### Option 1: Use Yarn
```bash
# Install yarn
npm install -g yarn

# Install dependencies
yarn install

# Start server
yarn start
```

### Option 2: Use npm with overrides
Add to `package.json`:
```json
{
  "overrides": {
    "ajv": "^8.17.1"
  }
}
```

### Option 3: Downgrade React
```bash
npm install react@^18.0.0 react-dom@^18.0.0 --legacy-peer-deps
```

---

**Status**: ✅ **FIXED AND WORKING**  
**Last Updated**: November 22, 2025



