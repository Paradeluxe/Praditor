# Praditor Code Review — Bug Report

Generated: 2026-05-20
Scope: Full codebase review (`src/app/`, `src/core/`, `src/gui/`, `src/utils/`)

## 🔴 Critical

| # | File | Line | Description | Status |
|---|------|------|-------------|--------|
| 1 | `src/core/detection.py` | 92–93 | `segments[-1]` IndexError when first segment has no onsets/offsets | ✅ Fixed |
| 2 | `src/core/detection.py` | 395 | `_answer[-1]` in list comprehension — actually a false positive; empty `for` skips guard evaluation | ❌ False positive |
| 3 | `src/core/detection.py` | 282–292 | `_onsets`/`_offsets` length mismatch after filtering loop may cause IndexError on `_offsets[i]` | ⬜ Pending |
| 4 | `src/utils/audio.py` | 70 | `__getitem__` duration: `(end - start) / 1000` should be `/ self.frame_rate` (start/end are sample indices) | ⬜ Pending |
| 5 | `src/app/main.py` | 94, 97 | `QThread.terminate()` is unsafe — causes deadlocks, memory leaks, inconsistent state | ⬜ Pending |
| 6 | `src/app/main.py` | 1012–1019, 1437 | `current_runnables` list modified from main thread and worker threads without lock | ⬜ Pending |
| 7 | `src/core/detection.py` | 52, 58, 67 | `eval()` on file/string input — code injection risk | ⬜ Pending |
| 8 | `src/gui/sliders.py` | 243–281 | `eval()` in `resetParams()` — code injection risk | ⬜ Pending |

## 🟡 Medium

| # | File | Line | Description | Status |
|---|------|------|-------------|--------|
| 9 | `src/app/main.py` | 318–320, 377–379 | Mode button signals connected twice → callbacks fire twice per click | ⬜ Pending |
| 10 | `src/app/main.py` | 1173–1216 | `new_onsets`/`new_offsets` undefined when `onsets and offsets` is false → NameError | ⬜ Pending |
| 11 | `src/app/main.py` | 895–896 | `lastParams`: `self.param_sets[current_mode].reverse()` mutates list in place, destroys history | ⬜ Pending |
| 12 | `src/app/main.py` | 337 | `sys.stdout` redirected but never restored on app exit | ⬜ Pending |
| 13 | `src/core/detection.py` | 41–43 | `segment_audio`: re-reads audio file from disk, ignoring the passed-in `audio_obj` | ⬜ Pending |
| 14 | `src/gui/plots.py` | 264, 310, 318 | `event.modifiers() == Qt.ControlModifier` fails with combined modifiers (Ctrl+Shift) | ⬜ Pending |
| 15 | `src/gui/plots.py` | 124 | `self.maximum - self.interval_ms` can be negative → slider malfunction | ⬜ Pending |
| 16 | `src/utils/audio.py` | 125–130 | `bandpass_filter`: ValueError fallback `[low, 1]` uses normalized freq, not actual Hz | ⬜ Pending |
| 17 | `src/app/main.py` | 566 | `playSound`: `QUrl.fromLocalFile(None)` when `self.file_path` is None | ⬜ Pending |
| 18 | `src/app/main.py` | 1755 | `prevnext_audio`: `showXsetNum()` missing `is_test` argument | ⬜ Pending |
| 19 | `src/utils/audio.py` | 63–67 | `__getitem__`: negative `start`/`end` sample indices not guarded | ⬜ Pending |
| 20 | `src/core/detection.py` | 229 | DBSCAN radius: `np.max([])` crashes on very small arrays | ⬜ Pending |

## 🔵 Low

| # | File | Line | Description | Status |
|---|------|------|-------------|--------|
| 21 | `src/app/main.py` | 8, 24 | Duplicate `sys.path.insert(0, ...)` | ⬜ Pending |
| 22 | `src/app/main.py` | 162 | `run_current_done` signal defined but no receiver connected | ⬜ Pending |
| 23 | `src/app/main.py` | 1732 | `self.which_one %= len(self.file_paths)` → ZeroDivisionError if empty | ⬜ Pending |
| 24 | `src/gui/plots.py` | 160, 167 | Duplicate `self._chart.legend().hide()` call | ⬜ Pending |
| 25 | `src/gui/plots.py` | 267, 269 | `self.interval_ms //= 2` floor division loses precision on odd values | ⬜ Pending |
| 26 | `src/gui/styles.py` | 61–68 | QSlider handle missing `height` property → rendering issue in some Qt versions | ⬜ Pending |
| 27 | `src/gui/sliders.py` | 188–224 | `getParams()` returns formatted display strings instead of actual numeric slider values | ⬜ Pending |
| 28 | `src/gui/toolbar.py` | 114 | Hardcoded 16px padding offset assumption in `scroll_text` | ⬜ Pending |
