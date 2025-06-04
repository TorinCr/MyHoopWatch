# 🏀 Top100 – KenPom-Driven College Basketball Player Rankings

**Top100** is a data-driven web application that ranks the top NCAA Division I men's basketball players using advanced analytics inspired by the KenPom Player of the Year (KPOY) methodology.

This project uses normalized metrics from [KenPom](https://kenpom.com) and the [`kenpompy`](https://kenpompy.readthedocs.io/) library to score players based on offensive efficiency, usage, impact stats, and team performance.

---

## 🔍 Features

- 🧠 **KenPom-Inspired Rankings** – ORtg × Poss × Min-based player efficiency score
- 🔢 **17 Advanced Metrics** – Includes eFG%, ARate, STL, BLK, DR, OR, TS%, FTRate, and more
- 🧩 **Dynamic Normalization** – Stats are scaled across all qualified players
- 🏆 **KenPom Top 5 Badge** – Real-time badge for players in KenPom's official Top 10
- 🎨 **Clean, Responsive UI** – Players shown in stylized, hoverable cards
- 🖼 **Portrait Fallbacks** – Auto-generated avatars with optional custom images
- 🔄 **Designed for Updates** – Easily add new players, stats, or features

---

## 📊 Ranking Formula (Approximation of KPOY (so far))

KPOY_Score = (ORtg × Poss × Min%) × TeamStrength
           + Bonuses from: ARate, Stl, Blk, TS%, Reb
