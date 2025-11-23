const path = require('path');

const config = {
  disableHotReload: process.env.DISABLE_HOT_RELOAD === 'true',
};

module.exports = {
  webpack: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
      '@omnify/shared-ui': path.resolve(__dirname, '../packages/shared-ui'),
      '@omnify/shared-ui/utils': path.resolve(__dirname, '../packages/shared-ui/utils'),
      '@omnify/shared-ui/hooks': path.resolve(__dirname, '../packages/shared-ui/hooks'),
    },
    configure: (webpackConfig) => {
      const sharedUiPath = path.resolve(__dirname, '../packages/shared-ui');
      const projectRoot = path.resolve(__dirname, '../');
      
      // CRITICAL: Configure resolve
      if (!webpackConfig.resolve) {
        webpackConfig.resolve = {};
      }
      
      // Add shared-ui to resolve modules
      webpackConfig.resolve.modules = [
        ...(webpackConfig.resolve.modules || ['node_modules']),
        sharedUiPath,
        projectRoot
      ];
      
      // CRITICAL: Add extensions with .js first
      webpackConfig.resolve.extensions = [
        '.js',
        '.jsx',
        '.json',
        ...(webpackConfig.resolve.extensions || []).filter(ext => !['.js', '.jsx', '.json'].includes(ext))
      ];
      
      webpackConfig.resolve.symlinks = true;
      webpackConfig.resolve.fullySpecified = false;
      
      // CRITICAL: Configure babel-loader to process shared-ui files
      const oneOfRule = webpackConfig.module.rules.find((rule) => rule.oneOf);
      if (oneOfRule) {
        oneOfRule.oneOf.forEach((rule) => {
          if (rule.test && (
            rule.test.toString().includes('jsx') || 
            rule.test.toString().includes('\\.js$') ||
            rule.test.toString().includes('\\.jsx$')
          )) {
            // ALWAYS include shared-ui
            if (!rule.include) {
              rule.include = [sharedUiPath];
            } else if (Array.isArray(rule.include)) {
              if (!rule.include.some(inc => typeof inc === 'string' && inc.includes(sharedUiPath))) {
                rule.include.push(sharedUiPath);
              }
            } else {
              rule.include = [rule.include, sharedUiPath];
            }
            
            // NEVER exclude shared-ui
            if (rule.exclude) {
              const originalExclude = Array.isArray(rule.exclude) ? rule.exclude : [rule.exclude];
              rule.exclude = originalExclude.map((exclude) => {
                if (exclude && exclude.toString && exclude.toString().includes('node_modules')) {
                  return (modulePath) => {
                    const pathStr = typeof modulePath === 'string' ? modulePath : (modulePath?.request || modulePath?.resource || '');
                    if (pathStr && pathStr.includes(sharedUiPath)) {
                      return false;
                    }
                    return /node_modules/.test(pathStr) && !pathStr.includes(sharedUiPath);
                  };
                }
                return exclude;
              });
            } else {
              rule.exclude = (modulePath) => {
                const pathStr = typeof modulePath === 'string' ? modulePath : (modulePath?.request || modulePath?.resource || '');
                if (pathStr && pathStr.includes(sharedUiPath)) {
                  return false;
                }
                return /node_modules/.test(pathStr) && !pathStr.includes(sharedUiPath);
              };
            }
          }
        });
      }
      
      // Remove ModuleScopePlugin
      if (webpackConfig.resolve && webpackConfig.resolve.plugins) {
        webpackConfig.resolve.plugins = webpackConfig.resolve.plugins.filter(
          plugin => plugin.constructor.name !== 'ModuleScopePlugin'
        );
      }
      webpackConfig.plugins = webpackConfig.plugins.filter(
        plugin => plugin.constructor.name !== 'ModuleScopePlugin'
      );
      
      if (config.disableHotReload) {
        webpackConfig.plugins = webpackConfig.plugins.filter(plugin => {
          return !(plugin.constructor.name === 'HotModuleReplacementPlugin');
        });
        webpackConfig.watch = false;
        webpackConfig.watchOptions = {
          ignored: /.*/,
        };
      } else {
        webpackConfig.watchOptions = {
          ...webpackConfig.watchOptions,
          ignored: [
            '**/node_modules/**',
            '**/.git/**',
            '**/build/**',
            '**/dist/**',
            '**/coverage/**',
            '**/public/**',
          ],
        };
      }
      
      return webpackConfig;
    },
  },
  devServer: {
    host: '0.0.0.0',
    port: 4001,
    allowedHosts: 'all',
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
};
