from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass(frozen=True)
class EntreeFPS:
    date_iso: str
    fps_moyen: float
    frames: int


class HistoriqueFPS:
    def __init__(self, chemin: Path | None = None) -> None:
        racine = Path(__file__).resolve().parents[2]
        self.chemin = chemin or racine / "data" / "fps_executions.csv"

    def charger(self) -> list[EntreeFPS]:
        if not self.chemin.exists():
            return []

        entrees: list[EntreeFPS] = []
        with self.chemin.open("r", newline="", encoding="utf-8") as fichier:
            lecteur = csv.DictReader(fichier)
            for ligne in lecteur:
                try:
                    entrees.append(
                        EntreeFPS(
                            date_iso=ligne.get("date_iso", ""),
                            fps_moyen=float(ligne.get("fps_moyen", "0") or 0.0),
                            frames=int(ligne.get("frames", "0") or 0),
                        )
                    )
                except ValueError:
                    continue
        return entrees

    def charger_fps(self) -> list[float]:
        return [entree.fps_moyen for entree in self.charger() if entree.fps_moyen > 0.0]

    def enregistrer_execution(self, fps_moyen: float, frames: int) -> None:
        if fps_moyen <= 0.0 or frames <= 0:
            return

        self.chemin.parent.mkdir(parents=True, exist_ok=True)
        existe = self.chemin.exists()

        with self.chemin.open("a", newline="", encoding="utf-8") as fichier:
            champs = ("date_iso", "fps_moyen", "frames")
            writer = csv.DictWriter(fichier, fieldnames=champs)
            if not existe:
                writer.writeheader()
            writer.writerow(
                {
                    "date_iso": datetime.now().isoformat(timespec="seconds"),
                    "fps_moyen": f"{fps_moyen:.3f}",
                    "frames": str(frames),
                }
            )
