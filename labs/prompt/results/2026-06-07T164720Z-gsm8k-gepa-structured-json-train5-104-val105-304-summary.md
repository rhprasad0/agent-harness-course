# DSPy/GEPA GSM8K Structured Reliability Smoke Test

- Date: 2026-06-07T164720Z
- DSPy version: `3.2.1`
- Model: `llama3:latest` via Ollama `http://127.0.0.1:11434`
- Adapter: `json`
- Reflection model: `gpt-5.4` via `openai-compatible` at `http://kube1.lan:4001/v1`
- Train rows: `[5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104]`
- Validation rows: `[105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259, 260, 261, 262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 280, 281, 282, 283, 284, 285, 286, 287, 288, 289, 290, 291, 292, 293, 294, 295, 296, 297, 298, 299, 300, 301, 302, 303, 304]`
- Solver max tokens: 1536
- Reflection max tokens: 1536
- GEPA budget: max_metric_calls=600
- Structured baseline validation score: 138/200 (69.0%)
- Structured baseline failure counts: `{'correct': 138, 'math': 62}`
- GEPA-compiled validation score: 138/200 (69.0%)
- GEPA-compiled failure counts: `{'correct': 138, 'math': 62}`

## Interpretation

This is a reliability-first setup smoke. The solver uses an explicit DSPy signature with `reasoning: str` and `answer: int`, so the metric can separate adapter/format failures from math failures.

Do not treat this as a frontier GEPA benchmark. It is a local-model harness check designed to make later optimization evidence cleaner.

## Validation rows

| Row | Baseline | Baseline failure | GEPA compiled | GEPA failure | Gold |
|---:|---:|---|---:|---|---:|
| 105 | 500 (✅) | correct | 500 (✅) | correct | 500 |
| 106 | 20 (✅) | correct | 20 (✅) | correct | 20 |
| 107 | 180 (❌) | math | 180 (❌) | math | 72 |
| 108 | 4 (❌) | math | 4 (❌) | math | 3 |
| 109 | 45 (❌) | math | 45 (❌) | math | 50 |
| 110 | 28 (✅) | correct | 28 (✅) | correct | 28 |
| 111 | 45 (✅) | correct | 45 (✅) | correct | 45 |
| 112 | 16 (✅) | correct | 16 (✅) | correct | 16 |
| 113 | 24 (✅) | correct | 24 (✅) | correct | 24 |
| 114 | 25 (✅) | correct | 25 (✅) | correct | 25 |
| 115 | 6 (✅) | correct | 6 (✅) | correct | 6 |
| 116 | 45 (❌) | math | 45 (❌) | math | 90 |
| 117 | 42 (✅) | correct | 42 (✅) | correct | 42 |
| 118 | 360 (✅) | correct | 360 (✅) | correct | 360 |
| 119 | 4 (✅) | correct | 4 (✅) | correct | 4 |
| 120 | 95200 (✅) | correct | 95200 (✅) | correct | 95200 |
| 121 | 240 (✅) | correct | 240 (✅) | correct | 240 |
| 122 | 27 (✅) | correct | 27 (✅) | correct | 27 |
| 123 | 34 (❌) | math | 34 (❌) | math | 48 |
| 124 | 50 (✅) | correct | 50 (✅) | correct | 50 |
| 125 | 50 (❌) | math | 50 (❌) | math | 10 |
| 126 | 7 (❌) | math | 7 (❌) | math | 10 |
| 127 | 82 (✅) | correct | 82 (✅) | correct | 82 |
| 128 | 120 (✅) | correct | 120 (✅) | correct | 120 |
| 129 | 880 (✅) | correct | 880 (✅) | correct | 880 |
| 130 | 411 (❌) | math | 411 (❌) | math | 10000 |
| 131 | 30 (✅) | correct | 30 (✅) | correct | 30 |
| 132 | 940 (✅) | correct | 940 (✅) | correct | 940 |
| 133 | 60 (✅) | correct | 60 (✅) | correct | 60 |
| 134 | 13 (✅) | correct | 13 (✅) | correct | 13 |
| 135 | 720 (✅) | correct | 720 (✅) | correct | 720 |
| 136 | 40 (✅) | correct | 40 (✅) | correct | 40 |
| 137 | 6 (✅) | correct | 6 (✅) | correct | 6 |
| 138 | 29 (✅) | correct | 29 (✅) | correct | 29 |
| 139 | 105 (✅) | correct | 105 (✅) | correct | 105 |
| 140 | 70 (✅) | correct | 70 (✅) | correct | 70 |
| 141 | 20 (✅) | correct | 20 (✅) | correct | 20 |
| 142 | 400 (✅) | correct | 400 (✅) | correct | 400 |
| 143 | 140 (✅) | correct | 140 (✅) | correct | 140 |
| 144 | 16 (✅) | correct | 16 (✅) | correct | 16 |
| 145 | 20 (✅) | correct | 20 (✅) | correct | 20 |
| 146 | 4000 (✅) | correct | 4000 (✅) | correct | 4000 |
| 147 | 2125 (✅) | correct | 2125 (✅) | correct | 2125 |
| 148 | 45 (❌) | math | 45 (❌) | math | 75 |
| 149 | 30 (✅) | correct | 30 (✅) | correct | 30 |
| 150 | 16 (✅) | correct | 16 (✅) | correct | 16 |
| 151 | 700 (❌) | math | 700 (❌) | math | 4 |
| 152 | 28 (❌) | math | 28 (❌) | math | 5 |
| 153 | 4 (✅) | correct | 4 (✅) | correct | 4 |
| 154 | 39 (❌) | math | 39 (❌) | math | 48 |
| 155 | 272 (✅) | correct | 272 (✅) | correct | 272 |
| 156 | 280 (✅) | correct | 280 (✅) | correct | 280 |
| 157 | 1200 (❌) | math | 1200 (❌) | math | 1400 |
| 158 | 2440 (❌) | math | 2440 (❌) | math | 80 |
| 159 | 30 (❌) | math | 30 (❌) | math | 34 |
| 160 | 15 (✅) | correct | 15 (✅) | correct | 15 |
| 161 | 16 (✅) | correct | 16 (✅) | correct | 16 |
| 162 | 32 (✅) | correct | 32 (✅) | correct | 32 |
| 163 | 28 (❌) | math | 28 (❌) | math | 92 |
| 164 | 50 (✅) | correct | 50 (✅) | correct | 50 |
| 165 | 15 (✅) | correct | 15 (✅) | correct | 15 |
| 166 | 77 (✅) | correct | 77 (✅) | correct | 77 |
| 167 | 5 (✅) | correct | 5 (✅) | correct | 5 |
| 168 | 16 (✅) | correct | 16 (✅) | correct | 16 |
| 169 | 18 (✅) | correct | 18 (✅) | correct | 18 |
| 170 | 120 (✅) | correct | 120 (✅) | correct | 120 |
| 171 | 150 (✅) | correct | 150 (✅) | correct | 150 |
| 172 | 1210 (✅) | correct | 1210 (✅) | correct | 1210 |
| 173 | 43 (❌) | math | 43 (❌) | math | 51 |
| 174 | 18000 (✅) | correct | 18000 (✅) | correct | 18000 |
| 175 | 95 (✅) | correct | 95 (✅) | correct | 95 |
| 176 | 750 (❌) | math | 750 (❌) | math | 15 |
| 177 | 100 (✅) | correct | 100 (✅) | correct | 100 |
| 178 | 1560 (❌) | math | 1560 (❌) | math | 350 |
| 179 | 122 (✅) | correct | 122 (✅) | correct | 122 |
| 180 | 130 (✅) | correct | 130 (✅) | correct | 130 |
| 181 | 20 (✅) | correct | 20 (✅) | correct | 20 |
| 182 | 160 (✅) | correct | 160 (✅) | correct | 160 |
| 183 | 18 (❌) | math | 18 (❌) | math | 23 |
| 184 | 2 (✅) | correct | 2 (✅) | correct | 2 |
| 185 | 17 (❌) | math | 17 (❌) | math | 25 |
| 186 | 30 (✅) | correct | 30 (✅) | correct | 30 |
| 187 | 8 (❌) | math | 8 (❌) | math | 5 |
| 188 | 106 (✅) | correct | 106 (✅) | correct | 106 |
| 189 | 50 (✅) | correct | 50 (✅) | correct | 50 |
| 190 | 34 (✅) | correct | 34 (✅) | correct | 34 |
| 191 | 360 (✅) | correct | 360 (✅) | correct | 360 |
| 192 | 100 (❌) | math | 100 (❌) | math | 5 |
| 193 | 91 (✅) | correct | 91 (✅) | correct | 91 |
| 194 | 24 (✅) | correct | 24 (✅) | correct | 24 |
| 195 | 10 (✅) | correct | 10 (✅) | correct | 10 |
| 196 | 12 (✅) | correct | 12 (✅) | correct | 12 |
| 197 | 120 (✅) | correct | 120 (✅) | correct | 120 |
| 198 | 6237 (❌) | math | 6237 (❌) | math | 6277 |
| 199 | 280 (❌) | math | 280 (❌) | math | 320 |
| 200 | 15000 (❌) | math | 15000 (❌) | math | 7500 |
| 201 | 55 (✅) | correct | 55 (✅) | correct | 55 |
| 202 | 106400 (❌) | math | 106400 (❌) | math | 114200 |
| 203 | 500 (❌) | math | 500 (❌) | math | 100 |
| 204 | 31 (✅) | correct | 31 (✅) | correct | 31 |
| 205 | 98 (✅) | correct | 98 (✅) | correct | 98 |
| 206 | 191 (❌) | math | 191 (❌) | math | 98 |
| 207 | 860 (✅) | correct | 860 (✅) | correct | 860 |
| 208 | 2000 (❌) | math | 2000 (❌) | math | 2600 |
| 209 | 76 (✅) | correct | 76 (✅) | correct | 76 |
| 210 | 5 (❌) | math | 5 (❌) | math | 145 |
| 211 | 2 (❌) | math | 2 (❌) | math | 10 |
| 212 | 4 (✅) | correct | 4 (✅) | correct | 4 |
| 213 | 533 (❌) | math | 533 (❌) | math | 5 |
| 214 | 250 (✅) | correct | 250 (✅) | correct | 250 |
| 215 | 8 (✅) | correct | 8 (✅) | correct | 8 |
| 216 | 44 (✅) | correct | 44 (✅) | correct | 44 |
| 217 | 220 (✅) | correct | 220 (✅) | correct | 220 |
| 218 | 15 (✅) | correct | 15 (✅) | correct | 15 |
| 219 | 50 (❌) | math | 50 (❌) | math | 45 |
| 220 | 54 (✅) | correct | 54 (✅) | correct | 54 |
| 221 | 70 (✅) | correct | 70 (✅) | correct | 70 |
| 222 | 90 (✅) | correct | 90 (✅) | correct | 90 |
| 223 | 140 (✅) | correct | 140 (✅) | correct | 140 |
| 224 | 20000 (✅) | correct | 20000 (✅) | correct | 20000 |
| 225 | 180 (✅) | correct | 180 (✅) | correct | 180 |
| 226 | 9 (✅) | correct | 9 (✅) | correct | 9 |
| 227 | 39 (❌) | math | 39 (❌) | math | 33 |
| 228 | 9 (✅) | correct | 9 (✅) | correct | 9 |
| 229 | 1 (✅) | correct | 1 (✅) | correct | 1 |
| 230 | 21 (✅) | correct | 21 (✅) | correct | 21 |
| 231 | 276000 (✅) | correct | 276000 (✅) | correct | 276000 |
| 232 | 50 (✅) | correct | 50 (✅) | correct | 50 |
| 233 | 75 (✅) | correct | 75 (✅) | correct | 75 |
| 234 | 12 (✅) | correct | 12 (✅) | correct | 12 |
| 235 | 1 (❌) | math | 1 (❌) | math | 21 |
| 236 | 10 (✅) | correct | 10 (✅) | correct | 10 |
| 237 | 30 (❌) | math | 30 (❌) | math | 31 |
| 238 | 90 (✅) | correct | 90 (✅) | correct | 90 |
| 239 | 68 (✅) | correct | 68 (✅) | correct | 68 |
| 240 | 280 (✅) | correct | 280 (✅) | correct | 280 |
| 241 | 21 (✅) | correct | 21 (✅) | correct | 21 |
| 242 | 6 (✅) | correct | 6 (✅) | correct | 6 |
| 243 | 3 (✅) | correct | 3 (✅) | correct | 3 |
| 244 | 250 (✅) | correct | 250 (✅) | correct | 250 |
| 245 | 11 (❌) | math | 11 (❌) | math | 20 |
| 246 | 14 (❌) | math | 14 (❌) | math | 7 |
| 247 | 27000 (✅) | correct | 27000 (✅) | correct | 27000 |
| 248 | 32 (✅) | correct | 32 (✅) | correct | 32 |
| 249 | 300 (✅) | correct | 300 (✅) | correct | 300 |
| 250 | 5600 (✅) | correct | 5600 (✅) | correct | 5600 |
| 251 | 10 (❌) | math | 10 (❌) | math | 17 |
| 252 | 70 (✅) | correct | 70 (✅) | correct | 70 |
| 253 | 82 (❌) | math | 82 (❌) | math | 73 |
| 254 | 18 (✅) | correct | 18 (✅) | correct | 18 |
| 255 | 84 (✅) | correct | 84 (✅) | correct | 84 |
| 256 | 176 (❌) | math | 176 (❌) | math | 192 |
| 257 | 45 (✅) | correct | 45 (✅) | correct | 45 |
| 258 | 16000 (❌) | math | 16000 (❌) | math | 5600 |
| 259 | 6 (✅) | correct | 6 (✅) | correct | 6 |
| 260 | 104 (❌) | math | 104 (❌) | math | 168 |
| 261 | 9 (❌) | math | 9 (❌) | math | 11 |
| 262 | 62 (✅) | correct | 62 (✅) | correct | 62 |
| 263 | 270 (✅) | correct | 270 (✅) | correct | 270 |
| 264 | 8 (✅) | correct | 8 (✅) | correct | 8 |
| 265 | 400 (✅) | correct | 400 (✅) | correct | 400 |
| 266 | 5000 (❌) | math | 5000 (❌) | math | 9500 |
| 267 | 230000 (❌) | math | 230000 (❌) | math | 118000 |
| 268 | 48 (❌) | math | 48 (❌) | math | 91 |
| 269 | 1375 (✅) | correct | 1375 (✅) | correct | 1375 |
| 270 | 4 (✅) | correct | 4 (✅) | correct | 4 |
| 271 | 762 (✅) | correct | 762 (✅) | correct | 762 |
| 272 | 20 (✅) | correct | 20 (✅) | correct | 20 |
| 273 | 5 (✅) | correct | 5 (✅) | correct | 5 |
| 274 | 265 (❌) | math | 265 (❌) | math | 315 |
| 275 | 3200 (✅) | correct | 3200 (✅) | correct | 3200 |
| 276 | 84 (❌) | math | 84 (❌) | math | 138 |
| 277 | 23 (❌) | math | 23 (❌) | math | 9 |
| 278 | 4 (✅) | correct | 4 (✅) | correct | 4 |
| 279 | 41 (❌) | math | 41 (❌) | math | 40 |
| 280 | 6 (✅) | correct | 6 (✅) | correct | 6 |
| 281 | 7 (✅) | correct | 7 (✅) | correct | 7 |
| 282 | 2012 (❌) | math | 2012 (❌) | math | 2450 |
| 283 | 225 (❌) | math | 225 (❌) | math | 195 |
| 284 | 68 (✅) | correct | 68 (✅) | correct | 68 |
| 285 | 240 (❌) | math | 240 (❌) | math | 360 |
| 286 | 21 (✅) | correct | 21 (✅) | correct | 21 |
| 287 | 90 (✅) | correct | 90 (✅) | correct | 90 |
| 288 | 8 (✅) | correct | 8 (✅) | correct | 8 |
| 289 | 3 (✅) | correct | 3 (✅) | correct | 3 |
| 290 | 240 (❌) | math | 240 (❌) | math | 16 |
| 291 | 27 (❌) | math | 27 (❌) | math | 390 |
| 292 | 2 (✅) | correct | 2 (✅) | correct | 2 |
| 293 | 90 (❌) | math | 90 (❌) | math | 75 |
| 294 | 83 (✅) | correct | 83 (✅) | correct | 83 |
| 295 | 3 (✅) | correct | 3 (✅) | correct | 3 |
| 296 | 540 (❌) | math | 540 (❌) | math | 370 |
| 297 | 3 (✅) | correct | 3 (✅) | correct | 3 |
| 298 | 55 (✅) | correct | 55 (✅) | correct | 55 |
| 299 | 350 (❌) | math | 350 (❌) | math | 500 |
| 300 | 31800 (✅) | correct | 31800 (✅) | correct | 31800 |
| 301 | 78 (✅) | correct | 78 (✅) | correct | 78 |
| 302 | 16 (❌) | math | 16 (❌) | math | 8 |
| 303 | 15 (✅) | correct | 15 (✅) | correct | 15 |
| 304 | 2200 (❌) | math | 2200 (❌) | math | 1300 |

## Artifact

Raw JSON: `labs/prompt/results/2026-06-07T164720Z-gsm8k-gepa-structured-json-train5-104-val105-304.json`
