<img width="1532" height="1235" alt="StarSpike_generator_illu" src="https://github.com/user-attachments/assets/0c0dd225-2e82-4976-bba0-cc954e8461ac" />

---

# 📖 Star Spikes Generator — Code & Architecture Documentation

## 📌 Overview
**Star Spikes Generator** is a Python desktop utility built with **Tkinter** and **OpenCV** designed to detect stars in astronomical images and synthesize realistic diffraction spikes (aigrettes) with chromatic aberration, tapered branches, luminosity auto-scaling, and dynamic range compression.

---

## 🛠️ Global Functions

### `set_dark_title_bar(window)`
* **Description:** Enables the native immersive dark mode title bar on Windows 10 (version 1809+) and Windows 11 using the Windows Desktop Window Manager (`DWMAPI.dll`).
* **Parameters:**
  * `window` (`tk.Tk` / `tk.Toplevel`): The Tkinter window instance.
* **Platform Behavior:** Runs only on `win32` platform; fails silently on Linux and macOS to prevent crashes.

---

## 🏛️ Class: `AigrettesGeneratorApp`

The main application class encapsulating GUI management, event handlers, star detection algorithms, and spike rendering.

---

### 1. Initialization & UI Setup

#### `__init__(self, root)`
* **Description:** Initializes the application state (zoom, image buffers), configures the window geometry, loads the custom SIRIL dark theme, builds GUI widgets, and activates the dark title bar.
* **Parameters:**
  * `root` (`tk.Tk`): Main Tkinter root window.

#### `_setup_siril_theme(self)`
* **Description:** Configures a custom `ttk` style matching **Siril's Dark Theme** (dark gray background `#2b2b2b`, custom sliders, entries, labels, buttons, and cyan/light-blue `#4cc2ff` active accents).

#### `_create_widgets(self)`
* **Description:** Builds the left control panel (sliders, radio buttons, action buttons) and right canvas preview area. Binds mouse events for interactive pan and zoom.

#### `_add_slider(self, parent, label_text, min_val, max_val, default_val, is_integer=False)`
* **Description:** Helper method creating a synchronized combination of a **Label**, **ttk.Scale (Slider)**, and **ttk.Entry (Text field)**.
* **Parameters:**
  * `parent`: Parent GUI container.
  * `label_text` (*str*): Display text.
  * `min_val` (*float/int*): Minimum allowed value.
  * `max_val` (*float/int*): Maximum allowed value.
  * `default_val` (*float/int*): Initial starting value.
  * `is_integer` (*bool*): If `True`, locks values to whole integers (`int`). If `False`, formats floats to **2 decimal places**.
* **Returns:** `tk.DoubleVar` bound to the slider and entry.

---

### 2. Viewport & Canvas Navigation

#### `_on_mousewheel(self, event)`
* **Description:** Handles mouse scroll wheel inputs (supporting both Windows `delta` and Linux `Button-4/5`) to zoom in or out on the canvas (range: `0.05x` to `20.0x`).

#### `_on_pan_start(self, event)`
* **Description:** Records the starting coordinates of the right-click drag action (`<ButtonPress-3>`) for panning the image canvas.

#### `_on_pan_move(self, event)`
* **Description:** Shifts the canvas view dynamically based on mouse drag movement (`<B3-Motion>`).

#### `display_image(self, img_bgr)`
* **Description:** Converts the internal OpenCV BGR image to RGB, applies the current zoom factor, converts it to a `PIL.ImageTk.PhotoImage`, and centers it on the Tkinter canvas.
* **Parameters:**
  * `img_bgr` (*numpy.ndarray*): Image array in BGR format.

---

### 3. Star Detection & Image Processing

#### `load_image(self)`
* **Description:** Opens a file dialog to import images (`.png`, `.jpg`, `.jpeg`, `.tif`, `.tiff`). Uses a raw binary buffer (`np.fromfile` + `cv2.imdecode`) to ensure full support for paths containing **spaces, special characters, and Unicode/accents**. Normalizes bit depth to 8-bit BGR.

#### `detect_stars(self)`
* **Description:** Detects candidate stars using thresholding and morphological connected component analysis.
* **Algorithm Pipeline:**
  1. Converts the source image to grayscale.
  2. Applies a threshold (`Bright Star threshold`).
  3. Executes `cv2.connectedComponentsWithStats` to extract star centroids $(cx, cy)$, bounding box, and area.
  4. Filters out artifacts smaller than `Star Min Size (px²)`.
  5. Computes star equivalent diameter (`size_px`), mean core brightness, and total flux ($Area \times \frac{Brightness}{255}$).
  6. Sorts stars by descending flux and limits results to `Max Stars`.
* **Returns:** `List[Tuple(cx, cy, size_px, brightness, flux)]`.

#### `_draw_tapered_spike(self, mask, cx, cy, angle_rad, length, base_thickness, base_intensity, chroma_amount, n_segments=24)`
* **Description:** Renders an individual spike branch with a realistic tapered profile (thickness and intensity decreasing away from the center) and chromatic dispersion.
* **Parameters:**
  * `mask` (*numpy.ndarray*): Float32 accumulator mask.
  * `cx, cy` (*float*): Star center coordinates.
  * `angle_rad` (*float*): Direction angle in radians.
  * `length` (*float*): Spike length in pixels.
  * `base_thickness` (*float*): Starting thickness at the star core.
  * `base_intensity` (*float*): Spike brightness at the star core.
  * `chroma_amount` (*int*): Level of chromatic aberration (0 to 10).
  * `n_segments` (*int*): Number of linear subdivisions for smooth anti-aliased gradient rendering.

#### `generate_preview(self)`
* **Description:** Main synthesis pipeline:
  1. Calls `detect_stars()`.
  2. Computes per-star scaling factors based on relative flux, **Auto-Scale Luminosity (%)**, and **Dynamic Range Compression** ($\gamma$).
  3. Iterates over branches (4 branches at $90^\circ$ or 6 branches at $60^\circ$) + user rotation offset.
  4. Renders branches into an accumulator mask using `_draw_tapered_spike()`.
  5. Applies a Gaussian blur (`Softening / Blur`) to simulate optical diffusion.
  6. Blends the spikes onto the original image using `cv2.addWeighted` based on `Global Opacity (%)`.
  7. Updates the canvas display.

#### `save_image(self)`
* **Description:** Exports the processed image (`.png`, `.tif`, `.jpg`) using `cv2.imencode` + `.tofile()` to prevent Unicode filepath bugs on Windows.

---

## 🎛️ Parameters Reference

| Parameter | Type | Default | Description |
|---|---|---|---|
| **Bright Star threshold** | Integer | `220` | Detection sensitivity (0-255). |
| **Max Stars** | Integer | `12` | Max stars to process (0 = unlimited). |
| **Star Min Size** | Integer | `75` | Minimum star area in pixels² to filter out noise. |
| **Auto-Scale Luminosity** | Float (%) | `12.00` | Influence of star brightness on spike size. |
| **Dynamic Range Compression** | Float | `1.00` | Non-linear power factor ($\gamma$) balancing spike size difference between bright and faint stars. |
| **Base Length** | Float (%) | `4.00` | Base spike length relative to image dimension. |
| **Star Size Factor → Length** | Float | `2.50` | Proportional length multiplier based on star radius. |
| **Base Thickness** | Float | `21.00` | Base line thickness in pixels. |
| **Rotation Angle** | Float | `0.00` | Angular rotation offset in degrees. |
| **Branch Mode** | Radio | `4` | 4 branches (Newton/RC) or 6 branches (JWST). |
| **Softening / Blur** | Integer | `5` | Gaussian blur kernel size (forced odd). |
| **Global Opacity** | Float (%) | `100.00` | Spike blend opacity on the original image. |
| **Chromatic Aberration** | Integer | `8` | Color dispersion intensity along the spikes. |
