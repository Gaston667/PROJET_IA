from __future__ import annotations

import tkinter as tk

from src.Composant.Force import Force
from src.Composant.Masse import Masse
from src.Composant.Position import Position
from src.Composant.Vitesse import Vitesse
from src.Config import Config
from src.Monde.Monde import Monde
from src.Rendu.Point3D import Point3D


def _telemetrie_lignes(
    monde: Monde,
    fps: float,
    inclure_camera: bool = False,
    rendu: object | None = None,
) -> list[str]:
    lignes = [
        "TELEMETRIE",
        "",
        f"Temps: {getattr(monde, 'temps_courant', 0.0):.3f} s",
        f"FPS: {fps:.1f}",
        f"Delta t: {Config.delta_t:.4f} s",
        f"Accumulateur: {getattr(monde, 'accumulateur', 0.0):.4f} s",
        f"Entites: {len(monde.entites)}",
    ]

    if inclure_camera and rendu is not None:
        lignes.append("")
        lignes.append(
            "Camera: "
            f"x={rendu.camera.position.x:.2f} y={rendu.camera.position.y:.2f} z={rendu.camera.position.z:.2f}"
        )
        if hasattr(rendu.camera, "yaw") and hasattr(rendu.camera, "pitch"):
            lignes.append(
                f"Orientation: yaw={rendu.camera.yaw:.1f} pitch={rendu.camera.pitch:.1f}"
            )

    for entite in monde.entites:
        lignes.append("")
        position = entite.get(Position)
        vitesse = entite.get(Vitesse)
        force = entite.get(Force)
        masse = entite.get(Masse)

        lignes.append(f"Entite {entite.id}")
        if position is not None:
            point = Point3D(position.x, position.y, position.z)
            lignes.append(
                f"  Pos: x={point.x:.2f} y={point.y:.2f} z={point.z:.2f}"
            )
        else:
            lignes.append("  Pos: n/a")
        lignes.append(
            "  Vit: "
            f"vx={vitesse.vx:.2f} vy={vitesse.vy:.2f} vz={vitesse.vz:.2f}"
            if vitesse is not None
            else "  Vit: n/a"
        )
        lignes.append(
            "  Force: "
            f"fx={force.fx:.2f} fy={force.fy:.2f} fz={force.fz:.2f}"
            if force is not None
            else "  Force: n/a"
        )
        lignes.append(
            f"  Masse: {masse.valeur:.2f} kg"
            if masse is not None
            else "  Masse: n/a"
        )

    return lignes


class FenetreTelemetrie:
    def __init__(self) -> None:
        self.active = True
        self.racine = tk.Tk()
        self.racine.title("Telemetrie")
        self.racine.geometry("420x720")
        self.racine.configure(bg="#101826")
        self.racine.protocol("WM_DELETE_WINDOW", self.fermer)

        self.texte = tk.Text(
            self.racine,
            bg="#101826",
            fg="#d7deeb",
            insertbackground="#d7deeb",
            relief="flat",
            borderwidth=0,
            padx=16,
            pady=16,
            font=("Consolas", 13),
        )
        self.texte.pack(fill="both", expand=True)
        self.texte.configure(state="disabled")

    def mettre_a_jour(self, monde: Monde, rendu: object) -> None:
        if not self.active:
            return

        lignes = _telemetrie_lignes(
            monde,
            rendu.clock.get_fps(),
            hasattr(rendu, "distance_projection"),
            rendu,
        )

        contenu = "\n".join(lignes)
        try:
            self.texte.configure(state="normal")
            self.texte.delete("1.0", tk.END)
            self.texte.insert("1.0", contenu)
            self.texte.configure(state="disabled")
            self.racine.update_idletasks()
            self.racine.update()
        except tk.TclError:
            self.active = False

    def fermer(self) -> None:
        if not self.active:
            return

        self.active = False
        try:
            self.racine.destroy()
        except tk.TclError:
            pass
