import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import tailwind from '@tailwindcss/vite';
import { VitePWA } from 'vite-plugin-pwa';
export default defineConfig({
 build:{rollupOptions:{output:{manualChunks:(id)=>id.includes('commonjsHelpers')?'shared':id.includes('vosk-browser')?'vosk':undefined}}},
 plugins: [react(), tailwind(), VitePWA({
  registerType: 'prompt',
  includeAssets: ['icon.svg', 'icon-192.png', 'icon-512.png'],
  manifest: {name:'HridayMitra Saathi',short_name:'Saathi',description:'Your daily care companion',lang:'en',start_url:'/',scope:'/',display:'standalone',background_color:'#F5F7F4',theme_color:'#0D6B6E',icons:[{src:'/icon-192.png',sizes:'192x192',type:'image/png',purpose:'any'},{src:'/icon-512.png',sizes:'512x512',type:'image/png',purpose:'any maskable'}]},
  workbox:{globPatterns:['**/*.{js,css,html,svg,png,woff2,mp3,json}'],globIgnores:['**/vosk-*.js','models/**'],runtimeCaching:[{urlPattern:/\/models\/(en|hi)\.bin$/,handler:'CacheOnly',options:{cacheName:'saathi-voice-packs-v1'}},{urlPattern:/\/assets\/vosk-.*\.js$/,handler:'CacheFirst',options:{cacheName:'saathi-vosk-runtime-v1',expiration:{maxEntries:2}}}],navigateFallback:'index.html',cleanupOutdatedCaches:true,clientsClaim:true}
 })]
});

