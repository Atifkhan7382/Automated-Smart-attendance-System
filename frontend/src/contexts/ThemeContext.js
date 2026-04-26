import React, { createContext, useContext, useEffect, useMemo, useState } from 'react';

const ThemeContext = createContext(null);
const THEME_STORAGE_KEY = 'theme-mode';

const getSystemPrefersDark = () => {
  if (typeof window === 'undefined' || !window.matchMedia) {
    return false;
  }
  return window.matchMedia('(prefers-color-scheme: dark)').matches;
};

export const ThemeProvider = ({ children }) => {
  const [mode, setMode] = useState('system');
  const [resolvedTheme, setResolvedTheme] = useState(getSystemPrefersDark() ? 'dark' : 'light');

  useEffect(() => {
    const savedMode = localStorage.getItem(THEME_STORAGE_KEY);
    if (savedMode === 'light' || savedMode === 'dark' || savedMode === 'system') {
      setMode(savedMode);
    }
  }, []);

  useEffect(() => {
    const updateTheme = () => {
      const systemDark = getSystemPrefersDark();
      const nextTheme = mode === 'system' ? (systemDark ? 'dark' : 'light') : mode;
      setResolvedTheme(nextTheme);
      document.documentElement.classList.toggle('dark', nextTheme === 'dark');
    };

    updateTheme();

    if (mode === 'system' && window.matchMedia) {
      const media = window.matchMedia('(prefers-color-scheme: dark)');
      const handleChange = () => updateTheme();
      media.addEventListener('change', handleChange);
      return () => media.removeEventListener('change', handleChange);
    }

    return undefined;
  }, [mode]);

  const toggleTheme = () => {
    const systemDark = getSystemPrefersDark();
    const nextMode = mode === 'system'
      ? (systemDark ? 'light' : 'dark')
      : (mode === 'dark' ? 'light' : 'dark');

    setMode(nextMode);
    localStorage.setItem(THEME_STORAGE_KEY, nextMode);
  };

  const value = useMemo(
    () => ({
      mode,
      resolvedTheme,
      setMode: (nextMode) => {
        const safeMode = nextMode === 'light' || nextMode === 'dark' || nextMode === 'system'
          ? nextMode
          : 'system';
        setMode(safeMode);
        localStorage.setItem(THEME_STORAGE_KEY, safeMode);
      },
      toggleTheme,
    }),
    [mode, resolvedTheme]
  );

  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
};

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within ThemeProvider');
  }
  return context;
};
