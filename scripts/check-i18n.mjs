import { readFileSync } from 'node:fs'
const root = new URL('../frontend/src/', import.meta.url)
const en = JSON.parse(readFileSync(new URL('en.json', root), 'utf8'))
const vi = JSON.parse(readFileSync(new URL('vi.json', root), 'utf8'))
const differences = [...Object.keys(en).filter(k => !(k in vi)), ...Object.keys(vi).filter(k => !(k in en))]
if (differences.length || Object.values(vi).some(v => typeof v !== 'string' || !v.trim())) throw new Error(`Invalid translations: ${differences}`)
console.log(`Translation coverage: ${Object.keys(en).length} keys, EN/VI parity passed.`)
