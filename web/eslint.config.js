import js from "@eslint/js";
import react from "eslint-plugin-react";
import reactHooks from "eslint-plugin-react-hooks";
import reactRefresh from "eslint-plugin-react-refresh";
import globals from "globals";

const reactLanguageOptions = {
  ...react.configs.flat.recommended.languageOptions,
  ...react.configs.flat["jsx-runtime"].languageOptions,
  globals: globals.browser,
};

export default [
  { ignores: ["dist", "node_modules", ".next"] },
  js.configs.recommended,
  {
    files: ["**/*.{js,jsx}"],
    plugins: {
      react,
      "react-hooks": reactHooks,
      "react-refresh": reactRefresh,
    },
    languageOptions: reactLanguageOptions,
    rules: {
      ...react.configs.flat.recommended.rules,
      ...react.configs.flat["jsx-runtime"].rules,
      "react/prop-types": "off",
      ...reactHooks.configs.recommended.rules,
      "react-refresh/only-export-components": ["warn", { allowConstantExport: true }],
    },
    settings: { react: { version: "detect" } },
  },
];
