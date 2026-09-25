import { useEffect } from "react";

function ThemeManager() {
  useEffect(() => {
    const applyTheme = () => {
      const savedTheme =
        localStorage.getItem("resomind_theme") || "light";

      let activeTheme = savedTheme;

      if (savedTheme === "system") {
        activeTheme = window.matchMedia(
          "(prefers-color-scheme: dark)"
        ).matches
          ? "dark"
          : "light";
      }

      document.documentElement.setAttribute(
        "data-resomind-theme",
        activeTheme
      );
    };

    applyTheme();

    const media = window.matchMedia(
      "(prefers-color-scheme: dark)"
    );

    const handleSystemThemeChange = () => {
      const savedTheme =
        localStorage.getItem("resomind_theme");

      if (savedTheme === "system") {
        applyTheme();
      }
    };

    media.addEventListener(
      "change",
      handleSystemThemeChange
    );

    return () => {
      media.removeEventListener(
        "change",
        handleSystemThemeChange
      );
    };
  }, []);

  return null;
}

export default ThemeManager;