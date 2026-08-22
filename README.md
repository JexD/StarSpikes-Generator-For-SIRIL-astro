<img width="1532" height="1235" alt="StarSpike_generator_illu" src="https://github.com/user-attachments/assets/0c0dd225-2e82-4976-bba0-cc954e8461ac" />

---
# StarSpikes Generator V1.1.2

A standalone Python/Tkinter application for adding customizable diffraction spikes (star spikes) to astrophotography images. The interface follows the dark visual style of [Siril](https://siril.org/), and the generator is intended for images prepared or processed with Siril and other astrophotography workflows.

**Version:** 1.1.2  
**Author:** Jerome Desvignes (JeX)  
**Contact:** jex3dvf@gmail.com  
**License:** GNU General Public License v3.0 or later (GPL-3.0-or-later)

## Features

- Bright-star detection using an adjustable grayscale threshold.
- Minimum and maximum detected-star area filters.
- Optional limit on the number of stars processed, ordered by estimated flux.
- Automatic spike scaling from each star's estimated brightness/flux.
- Manual star or galaxy exclusion with a left click on the preview.
- Exclusion-marker visibility toggle and reset button.
- Four-branch diffraction pattern for Newtonian/RC-style appearances.
- Six-branch diffraction pattern for JWST/aperture-style appearances.
- Adjustable spike length, thickness, taper scaling, rotation, blur, and opacity.
- Two spectral modes:
  - **Standard / Fast:** original warm-to-cool chromatic aberration effect.
  - **Physical Spectral Rainbow:** continuous spectral coloring with spread and saturation controls.
- Preview controls for Fit to View, 1:1 (100%) zoom, mouse-wheel zoom, and right-button panning.
- PNG, TIFF, and JPG export.
- Dark Siril-inspired interface, including a dark Windows 10/11 title bar when supported.

## Requirements

- SIRIL 1.4.x. fetch it at  https://siril.org/fr/

## Installation

1. Download script and place `StarSpikes_Generator_V1.1.2.py` in basic or custom SIRIL script folder.


## Running the application

From the SIRIL script menu run the script:


The program opens a desktop window. It does not accept command-line arguments and does not modify the original image in place.

## Basic workflow

1. Click **1. Load Image** and select a PNG, JPG/JPEG, or TIFF image.
2. Adjust the **Stars Detection** controls until the intended stars are detected.
3. Adjust **Spikes Look**, branch count, and the spectral controls.
4. Click **PREVIEW** to render the effect.
5. Left-click detected stars or galaxies in the preview to exclude or re-include them.
6. Use **Fit to View**, **1:1 (100%)**, the mouse wheel, and right-button dragging to inspect the result.
7. Click **Save Image** and choose PNG, TIFF, or JPG.

The red exclusion markers are preview-only guides. They are not drawn into the exported image.

## Controls

### Stars Detection

| Control | Range | Default | Description |
|---|---:|---:|---|
| Bright Star threshold | 0–255 | 220 | Pixels above this grayscale threshold become detection candidates. Lower values detect more objects; higher values restrict detection to brighter pixels. |
| Max Stars | 0–500 | 15 | Maximum number of stars processed. `0` means unlimited. Candidates are ranked by estimated flux. |
| Star Min Size | 1–100 px² | 50 | Rejects connected components smaller than this area. |
| Max Star Area | 0–10,000 px² | 0 | Rejects components larger than this area. `0` means unlimited. |

Detection is based on connected bright regions in the grayscale image. The application estimates each candidate's size, mean brightness, and flux; the flux estimate is used for sorting and optional automatic scaling.

### Star / Galaxy Exclusion

- **Left-click on a detected object:** toggle that object's exclusion state.
- **Hide Markers / Show Markers:** hide or display the red dashed exclusion guides.
- **Reset:** clear all exclusions and regenerate the preview when an image is loaded.

The click tolerance is proportional to object size, with a minimum tolerance, so clicking near a detected star is sufficient.

### Auto Brightness Scaling

| Control | Range | Default | Description |
|---|---:|---:|---|
| Auto-Scale Luminosity | 0–100% | 12.00% | Mixes a uniform spike scale with a scale based on relative candidate flux. |
| Dynamic Range Compression | 0.10–2.00 | 1.00 | Exponent applied to relative flux when automatic scaling is active. |

### Spikes Look

| Control | Range | Default | Description |
|---|---:|---:|---|
| Base Length | 1–50% of image size | 4.00% | Base spike length, calculated from the larger image dimension. |
| Star Size Factor → Length | 0–10 | 2.50 | Adds a size-dependent contribution to each spike's length. |
| Base Thickness | 0.5–20 px | 2.00 px | Starting width of each tapered branch. |
| Rotation Angle | 0–360° | 0.00° | Rotates the complete branch pattern. |
| Branches Number | 4 or 6 | 4 | Four branches produce a 90° pattern; six branches produce a 60° pattern. |
| Softening / Blur | 1–51 px | 5 px | Gaussian blur applied to the generated spike mask. Even values are increased to the next odd value. |
| Global Opacity | 0–100% | 100.00% | Blend strength used when adding the spike mask to the original image. |

### Spectral Diffraction

Choose one mode:

- **Standard / Fast (Instant):** enables **Chromatic Aberration** and uses the original warm-to-cool color transition along each branch.
- **Physical Spectral Rainbow:** enables the rainbow controls and disables **Chromatic Aberration**. The color varies continuously along the spike using a spectral model with an adjustable envelope.

| Control | Range | Default | Active mode | Description |
|---|---:|---:|---|---|
| Chromatic Aberration | 0–10 px | 8 | Standard | Amount of the standard warm/cool chromatic effect. |
| Spectral Rainbow | 0–100% | 50.00% | Physical | Mix between white and the generated spectral color. |
| Rainbow Spread | 10–100% | 45.00% | Physical | Controls how quickly the spectral transition develops along a branch. |
| Rainbow Saturation | 0–200% | 100.00% | Physical | Reduces or increases spectral color saturation. |

## Supported images and conversion behavior

The file chooser accepts:

- PNG (`.png`)
- JPEG (`.jpg`, `.jpeg`)
- TIFF (`.tif`, `.tiff`)

Images are decoded with OpenCV. Grayscale images are converted to three-channel color for processing. Images with an alpha channel have that channel removed. Images whose source data is not 8-bit are normalized to the 0–255 range and converted to 8-bit before processing. Consequently, this version is not a high-bit-depth-preserving workflow.

The exported result is an 8-bit image. PNG, TIFF, and JPG are available in the save dialog; JPG export may introduce normal JPEG compression and does not preserve transparency.

## Preview navigation

- **Fit to View:** fit the processed image inside the preview canvas.
- **1:1 (100%):** display the image at native pixel scale.
- **Mouse wheel:** zoom in or out, clamped by the application between 1% and 2,000%.
- **Right-button drag:** pan the preview.
- **Left click:** exclude or re-include the nearest detected star/galaxy.

## Processing notes

The generator creates a separate floating-point spike mask, draws tapered branches for every non-excluded candidate, optionally blurs the mask, and blends it with the original image. The original loaded image remains in memory as the source for each preview regeneration; changing settings and clicking **PREVIEW** therefore rebuilds the effect rather than repeatedly stacking it.

If no connected component satisfies the detection filters, the application reports that no star was detected and does not generate a new preview. If the input image has no stars but the preview object from an earlier operation exists, save behavior follows the current in-memory processed image state; reload the source or regenerate as needed when changing workflows.

## Troubleshooting

### The application does not start

- Confirm that Python 3 is installed and available as `python`.
- Confirm that Tkinter is installed.
- Install or upgrade the required packages:

  ```bash
  python -m pip install --upgrade numpy opencv-python Pillow
  ```

### Too many or too few stars are detected

- Increase **Bright Star threshold** to detect fewer, brighter objects.
- Decrease the threshold to include fainter objects.
- Increase **Star Min Size** to reject small noise components.
- Set **Max Star Area** to reject large nebula/galaxy-like components.
- Use **Max Stars** to cap the number of candidates.
- Exclude remaining unwanted objects by left-clicking them in the preview.

### The preview appears blank or the effect is weak

- Confirm that an image has been loaded.
- Click **PREVIEW** after changing controls.
- Lower the detection threshold or adjust the area filters.
- Increase **Base Length**, **Base Thickness**, or **Global Opacity**.
- Verify that the intended objects have not been excluded.

### The Windows title bar is not dark

This is an optional Windows 10/11 appearance enhancement. It is skipped on non-Windows platforms and silently ignored when the Windows API does not support the requested attribute; it does not affect image processing.

## License

This project is released under the GNU General Public License, version 3 or any later version. See the SPDX identifier in `StarSpikes_Generator_V1.1.2.py`:

```text
SPDX-License-Identifier: GPL-3.0-or-later
```

---

# Générateur d'aigrettes V1.1.2

Application autonome en Python/Tkinter permettant d'ajouter des aigrettes de diffraction personnalisables aux images d'astrophotographie. L'interface reprend l'apparence sombre de [Siril](https://siril.org/) et le générateur est destiné aux images préparées ou traitées avec Siril ainsi qu'à d'autres flux de travail d'astrophotographie.

**Version :** 1.1.2  
**Auteur :** Jerome Desvignes (JeX)  
**Contact :** jex3dvf@gmail.com  
**Licence :** GNU General Public License v3.0 ou ultérieure (GPL-3.0-or-later)

## Fonctionnalités

- Détection des étoiles brillantes avec seuil de niveaux de gris réglable.
- Filtres de surface minimale et maximale des objets détectés.
- Limitation optionnelle du nombre d'étoiles traitées, classées selon le flux estimé.
- Mise à l'échelle automatique des aigrettes selon la luminosité/flux estimé de chaque étoile.
- Exclusion manuelle d'une étoile ou d'une galaxie par clic gauche dans l'aperçu.
- Bouton pour afficher/masquer les repères d'exclusion et bouton de réinitialisation.
- Motif à quatre branches pour une apparence de type Newton/RC.
- Motif à six branches pour une apparence de type JWST/ouverture.
- Réglage de la longueur, de l'épaisseur, de l'influence de la taille, de la rotation, du flou et de l'opacité.
- Deux modes spectraux :
  - **Standard / Rapide :** effet original d'aberration chromatique allant des tons chauds aux tons froids.
  - **Arc-en-ciel spectral physique :** coloration spectrale continue avec réglages de diffusion et de saturation.
- Contrôles d'aperçu : ajustement à la vue, zoom 1:1 (100 %), zoom à la molette et déplacement avec le bouton droit.
- Export PNG, TIFF et JPG.
- Interface sombre inspirée de Siril, avec barre de titre sombre sous Windows 10/11 lorsque cela est pris en charge.

## Prérequis

- SIRIL telechargeable ici https://siril.org/fr/

## Installation

1. Téléchargez ou clonez ce dépôt et placez `StarSpikes_Generator_V1.1.2.py` dans le dossier de script de SIRIL ou un dossier Custom de votre choix, à renseigner dans les preferences SIRIL.

## Lancer l'application

Depuis le menu script, exécutez StarSpikes_Generator_V1.1.2:

Le programme ouvre une fenêtre de bureau. Il n'accepte pas d'arguments en ligne de commande et ne modifie pas directement l'image originale.

## Flux de travail de base

1. Cliquez sur **1. Load Image** et sélectionnez une image PNG, JPG/JPEG ou TIFF.
2. Ajustez les réglages de **Stars Detection** jusqu'à obtenir les étoiles souhaitées.
3. Réglez **Spikes Look**, le nombre de branches et les contrôles spectraux.
4. Cliquez sur **PREVIEW** pour générer l'effet.
5. Cliquez avec le bouton gauche sur les étoiles ou galaxies à exclure ou à réinclure.
6. Utilisez **Fit to View**, **1:1 (100%)**, la molette et le glissement avec le bouton droit pour inspecter le résultat.
7. Cliquez sur **Save Image** et choisissez PNG, TIFF ou JPG.

Les repères rouges d'exclusion sont uniquement des guides d'aperçu. Ils ne sont pas présents dans l'image exportée.

## Contrôles

### Détection des étoiles

| Contrôle | Plage | Valeur par défaut | Description |
|---|---:|---:|---|
| Bright Star threshold | 0–255 | 220 | Les pixels au-dessus de ce seuil en niveaux de gris deviennent des candidats. Une valeur plus faible détecte davantage d'objets ; une valeur plus élevée limite la détection aux pixels plus lumineux. |
| Max Stars | 0–500 | 15 | Nombre maximal d'étoiles traitées. `0` signifie illimité. Les candidats sont classés par flux estimé. |
| Star Min Size | 1–100 px² | 50 | Élimine les composantes connexes dont la surface est inférieure à cette valeur. |
| Max Star Area | 0–10 000 px² | 0 | Élimine les composantes dont la surface est supérieure à cette valeur. `0` signifie illimité. |

La détection repose sur les régions lumineuses connexes de l'image en niveaux de gris. L'application estime la taille, la luminosité moyenne et le flux de chaque candidat ; le flux sert au classement et à la mise à l'échelle automatique éventuelle.

### Exclusion d'étoiles/de galaxies

- **Clic gauche sur un objet détecté :** active ou désactive son exclusion.
- **Hide Markers / Show Markers :** masque ou affiche les repères rouges en pointillés.
- **Reset :** efface toutes les exclusions et régénère l'aperçu lorsqu'une image est chargée.

La tolérance du clic est proportionnelle à la taille de l'objet, avec une tolérance minimale ; il suffit donc de cliquer près d'une étoile détectée.

### Mise à l'échelle automatique selon la luminosité

| Contrôle | Plage | Valeur par défaut | Description |
|---|---:|---:|---|
| Auto-Scale Luminosity | 0–100 % | 12,00 % | Mélange une échelle uniforme avec une échelle basée sur le flux relatif du candidat. |
| Dynamic Range Compression | 0,10–2,00 | 1,00 | Exposant appliqué au flux relatif lorsque la mise à l'échelle automatique est active. |

### Apparence des aigrettes

| Contrôle | Plage | Valeur par défaut | Description |
|---|---:|---:|---|
| Base Length | 1–50 % de la taille de l'image | 4,00 % | Longueur de base calculée à partir de la plus grande dimension de l'image. |
| Star Size Factor → Length | 0–10 | 2,50 | Ajoute une contribution dépendant de la taille à la longueur de chaque aigrette. |
| Base Thickness | 0,5–20 px | 2,00 px | Largeur initiale de chaque branche effilée. |
| Rotation Angle | 0–360° | 0,00° | Fait pivoter l'ensemble du motif. |
| Branches Number | 4 ou 6 | 4 | Quatre branches créent un motif à 90° ; six branches créent un motif à 60°. |
| Softening / Blur | 1–51 px | 5 px | Flou gaussien appliqué au masque d'aigrettes. Les valeurs paires sont augmentées à la valeur impaire suivante. |
| Global Opacity | 0–100 % | 100,00 % | Force du mélange lors de l'ajout du masque à l'image originale. |

### Diffraction spectrale

Choisissez un mode :

- **Standard / Fast (Instant) :** active **Chromatic Aberration** et utilise la transition originale entre couleurs chaudes et froides le long de chaque branche.
- **Physical Spectral Rainbow :** active les réglages de l'arc-en-ciel et désactive **Chromatic Aberration**. La couleur varie continuellement le long de l'aigrette selon un modèle spectral avec une enveloppe réglable.

| Contrôle | Plage | Valeur par défaut | Mode actif | Description |
|---|---:|---:|---|---|
| Chromatic Aberration | 0–10 px | 8 | Standard | Intensité de l'effet chromatique chaud/froid standard. |
| Spectral Rainbow | 0–100 % | 50,00 % | Physique | Mélange entre le blanc et la couleur spectrale générée. |
| Rainbow Spread | 10–100 % | 45,00 % | Physique | Contrôle la vitesse de transition spectrale le long d'une branche. |
| Rainbow Saturation | 0–200 % | 100,00 % | Physique | Diminue ou augmente la saturation des couleurs spectrales. |

## Images prises en charge et conversions

Le sélecteur de fichiers accepte :

- PNG (`.png`)
- JPEG (`.jpg`, `.jpeg`)
- TIFF (`.tif`, `.tiff`)

Les images sont décodées par OpenCV. Les images en niveaux de gris sont converties en couleur à trois canaux pour le traitement. Les images possédant un canal alpha perdent ce canal. Les données qui ne sont pas sur 8 bits sont normalisées sur l'intervalle 0–255 puis converties en 8 bits. Cette version ne conserve donc pas les hautes profondeurs de bits.

Le résultat exporté est une image 8 bits. PNG, TIFF et JPG sont disponibles dans la boîte de dialogue d'enregistrement ; l'export JPG peut introduire la compression JPEG habituelle et ne conserve pas la transparence.

## Navigation dans l'aperçu

- **Fit to View :** ajuste l'image traitée dans le canevas d'aperçu.
- **1:1 (100%) :** affiche l'image à son échelle native en pixels.
- **Molette :** zoome en avant ou en arrière, entre 1 % et 2 000 %.
- **Glissement avec le bouton droit :** déplace l'aperçu.
- **Clic gauche :** exclut ou réinclut l'étoile/galaxie détectée la plus proche.

## Notes de traitement

Le générateur crée un masque d'aigrettes en virgule flottante, dessine des branches effilées pour chaque candidat non exclu, applique éventuellement un flou, puis mélange le masque avec l'image originale. L'image originale chargée reste la source de chaque aperçu ; modifier les réglages et cliquer sur **PREVIEW** reconstruit donc l'effet au lieu de l'empiler à chaque fois.

Si aucune composante connexe ne satisfait les filtres de détection, l'application indique qu'aucune étoile n'a été détectée et ne crée pas de nouvel aperçu. Si l'image ne contient aucune étoile mais qu'un aperçu traité existait auparavant, l'enregistrement suit l'état de l'image traitée conservée en mémoire ; rechargez la source ou régénérez l'aperçu selon le flux de travail souhaité.

## Dépannage

### L'application ne démarre pas

- Vérifiez que Python 3 est installé et accessible avec la commande `python`.
- Vérifiez que Tkinter est installé.
- Installez ou mettez à jour les paquets requis :

  ```bash
  python -m pip install --upgrade numpy opencv-python Pillow
  ```

### Trop ou pas assez d'étoiles sont détectées

- Augmentez **Bright Star threshold** pour détecter moins d'objets plus brillants.
- Diminuez le seuil pour inclure des objets plus faibles.
- Augmentez **Star Min Size** pour éliminer les petites composantes de bruit.
- Définissez **Max Star Area** pour éliminer les grandes composantes de type nébuleuse/galaxie.
- Utilisez **Max Stars** pour plafonner le nombre de candidats.
- Excluez les objets restants par clic gauche dans l'aperçu.

### L'aperçu semble vide ou l'effet est faible

- Vérifiez qu'une image a été chargée.
- Cliquez sur **PREVIEW** après avoir modifié les contrôles.
- Diminuez le seuil de détection ou ajustez les filtres de surface.
- Augmentez **Base Length**, **Base Thickness** ou **Global Opacity**.
- Vérifiez que les objets souhaités n'ont pas été exclus.

### La barre de titre Windows n'est pas sombre

Il s'agit d'une amélioration visuelle optionnelle pour Windows 10/11. Elle est ignorée sur les systèmes non Windows et silencieusement désactivée lorsque l'API Windows ne prend pas en charge l'attribut demandé ; cela n'a aucun effet sur le traitement des images.

## Licence

Ce projet est distribué sous la GNU General Public License, version 3 ou toute version ultérieure. Consultez l'identifiant SPDX dans `StarSpikes_Generator_V1.1.2.py` :

```text
SPDX-License-Identifier: GPL-3.0-or-later
```
