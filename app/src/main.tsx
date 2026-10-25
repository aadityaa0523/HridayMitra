import '@fontsource/noto-sans-oriya/oriya-400.css';
import '@fontsource/noto-sans-malayalam/malayalam-400.css';
import '@fontsource/noto-sans-gujarati/gujarati-400.css';
import '@fontsource/noto-sans-bengali/bengali-400.css';
import '@fontsource/noto-sans-kannada/kannada-400.css';
import '@fontsource/noto-sans-telugu/telugu-400.css';
import '@fontsource/noto-sans-tamil/tamil-400.css';
import '@fontsource/noto-sans/latin-400.css';
import '@fontsource/noto-sans/latin-600.css';
import '@fontsource/noto-sans/latin-700.css';
import '@fontsource/noto-sans-devanagari/devanagari-400.css';
import '@fontsource/noto-sans-devanagari/devanagari-600.css';
import '@fontsource/noto-sans-devanagari/devanagari-700.css';
import React from 'react';
import ReactDOM from 'react-dom/client';
import './i18n';
import './styles.css';
import { App } from './App';
try{document.documentElement.dataset.large=localStorage.getItem('saathi.large')==='true'?'true':'false';}catch{/* Use standard text size. */}
ReactDOM.createRoot(document.getElementById('root')!).render(<React.StrictMode><App /></React.StrictMode>);

