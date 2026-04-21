from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from src.Composant.Force import Force
from src.Composant.Masse import Masse
from src.Composant.Position import Position
from src.Composant.Renderable import Renderable
from src.Composant.Vitesse import Vitesse
from src.Config import Config
from src.Monde.Monde import Monde
from src.Outils.Profiler import Profiler
from src.Rendu.Point3D import Point3D


def _fmt_ms(valeur: float) -> str:
    return f"{valeur:8.3f}"


class FenetreTelemetrie:
    def __init__(self, profiler: Profiler | None = None) -> None:
        self.active = True
        self.profiler = profiler
        self.racine = tk.Tk()
        self.racine.title("Telemetrie")
        self.racine.geometry("760x820+860+40")
        self.racine.minsize(420, 360)
        self.racine.resizable(True, True)
        self.racine.configure(bg="#0f172a")
        self.racine.protocol("WM_DELETE_WINDOW", self.fermer)
        self._premier_affichage = True

        self.couleurs = {
            "fond": "#0f172a",
            "panneau": "#111c33",
            "panneau2": "#17243d",
            "texte": "#e5edf8",
            "muted": "#97a6ba",
            "accent": "#38bdf8",
            "vert": "#4ade80",
            "orange": "#fbbf24",
            "rouge": "#fb7185",
        }

        self._configurer_style()
        self._construire_interface()
        self._afficher_devant()

    def _configurer_style(self) -> None:
        style = ttk.Style(self.racine)
        style.theme_use("clam")
        style.configure(
            "Treeview",
            background=self.couleurs["panneau"],
            fieldbackground=self.couleurs["panneau"],
            foreground=self.couleurs["texte"],
            rowheight=26,
            borderwidth=0,
            font=("Consolas", 10),
        )
        style.configure(
            "Treeview.Heading",
            background=self.couleurs["panneau2"],
            foreground=self.couleurs["texte"],
            relief="flat",
            font=("Segoe UI", 10, "bold"),
        )
        style.map("Treeview", background=[("selected", self.couleurs["accent"])])

    def _construire_interface(self) -> None:
        self.racine.grid_columnconfigure(0, weight=1)
        self.racine.grid_rowconfigure(2, weight=1)
        self.racine.grid_rowconfigure(4, weight=1)

        titre = tk.Label(
            self.racine,
            text="TELEMETRIE",
            bg=self.couleurs["fond"],
            fg=self.couleurs["texte"],
            font=("Segoe UI", 18, "bold"),
            anchor="w",
            padx=18,
            pady=12,
        )
        titre.grid(row=0, column=0, sticky="ew")

        self.cartes = tk.Frame(self.racine, bg=self.couleurs["fond"])
        self.cartes.grid(row=1, column=0, sticky="ew", padx=14)
        for colonne in range(4):
            self.cartes.grid_columnconfigure(colonne, weight=1)

        self.labels_cartes: dict[str, tk.Label] = {}
        self._ajouter_carte("fps", "FPS", 0)
        self._ajouter_carte("frame", "FRAME MS", 1)
        self._ajouter_carte("physique", "PHYSIQUE MS", 2)
        self._ajouter_carte("rendu", "RENDU MS", 3)

        self.tableau = ttk.Treeview(
            self.racine,
            columns=("mesure", "dernier", "moyenne", "min", "max", "appels"),
            show="headings",
            height=12,
        )
        self.tableau.heading("mesure", text="Mesure")
        self.tableau.heading("dernier", text="Dernier ms")
        self.tableau.heading("moyenne", text="Moyenne ms")
        self.tableau.heading("min", text="Min ms")
        self.tableau.heading("max", text="Max ms")
        self.tableau.heading("appels", text="Appels")
        self.tableau.column("mesure", width=220, anchor="w", stretch=True)
        self.tableau.column("dernier", width=115, anchor="e")
        self.tableau.column("moyenne", width=115, anchor="e")
        self.tableau.column("min", width=100, anchor="e")
        self.tableau.column("max", width=100, anchor="e")
        self.tableau.column("appels", width=90, anchor="e")
        self.tableau.grid(row=2, column=0, sticky="nsew", padx=14, pady=(12, 8))

        self.zone_infos = tk.Frame(self.racine, bg=self.couleurs["panneau"])
        self.zone_infos.grid(row=4, column=0, sticky="nsew", padx=14, pady=(8, 14))
        self.zone_infos.grid_columnconfigure(0, weight=1)
        self.zone_infos.grid_rowconfigure(0, weight=1)

        self.infos = tk.Text(
            self.zone_infos,
            bg=self.couleurs["panneau"],
            fg=self.couleurs["texte"],
            insertbackground=self.couleurs["texte"],
            relief="flat",
            borderwidth=0,
            padx=16,
            pady=14,
            font=("Consolas", 11),
            wrap="none",
            height=14,
        )
        self.scroll_infos_y = ttk.Scrollbar(
            self.zone_infos,
            orient="vertical",
            command=self.infos.yview,
        )
        self.scroll_infos_x = ttk.Scrollbar(
            self.zone_infos,
            orient="horizontal",
            command=self.infos.xview,
        )
        self.infos.configure(
            yscrollcommand=self.scroll_infos_y.set,
            xscrollcommand=self.scroll_infos_x.set,
        )
        self.infos.grid(row=0, column=0, sticky="nsew")
        self.scroll_infos_y.grid(row=0, column=1, sticky="ns")
        self.scroll_infos_x.grid(row=1, column=0, sticky="ew")
        self.infos.configure(state="disabled")

    def _ajouter_carte(self, cle: str, titre: str, colonne: int) -> None:
        carte = tk.Frame(self.cartes, bg=self.couleurs["panneau"], padx=12, pady=10)
        carte.grid(row=0, column=colonne, sticky="ew", padx=4)

        label_titre = tk.Label(
            carte,
            text=titre,
            bg=self.couleurs["panneau"],
            fg=self.couleurs["muted"],
            font=("Segoe UI", 9, "bold"),
            anchor="w",
        )
        label_titre.pack(fill="x")

        label_valeur = tk.Label(
            carte,
            text="0.000",
            bg=self.couleurs["panneau"],
            fg=self.couleurs["accent"],
            font=("Consolas", 18, "bold"),
            anchor="w",
        )
        label_valeur.pack(fill="x", pady=(5, 0))
        self.labels_cartes[cle] = label_valeur

    def mettre_a_jour(self, monde: Monde, rendu: object, profiler: Profiler | None = None) -> None:
        if not self.active:
            return

        profiler_actif = profiler or self.profiler
        self.profiler = profiler_actif

        try:
            self._mettre_a_jour_cartes(monde, rendu, profiler_actif)
            self._mettre_a_jour_tableau(profiler_actif)
            self._mettre_a_jour_infos(monde, rendu, profiler_actif)
            if self._premier_affichage:
                self._afficher_devant()
                self._premier_affichage = False
            self.racine.update_idletasks()
            self.racine.update()
        except tk.TclError:
            self.active = False

    def _afficher_devant(self) -> None:
        self.racine.deiconify()
        self.racine.lift()
        self.racine.attributes("-topmost", True)
        self.racine.after(500, lambda: self.racine.attributes("-topmost", False))
        self.racine.update_idletasks()
        self.racine.update()

    def _mettre_a_jour_cartes(
        self,
        monde: Monde,
        rendu: object,
        profiler: Profiler | None,
    ) -> None:
        fps = rendu.clock.get_fps() if getattr(rendu, "clock", None) is not None else 0.0
        frame_ms = 0.0
        physique_ms = 0.0
        rendu_ms = 0.0

        if profiler is not None:
            mesures = profiler.snapshot()
            frame_ms = mesures.get("frame").moyenne_ms if "frame" in mesures else 0.0
            rendu_ms = mesures.get("rendu").moyenne_ms if "rendu" in mesures else 0.0
            physique_ms = sum(
                mesure.moyenne_ms
                for nom, mesure in mesures.items()
                if nom.startswith("systeme.")
            )
            fps_profil = profiler.fps_moyen()
            if fps_profil > 0.0:
                fps = fps_profil

        self.labels_cartes["fps"].configure(text=f"{fps:.1f}", fg=self._couleur_fps(fps))
        self.labels_cartes["frame"].configure(text=f"{frame_ms:.3f}")
        self.labels_cartes["physique"].configure(text=f"{physique_ms:.3f}")
        self.labels_cartes["rendu"].configure(text=f"{rendu_ms:.3f}")

    def _mettre_a_jour_tableau(self, profiler: Profiler | None) -> None:
        self.tableau.delete(*self.tableau.get_children())

        if profiler is None:
            return

        for nom, mesure in profiler.snapshot().items():
            self.tableau.insert(
                "",
                "end",
                values=(
                    nom,
                    _fmt_ms(mesure.dernier_ms),
                    _fmt_ms(mesure.moyenne_ms),
                    _fmt_ms(mesure.min_ms),
                    _fmt_ms(mesure.max_ms),
                    str(mesure.appels),
                ),
            )

    def _mettre_a_jour_infos(
        self,
        monde: Monde,
        rendu: object,
        profiler: Profiler | None,
    ) -> None:
        lignes = self._lignes_infos(monde, rendu, profiler)
        contenu = "\n".join(lignes)
        scroll_y = self.infos.yview()
        scroll_x = self.infos.xview()
        self.infos.configure(state="normal")
        self.infos.delete("1.0", tk.END)
        self.infos.insert("1.0", contenu)
        self.infos.configure(state="disabled")
        self.infos.yview_moveto(scroll_y[0])
        self.infos.xview_moveto(scroll_x[0])

    def _lignes_infos(
        self,
        monde: Monde,
        rendu: object,
        profiler: Profiler | None,
    ) -> list[str]:
        lignes = [
            f"Temps           {getattr(monde, 'temps_courant', 0.0):.3f} s",
            f"Delta t         {Config.delta_t:.4f} s",
            f"Accumulateur    {getattr(monde, 'accumulateur', 0.0):.4f} s",
            f"Entites         {len(monde.entites)}",
        ]

        camera = getattr(rendu, "camera", None)
        if camera is not None:
            lignes.extend([
                "",
                "Camera",
                f"  Position      x={camera.position.x:.2f} y={camera.position.y:.2f} z={camera.position.z:.2f}",
                f"  Orientation   yaw={camera.yaw:.1f} pitch={camera.pitch:.1f}",
            ])

        if profiler is not None:
            compteurs = profiler.compteurs_frame()
            if compteurs:
                lignes.append("")
                lignes.append("Compteurs frame")
                for nom, valeur in compteurs.items():
                    lignes.append(f"  {nom:<18} {valeur}")

        compteurs_rendu = {
            "objets_rendus": getattr(rendu, "objets_rendus", 0),
            "objets_occlus_pixels": getattr(rendu, "objets_occlus_pixels", 0),
        }
        lignes.append("")
        lignes.append("Compteurs rendu")
        for nom, valeur in compteurs_rendu.items():
            lignes.append(f"  {nom:<18} {valeur}")

        for entite in monde.entites:
            lignes.append("")
            lignes.extend(self._lignes_entite(entite))

        return lignes

    def _lignes_entite(self, entite: object) -> list[str]:
        position = entite.get(Position)
        vitesse = entite.get(Vitesse)
        force = entite.get(Force)
        masse = entite.get(Masse)
        renderable = entite.get(Renderable)

        lignes = [f"Entite {entite.id}"]
        if position is not None:
            point = Point3D(position.x, position.y, position.z)
            lignes.append(f"  Pos           x={point.x:.2f} y={point.y:.2f} z={point.z:.2f}")
        else:
            lignes.append("  Pos           n/a")

        if vitesse is not None:
            lignes.append(f"  Vit           vx={vitesse.vx:.2f} vy={vitesse.vy:.2f} vz={vitesse.vz:.2f}")
        else:
            lignes.append("  Vit           n/a")

        if force is not None:
            lignes.append(f"  Force         fx={force.fx:.2f} fy={force.fy:.2f} fz={force.fz:.2f}")
        else:
            lignes.append("  Force         n/a")

        lignes.append(f"  Masse         {masse.valeur:.2f} kg" if masse is not None else "  Masse         n/a")
        lignes.append(f"  Segments      {renderable.segments}" if renderable is not None else "  Segments      n/a")
        return lignes

    def _couleur_fps(self, fps: float) -> str:
        if fps >= 55.0:
            return self.couleurs["vert"]
        if fps >= 30.0:
            return self.couleurs["orange"]
        return self.couleurs["rouge"]

    def fermer(self) -> None:
        if not self.active:
            return

        self.active = False
        try:
            self.racine.destroy()
        except tk.TclError:
            pass
